import asyncio
import logging
import typer
import httpx
from importlib.metadata import version, PackageNotFoundError  # type: ignore
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from gidgetlab.httpx import GitLabAPI
from . import util, api
from .models import GitLabId
from .clone import run_clone
from .get import run_get
from .pipelines import run_trigger_group_pipelines, PipelineExecution
from .commits import run_commit_file

try:
    __version__ = version("gidgetlab-kit")
except PackageNotFoundError:
    __version__ = "unknown"

app = typer.Typer()
state = {}


def version_callback(value: bool):
    if value:
        typer.echo(f"gidgetlab-kit version: {__version__}")
        raise typer.Exit()


async def run_list_projects(gl: GitLabAPI, group_id: GitLabId, archived: bool) -> None:
    typer.echo(f"Projects under group {group_id}:")
    async for project in api.get_all_projects(gl, group_id, archived):
        typer.secho(
            f"{project.path_with_namespace} (id: {project.id} name: {project.name})",
            fg=typer.colors.GREEN,
        )
    await gl._client.aclose()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the current version and exit.",
        ),
    ] = None,
    url: Annotated[
        str, typer.Option(envvar="GL_URL", help="GitLab URL")
    ] = "https://gitlab.com",
    access_token: Annotated[
        str, typer.Option(envvar="GL_ACCESS_TOKEN", help="GitLab access token")
    ] = "",
    verify: Annotated[
        bool, typer.Option(help="Verify SSL cerificate or disable verification")
    ] = True,
):
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    client = httpx.AsyncClient(verify=verify)
    state["gl"] = GitLabAPI(client, "gidgetlab", url=url, access_token=access_token)


@app.command()
def clone(
    group: Annotated[str, typer.Argument(..., help="Name of the group to clone")],
    path: Annotated[
        Path,
        typer.Option(
            "--path",
            "-p",
            exists=True,
            resolve_path=True,
            help="Path where to clone the group",
        ),
    ] = Path("."),
    archived: Annotated[bool, typer.Option(help="Clone archived projects")] = False,
    delete_extra_repos: Annotated[
        bool, typer.Option(help="Delete extra local repositories")
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            help="Force repository update when it exists (git reset --hard origin/default_branch instead of rebase)",
        ),
    ] = False,
    nb_consumers: Annotated[
        int,
        typer.Option(
            "--nb-consumers",
            "-n",
            help="Number of consumers to start to clone in parallel",
        ),
    ] = 5,
):
    """Clone or pull all projects from group (including subgroups)

    Projects are cloned/updated in parallel
    """
    asyncio.run(
        run_clone(
            state["gl"], group, path, archived, delete_extra_repos, force, nb_consumers
        )
    )


@app.command()
def get(
    endpoint: Annotated[str, typer.Argument(help="Endpoint to get")],
    parameters: Annotated[
        Optional[list[str]],
        typer.Argument(help="Optional key-value pairs to pass as json parameters"),
    ] = None,
    nb_items: Annotated[
        int,
        typer.Option(
            "--nb-items",
            "-n",
            help="Number of items to retrieve. Only valid when a list is returned. Set to 0 to return all.",
        ),
    ] = 0,
):
    """Get one or several items from the given endpoint"""
    if parameters is None:
        parameters = []
    try:
        params = util.convert_params_to_dict(parameters)
    except ValueError:
        typer.echo(
            f"Invalid parameters: '{' '.join(parameters)}' should be a list of key-value pairs separated by '='."
        )
        raise typer.Exit(code=1) from None
    asyncio.run(run_get(state["gl"], endpoint, params, nb_items))


@app.command()
def list_projects(
    group: Annotated[str, typer.Argument(help="Name of the group")],
    archived: Annotated[bool, typer.Option(help="list archived projects")] = False,
):
    """list all projects from group (including subgroups)"""
    asyncio.run(run_list_projects(state["gl"], group, archived))


@app.command()
def trigger_pipelines(
    group: Annotated[str, typer.Argument(help="Name of the group")],
    nb_projects: Annotated[
        int,
        typer.Option(
            "--nb-projects",
            "-n",
            help="Number of projects to trigger. Set to 0 to trigger all projects from the group.",
        ),
    ] = 0,
    sort: Annotated[
        PipelineExecution,
        typer.Option(
            help="How to sort the projects based on the latest pipeline execution date.",
        ),
    ] = PipelineExecution.oldest,
    exclude: Annotated[
        Optional[list[str]],
        typer.Option(
            help=(
                "Project to exclude (path with basename). "
                "This is to exclude very specific project(s). To use regex, use include instead."
            ),
        ),
    ] = None,
    include: Annotated[
        Optional[str],
        typer.Option(
            help="regex that should match the name of projects to include (using re.search).",
        ),
    ] = None,
    description: Annotated[
        str,
        typer.Option(
            help="Pipeline trigger description",
        ),
    ] = "gidgetlab",
    delay: Annotated[
        float,
        typer.Option(
            help="Delay to apply between pipeline triggering. No delay if set to 0.",
        ),
    ] = 0,
    chunk: Annotated[
        int,
        typer.Option(
            min=1,
            help="Number of projects to trigger without delay (list will be processed chunk by chunk if greater than 1).",
        ),
    ] = 1,
):
    """Trigger the pipeline for all or a subset of projects from group"""
    asyncio.run(
        run_trigger_group_pipelines(
            state["gl"],
            group,
            nb_projects,
            sort=sort,
            description=description,
            exclude=exclude,
            include=include,
            delay=delay,
            chunk=chunk,
        )
    )


@app.command()
def commit_file(
    filepath: Annotated[Path, typer.Argument(help="Local file to add or update")],
    group: Annotated[str, typer.Option(help="Name of the group")],
    repo_path: Annotated[
        Path,
        typer.Option(
            "--repo-path",
            "-p",
            resolve_path=False,
            help="Path of the file in the repository",
        ),
    ] = Path("."),
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            show_default=False,
            help="Commit message [default: Add/Update <filename>]",
        ),
    ] = "",
    branch: Annotated[
        str, typer.Option("--branch", "-b", help="Branch to commit to")
    ] = "master",
    nb_consumers: Annotated[
        int,
        typer.Option(
            "--nb-consumers",
            "-n",
            help="Number of consumers to start to update in parallel",
        ),
    ] = 5,
):
    """Add or update a file to a list of projects

    Example:

      The following will add the local .gitlab-ci.yml file to all projects under the my-group group

      $ gidgetlab commit-file --group my-group .gitlab-ci.yml
    """
    repo_file_path = str(repo_path / filepath.name)
    asyncio.run(
        run_commit_file(
            state["gl"],
            group,
            filepath,
            repo_file_path,
            branch,
            message,
            nb_consumers,
        )
    )
