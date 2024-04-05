import datetime
import random
import re
import typer
from operator import itemgetter
from enum import Enum
from typing import Optional
from dateutil.parser import parse
from dateutil.tz import UTC
from gidgetlab.httpx import GitLabAPI
from gidgetlab import BadRequest
from .models import GitLabId, Project
from . import api


class PipelineExecution(str, Enum):
    oldest = "oldest"
    newest = "newest"
    random = "random"


async def get_project_latest_pipeline_date(
    gl: GitLabAPI, project_id: GitLabId
) -> datetime.datetime:
    """Return the project latest pipeline execution date"""
    # pipelines are returned sorted by desc id by default
    # Highest id is the latest
    try:
        pipelines = await gl.getitem(f"/projects/{project_id}/pipelines")
    except BadRequest as e:
        if e.status_code == 403:
            # If CI/CD isn't enabled in the project General Settings,
            # 403 is returned - we don't want to crash on that
            pipelines = []
        else:
            raise
    try:
        latest_pipeline = pipelines[0]
    except IndexError:
        return datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=UTC)
    return parse(latest_pipeline["updated_at"])


async def sort_projects_by_pipeline_date(
    gl: GitLabAPI, projects: list[Project], reverse=False
) -> list[Project]:
    """Return the projects sorted by latest pipeline execution date"""
    # Build a list of tuple with each project and the latest pipeline date
    project_pipelines = [
        (project, await get_project_latest_pipeline_date(gl, project.id))
        for project in projects
    ]
    sorted_project_pipelines = sorted(
        project_pipelines, key=itemgetter(1), reverse=reverse
    )
    return [item[0] for item in sorted_project_pipelines]


async def run_trigger_group_pipelines(
    gl: GitLabAPI,
    group: GitLabId,
    nb_projects: int,
    sort: PipelineExecution = PipelineExecution.oldest,
    description: str = "gidgetlab",
    exclude: Optional[list[str]] = None,
    include: Optional[str] = None,
    delay: float = 0,
    chunk: int = 1,
) -> None:
    """Trigger the pipeline for the group projects

    When greater than 0, nb_projects allows to select a subset of the projects.
    By default, the projects selected are the ones with the oldest pipeline execution date.
    It can be set to "newest" or "random".
    Some projects can be excluded based on the path with namespace.
    You can also filter the projects based on the name using the include regex.
    """
    # Filter out empty project (default_branch is None) and excluded one
    if exclude is None:
        exclude = []
    projects = [
        project
        async for project in api.get_all_projects(gl, group)
        if project.default_branch is not None
        and project.path_with_namespace not in exclude
    ]
    if include is not None:
        pattern = re.compile(include)
        projects = [
            project for project in projects if pattern.search(project.name) is not None
        ]
    if nb_projects == 0 or nb_projects >= len(projects):
        sampled = projects
    else:
        if sort == PipelineExecution.random:
            sampled = random.sample(projects, nb_projects)
        else:
            reverse = sort == PipelineExecution.newest
            sorted_projects = await sort_projects_by_pipeline_date(
                gl, projects, reverse=reverse
            )
            sampled = sorted_projects[:nb_projects]
    typer.secho(
        f"Trigger pipeline for {' '.join([project.name for project in sampled])}",
        fg=typer.colors.GREEN,
    )
    await api.trigger_pipelines(gl, sampled, description, delay=delay, chunk=chunk)
    await gl._client.aclose()
