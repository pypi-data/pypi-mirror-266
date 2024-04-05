import os
import pytest
from pathlib import Path
from typer.testing import CliRunner
from gidgetlab_kit.command import app, state, PipelineExecution

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "clone" in result.output


@pytest.mark.parametrize(
    "invoke_args,called_args",
    [
        (["clone", "foo"], ["foo", Path(".").resolve(), False, False, False, 5]),
        (
            ["clone", "-n", 10, "foo"],
            ["foo", Path(".").resolve(), False, False, False, 10],
        ),
        (
            ["clone", "--archived", "my-group"],
            ["my-group", Path(".").resolve(), True, False, False, 5],
        ),
        (
            ["clone", "--delete-extra-repos", "my-group"],
            ["my-group", Path(".").resolve(), False, True, False, 5],
        ),
        (
            ["clone", "--force", "my-group"],
            ["my-group", Path(".").resolve(), False, False, True, 5],
        ),
    ],
)
def test_clone_subcommand(mocker, invoke_args, called_args):
    mock_run_clone = mocker.patch("gidgetlab_kit.command.run_clone")
    result = runner.invoke(app, invoke_args)
    assert result.exit_code == 0
    mock_run_clone.assert_called_once_with(state["gl"], *called_args)


def test_clone_subcommand_with_path(mocker, tmp_path):
    mock_run_clone = mocker.patch("gidgetlab_kit.command.run_clone")
    assert os.getcwd() != str(tmp_path)
    result = runner.invoke(app, ["clone", "-p", str(tmp_path), "group"])
    assert result.exit_code == 0
    mock_run_clone.assert_called_once_with(
        state["gl"], "group", tmp_path, False, False, False, 5
    )


@pytest.mark.parametrize(
    "invoke_args,called_args",
    [
        (["get", "/projects"], ["/projects", {}, 0]),
        (["get", "-n", "5", "/projects"], ["/projects", {}, 5]),
        (["get", "/projects", "archived=true"], ["/projects", {"archived": "true"}, 0]),
        (
            ["get", "/projects", "order_by=updated_at", "sort=asc"],
            ["/projects", {"order_by": "updated_at", "sort": "asc"}, 0],
        ),
    ],
)
def test_get_subcommand(mocker, invoke_args, called_args):
    mock_run_get = mocker.patch("gidgetlab_kit.command.run_get")
    result = runner.invoke(app, invoke_args)
    assert result.exit_code == 0
    mock_run_get.assert_called_once_with(state["gl"], *called_args)


@pytest.mark.parametrize(
    "invoke_args, exit_code", [(["get"], 2), (["get", "/projects", "foo"], 1)]
)
def test_get_subcommand_invalid_arguments(mocker, invoke_args, exit_code):
    mock_run_get = mocker.patch("gidgetlab_kit.command.run_get")
    result = runner.invoke(app, invoke_args)
    assert result.exit_code == exit_code
    assert not mock_run_get.called


@pytest.mark.parametrize(
    "invoke_args,called_args,called_kwargs",
    [
        (
            ["trigger-pipelines", "group"],
            ["group", 0],
            {
                "sort": PipelineExecution.oldest,
                "description": "gidgetlab",
                "exclude": None,
                "include": None,
                "delay": 0,
                "chunk": 1,
            },
        ),
        (
            ["trigger-pipelines", "group", "-n", "5"],
            ["group", 5],
            {
                "sort": PipelineExecution.oldest,
                "description": "gidgetlab",
                "exclude": None,
                "include": None,
                "delay": 0,
                "chunk": 1,
            },
        ),
        (
            [
                "trigger-pipelines",
                "group",
                "--exclude",
                "mygroup/myproject",
                "--exclude",
                "mygroup/project2",
            ],
            ["group", 0],
            {
                "sort": PipelineExecution.oldest,
                "description": "gidgetlab",
                "exclude": ["mygroup/myproject", "mygroup/project2"],
                "include": None,
                "delay": 0,
                "chunk": 1,
            },
        ),
        (
            ["trigger-pipelines", "group", "--sort", "random"],
            ["group", 0],
            {
                "sort": PipelineExecution.random,
                "description": "gidgetlab",
                "exclude": None,
                "include": None,
                "delay": 0,
                "chunk": 1,
            },
        ),
        (
            ["trigger-pipelines", "group", "--delay", "3", "--chunk", "5"],
            ["group", 0],
            {
                "sort": PipelineExecution.oldest,
                "description": "gidgetlab",
                "exclude": None,
                "include": None,
                "delay": 3.0,
                "chunk": 5,
            },
        ),
        (
            ["trigger-pipelines", "group", "--description", "my-test"],
            ["group", 0],
            {
                "sort": PipelineExecution.oldest,
                "description": "my-test",
                "exclude": None,
                "include": None,
                "delay": 0,
                "chunk": 1,
            },
        ),
        (
            [
                "trigger-pipelines",
                "group",
                "--include",
                "^dev-|^lib-",
            ],
            ["group", 0],
            {
                "sort": PipelineExecution.oldest,
                "description": "gidgetlab",
                "exclude": None,
                "include": "^dev-|^lib-",
                "delay": 0,
                "chunk": 1,
            },
        ),
    ],
)
def test_trigger_pipelines_subcommand(mocker, invoke_args, called_args, called_kwargs):
    mock_run_trigger_pipelines = mocker.patch(
        "gidgetlab_kit.command.run_trigger_group_pipelines"
    )
    result = runner.invoke(app, invoke_args)
    assert result.exit_code == 0
    mock_run_trigger_pipelines.assert_called_once_with(
        state["gl"], *called_args, **called_kwargs
    )


@pytest.mark.parametrize(
    "invoke_args,called_args",
    [
        (
            ["commit-file", "--group", "mygroup", "afile"],
            ["mygroup", Path("afile"), "afile", "master", "", 5],
        ),
        (
            ["commit-file", "--group", "mygroup", "-b", "dev", "afile"],
            ["mygroup", Path("afile"), "afile", "dev", "", 5],
        ),
        (
            ["commit-file", "--group", "mygroup", "-m", "Update foo", "foo"],
            ["mygroup", Path("foo"), "foo", "master", "Update foo", 5],
        ),
        (
            ["commit-file", "--group", "mygroup", "-p", "tests", "/tmp/test_foo.py"],
            ["mygroup", Path("/tmp/test_foo.py"), "tests/test_foo.py", "master", "", 5],
        ),
    ],
)
def test_commit_file_subcommand(mocker, invoke_args, called_args):
    mock_run_commit_file = mocker.patch("gidgetlab_kit.command.run_commit_file")
    result = runner.invoke(app, invoke_args)
    assert result.exit_code == 0
    mock_run_commit_file.assert_called_once_with(state["gl"], *called_args)


@pytest.mark.parametrize(
    "invoke_args,called_args",
    [
        (
            ["list-projects", "mygroup"],
            ["mygroup", False],
        ),
        (
            ["list-projects", "--archived", "mygroup"],
            ["mygroup", True],
        ),
        (
            ["list-projects", "53"],
            ["53", False],
        ),
        (
            ["list-projects", "my-group/acc"],
            ["my-group/acc", False],
        ),
    ],
)
def test_list_projects_subcommand(mocker, invoke_args, called_args):
    mock_run_list_projects = mocker.patch("gidgetlab_kit.command.run_list_projects")
    result = runner.invoke(app, invoke_args)
    assert result.exit_code == 0
    mock_run_list_projects.assert_called_once_with(state["gl"], *called_args)
