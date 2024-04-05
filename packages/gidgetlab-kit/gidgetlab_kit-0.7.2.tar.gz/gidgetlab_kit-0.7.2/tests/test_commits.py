import http
import pytest
import asyncio
from gidgetlab.exceptions import HTTPException
from gidgetlab_kit.models import Project
from gidgetlab_kit import commits
from .utils import FakeGitLab


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "side_effect",
    [None, HTTPException(status_code=http.HTTPStatus.FORBIDDEN), IndexError],
)
async def test_update_projects(mocker, side_effect):
    # Ensure the update_projects task is properly done even
    # in case of exception raised by api.commit_file_in_repository
    mock_commit_file = mocker.patch(
        "gidgetlab_kit.api.commit_file_in_repository", side_effect=side_effect
    )
    queue = asyncio.Queue()
    project = Project(
        name="myproject", id=42, namespace="foo", path_with_namespace="foo/myproject"
    )
    gl = FakeGitLab()
    file_path = "myfile"
    branch = "master"
    content = "Hello World"
    commit_message = "test commit"
    task = asyncio.create_task(
        commits.update_projects(queue, gl, file_path, branch, content, commit_message)
    )
    await queue.put(project)
    await queue.join()
    task.cancel()
    mock_commit_file.assert_awaited_with(
        gl,
        project.id,
        file_path,
        branch=branch,
        start_branch=branch,
        content=content,
        commit_message=commit_message,
    )
    assert queue.empty()
