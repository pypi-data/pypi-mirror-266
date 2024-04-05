import base64
import http
from gidgetlab.exceptions import HTTPException
import pytest
from gidgetlab_kit.models import Group, Project, Tag, TreeObject
from gidgetlab_kit import api
from .utils import FakeGitLab

subgroup1 = {
    "id": 409,
    "web_url": "https://gitlab.com/groups/test-group/subgroup-1",
    "name": "subgroup-1",
    "path": "subgroup-1",
    "full_name": "test-group / subgroup-1",
    "full_path": "test-group/subgroup-1",
    "parent_id": 129,
}
subgroup1_1 = {
    "id": 411,
    "web_url": "https://gitlab.com/groups/test-group/subgroup-1/new-group",
    "name": "new-group",
    "path": "new-group",
    "full_name": "test-group / subgroup-1 / new-group",
    "full_path": "test-group/subgroup-1/new-group",
    "parent_id": 409,
}
subgroup2 = {
    "id": 410,
    "web_url": "https://gitlab.com/groups/test-group/subgroup-2",
    "name": "subgroup-2",
    "path": "subgroup-2",
    "description": "",
    "full_name": "test-group / subgroup-2",
    "full_path": "test-group/subgroup-2",
    "parent_id": 129,
}
SUBGROUPS = [
    Group(**subgroup1),
    Group(**subgroup1_1),
    Group(**subgroup2),
]


def test_url_encode():
    assert api.url_encode("recipe/meta.yaml") == "recipe%2Fmeta%2Eyaml"


@pytest.mark.parametrize(
    "gitlab_id, result",
    [
        ("foo", "foo"),
        ("my-group", "my-group"),
        ("group/subgroup", "group%2Fsubgroup"),
        (42, "42"),
    ],
)
def test_encode_gitlab_id(gitlab_id, result):
    assert api.encode_gitlab_id(gitlab_id) == result


@pytest.mark.asyncio
async def test_get_file_from_repository():
    content = base64.b64encode(b"Hello World")
    project_id = 1042
    file_path = "foo/meta.yaml"
    ref = "master"
    gl = FakeGitLab(
        getitem={
            "file_name": "meta.yaml",
            "file_path": "recipe/meta.yaml",
            "size": 778,
            "encoding": "base64",
            "content_sha256": "c25f7481e275b847b3fc9d0aeb1e6445fc8af109f35f53cd7bae2e5f91ca5de0",
            "ref": ref,
            "blob_id": "20ce5c84c4c6d0cf5c5ac6b8f5119c19beb730d1",
            "commit_id": "256ea9fe558852fdc13c915659fadbb2713a9048",
            "last_commit_id": "256ea9fe558852fdc13c915659fadbb2713a9048",
            "content": content,
        }
    )
    result = await api.get_file_from_repository(gl, project_id, file_path, ref)
    assert (
        gl.getitem_url
        == f"/projects/{project_id}/repository/files/foo%2Fmeta%2Eyaml?ref={ref}"
    )
    assert result == "Hello World"


@pytest.mark.asyncio
async def test_wait_for_merge_or_failure_max_loop():
    project_id = 1409
    mr_iid = 7
    mr = {
        "id": 2158,
        "iid": mr_iid,
        "project_id": project_id,
        "title": "Test MR",
        "state": "opened",
        "pipeline": None,
        "head_pipeline": {"id": 18193, "status": "running"},
    }
    gl = FakeGitLab(getitems=[mr for _ in range(200)])
    result = await api.wait_for_merge_or_failure(gl, project_id, mr_iid)
    assert gl.getitem_url == [
        f"/projects/{project_id}/merge_requests/{mr_iid}" for _ in range(200)
    ]
    assert gl.getitem_calls == 200
    assert result is False


@pytest.mark.asyncio
async def test_wait_for_merge_or_failure_merged():
    project_id = 1409
    mr_iid = 7
    gl = FakeGitLab(
        getitem={
            "id": 2158,
            "iid": mr_iid,
            "project_id": project_id,
            "title": "Test MR",
            "state": "merged",
            "pipeline": None,
            "head_pipeline": {"id": 18193, "status": "running"},
        }
    )
    result = await api.wait_for_merge_or_failure(gl, project_id, mr_iid)
    assert gl.getitem_url == f"/projects/{project_id}/merge_requests/{mr_iid}"
    assert gl.getitem_calls == 1
    assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize("pipeline_status", ("failed", "canceled"))
async def test_wait_for_merge_or_failure_pipeline_failed_or_canceled(pipeline_status):
    project_id = 1409
    mr_iid = 7
    gl = FakeGitLab(
        getitem={
            "id": 2158,
            "iid": mr_iid,
            "project_id": project_id,
            "title": "Test MR",
            "state": "opened",
            "pipeline": None,
            "head_pipeline": {"id": 18193, "status": pipeline_status},
        }
    )
    result = await api.wait_for_merge_or_failure(gl, project_id, mr_iid)
    assert gl.getitem_url == f"/projects/{project_id}/merge_requests/{mr_iid}"
    assert gl.getitem_calls == 1
    assert result is False


@pytest.mark.asyncio
@pytest.mark.parametrize("pipeline_status", ("success", "unknown"))
async def test_wait_for_merge_or_failure_pipeline_other(pipeline_status):
    project_id = 1409
    mr_iid = 7
    mr = {
        "id": 2158,
        "iid": mr_iid,
        "project_id": project_id,
        "title": "Test MR",
        "state": "opened",
        "pipeline": None,
        "head_pipeline": {"id": 18193, "status": pipeline_status},
    }
    gl = FakeGitLab(getitems=[mr for _ in range(200)])
    result = await api.wait_for_merge_or_failure(gl, project_id, mr_iid)
    assert gl.getitem_url == [
        f"/projects/{project_id}/merge_requests/{mr_iid}" for _ in range(200)
    ]
    assert gl.getitem_calls == 200
    assert result is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "group_id, encoded_group_id", [(129, "129"), ("group/subgroup", "group%2Fsubgroup")]
)
async def test_get_subgroups(group_id, encoded_group_id):
    gl = FakeGitLab(getiter=[[subgroup1, subgroup2], [subgroup1_1], [], []])
    subgroups = [subgroup async for subgroup in api.get_subgroups(gl, group_id)]
    assert gl.getiter_url == [
        f"/groups/{encoded_group_id}/subgroups",
        f"/groups/{subgroup1['id']}/subgroups",
        f"/groups/{subgroup1_1['id']}/subgroups",
        f"/groups/{subgroup2['id']}/subgroups",
    ]
    assert subgroups == SUBGROUPS


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "group_id, encoded_group_id", [(129, "129"), ("group/subgroup", "group%2Fsubgroup")]
)
async def test_get_all_projects(mocker, group_id, encoded_group_id):
    project1 = {
        "id": 553,
        "name": "my-project",
        "web_url": "https://gitlab.com/test-group/my-project",
        "namespace": {"id": 129, "name": "test-group"},
        "path_with_namespace": "test-group/my-project",
    }
    project2 = {
        "id": 2701,
        "name": "my-cool-project",
        "web_url": "https://gitlab.com/test-group/subgroup-1/my-cool-project",
        "namespace": "subgroup-1",
        "path_with_namespace": "test-group/subgroup-1/my-cool-project",
    }
    project3 = {
        "id": 2708,
        "name": "test-project",
        "web_url": "https://gitlab.com/test-group/subgroup-1/new-group/test-project",
        "namespace": {"name": "new-group"},
        "path_with_namespace": "test-group/subgroup-1/new-group/test-project",
    }
    project4 = {
        "id": 2702,
        "name": "cool-idea",
        "web_url": "https://gitlab.com/test-group/subgroup-2/cool-idea",
        "namespace": {"id": 410, "name": "subgroup-2"},
        "path_with_namespace": "test-group/subgroup-2/cool-idea",
    }

    async def subgroups_generator():
        for subgroup in SUBGROUPS:
            yield subgroup

    mock_get_subgroups = mocker.patch("gidgetlab_kit.api.get_subgroups")
    mock_get_subgroups.return_value = subgroups_generator()
    gl = FakeGitLab(getiter=[[project1], [project2], [project3], [project4]])
    projects = [project async for project in api.get_all_projects(gl, group_id)]
    assert gl.getiter_url == [
        f"/groups/{encoded_group_id}/projects",
        f"/groups/{subgroup1['id']}/projects",
        f"/groups/{subgroup1_1['id']}/projects",
        f"/groups/{subgroup2['id']}/projects",
    ]
    assert gl.params == {"archived": False}
    assert projects == [
        api.Project(**project1),
        api.Project(**project2),
        api.Project(**project3),
        api.Project(**project4),
    ]


async def projects_generator(all_projects):
    for project in all_projects:
        yield project


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_value",
    [
        [],
        [
            Project(name="project1", namespace="group1"),
            Project(name="project2", namespace="group2"),
        ],
    ],
)
async def test_find_projects_none_found(mocker, return_value):
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator(return_value)
    project = await api.find_projects(None, "foo", "group")
    assert project == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name",
    ["My-project", "my-project", "My-Project", "MY-PROJECT"],
)
async def test_find_projects_case_insensitive(mocker, name):
    project1 = Project(name="My-project", namespace="foo")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator(
        [
            Project(name="hello", namespace="world"),
            project1,
        ]
    )
    projects = await api.find_projects(None, [name], "group")
    assert projects == [project1]


@pytest.mark.asyncio
async def test_find_projects(mocker):
    project1 = Project(name="My-project", namespace="foo")
    project2 = Project(name="another-project", namespace="foo")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator(
        [
            Project(name="hello", namespace="world"),
            project1,
            Project(name="foo", namespace="world"),
            project2,
        ]
    )
    projects = await api.find_projects(None, ["another-project", "my-project"], "group")
    assert projects == [project1, project2]


@pytest.mark.asyncio
async def test_create_project_trigger():
    project_id = 1042
    description = "my trigger"
    token = "fsjfjfegoe"
    gl = FakeGitLab(post={"id": 1, "description": description, "token": token})
    result = await api.create_project_trigger(gl, project_id, description)
    assert gl.post_url[0] == f"/projects/{project_id}/triggers"
    assert gl.post_data[0] == {"description": description}
    assert result == token


@pytest.mark.asyncio
async def test_get_or_create_project_trigger_token_existing_token():
    project_id = 1042
    description = "my trigger"
    token = "fsjfjfegoe"
    gl = FakeGitLab(
        getiter=[
            {"id": 1, "description": "another trigger", "token": "xxxxxx"},
            {"id": 2, "description": description, "token": token},
        ]
    )
    result = await api.get_or_create_project_trigger_token(gl, project_id, description)
    assert gl.getiter_url == [f"/projects/{project_id}/triggers"]
    assert gl.post_url == []
    assert result == token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "getiter", ([], [{"id": 1, "description": "another trigger", "token": "xxxxxx"}])
)
async def test_get_or_create_project_trigger_token_create(getiter):
    project_id = 1042
    description = "my trigger"
    token = "fsjfjfegoe"
    gl = FakeGitLab(
        getiter=getiter,
        post={"id": project_id, "description": description, "token": token},
    )
    result = await api.get_or_create_project_trigger_token(gl, project_id, description)
    assert gl.getiter_url == [f"/projects/{project_id}/triggers"]
    assert gl.post_url[0] == f"/projects/{project_id}/triggers"
    assert gl.post_data[0] == {"description": description}
    assert result == token


@pytest.mark.asyncio
async def test_list_branches():
    project_id = 1042
    branches = [{"name": "master"}, {"name": "dev"}]
    gl = FakeGitLab(getiter=branches)
    result = await api.list_branches(gl, project_id)
    assert gl.getiter_calls == 1
    assert gl.getiter_url[0] == f"/projects/{project_id}/repository/branches"
    assert result == ["master", "dev"]


@pytest.mark.asyncio
async def test_list_tags():
    project_id = 1042
    tags = [
        {"name": "1.0.0", "target": "c4863f5d"},
        {"name": "0.5.0", "target": "58e9991d"},
    ]
    gl = FakeGitLab(getiter=tags)
    result = await api.list_tags(gl, project_id)
    assert gl.getiter_calls == 1
    assert gl.getiter_url[0] == f"/projects/{project_id}/repository/tags"
    assert gl.params == {"order_by": "updated", "sort": "desc"}
    assert result == [
        Tag(name="1.0.0", target="c4863f5d"),
        Tag(name="0.5.0", target="58e9991d"),
    ]


@pytest.mark.asyncio
async def test_get_latest_tag_on_branch():
    project_id = 123
    branch = "master"
    tags = [
        {"name": "1.0.0-dev", "target": "sha3"},
        {"name": "1.0.0", "target": "sha2"},
        {"name": "0.5.0", "target": "sha1"},
    ]
    refs1 = [{"type": "branch", "name": "dev"}]
    refs2 = [{"type": "branch", "name": "dev"}, {"type": "branch", "name": "master"}]
    gl = FakeGitLab(getiter=[tags, refs1, refs2])
    result = await api.get_latest_tag_on_branch(gl, project_id, branch)
    assert gl.getiter_calls == 3
    assert gl.getiter_url[0] == f"/projects/{project_id}/repository/tags"
    assert gl.getiter_url[1] == f"/projects/{project_id}/repository/commits/sha3/refs"
    assert gl.getiter_url[2] == f"/projects/{project_id}/repository/commits/sha2/refs"
    assert result == Tag(name="1.0.0", target="sha2")


@pytest.mark.asyncio
async def test_get_latest_tag_on_branch_no_tag():
    project_id = 123
    branch = "master"
    tags = []
    gl = FakeGitLab(getiter=tags)
    result = await api.get_latest_tag_on_branch(gl, project_id, branch)
    assert gl.getiter_calls == 1
    assert gl.getiter_url[0] == f"/projects/{project_id}/repository/tags"
    assert result is None


@pytest.mark.asyncio
async def test_get_latest_tag_on_branch_no_tag_on_master():
    project_id = 123
    branch = "master"
    tags = [
        {"name": "1.0.0-dev", "target": "sha3"},
    ]
    refs1 = [{"type": "branch", "name": "dev"}]
    gl = FakeGitLab(getiter=[tags, refs1])
    result = await api.get_latest_tag_on_branch(gl, project_id, branch)
    assert gl.getiter_calls == 2
    assert gl.getiter_url[0] == f"/projects/{project_id}/repository/tags"
    assert gl.getiter_url[1] == f"/projects/{project_id}/repository/commits/sha3/refs"
    assert result is None


@pytest.mark.asyncio
async def test_trigger_pipeline():
    project_id = 1042
    git_ref = "master"
    token = "secret"
    gl = FakeGitLab(post={})
    result = await api.trigger_pipeline(gl, project_id, git_ref, token)
    assert gl.post_url[0] == f"/projects/{project_id}/trigger/pipeline"
    assert gl.post_params[0] == {"token": token, "ref": git_ref}
    assert result is None


@pytest.mark.asyncio
async def test_trigger_pipelines():
    project1 = Project(id=1, name="project1", namespace="group", default_branch="main")
    project2 = Project(
        id=2, name="project2", namespace="group", default_branch="master"
    )
    description = "some text"
    gl = FakeGitLab(
        getiter=[
            ({"id": 1, "description": description, "token": "token1"},),
            ({"id": 2, "description": description, "token": "token2"},),
        ],
        post={},
    )
    result = await api.trigger_pipelines(gl, [project1, project2], description)
    assert gl.post_url[0] == f"/projects/{project1.id}/trigger/pipeline"
    assert gl.post_params[0] == {"token": "token1", "ref": project1.default_branch}
    assert gl.post_url[1] == f"/projects/{project2.id}/trigger/pipeline"
    assert gl.post_params[1] == {"token": "token2", "ref": project2.default_branch}
    assert result is None


@pytest.mark.asyncio
async def test_unsubscribe_from_merge_request():
    project_id = 1042
    mr_iid = 3
    gl = FakeGitLab(post={})
    result = await api.unsubscribe_from_merge_request(gl, project_id, mr_iid)
    assert len(gl.post_url) == 1
    assert (
        gl.post_url[0] == f"/projects/{project_id}/merge_requests/{mr_iid}/unsubscribe"
    )
    assert gl.post_data[0] == {}
    assert gl.post_params[0] == {}
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_path, branch, start_branch, commit_message, encoded_file_path, expected_message",
    [
        ("foo", "master", "master", "Fix bug", "foo", "Fix bug"),
        (
            ".gitlab-ci.yml",
            "master",
            "master",
            "",
            "%2Egitlab-ci%2Eyml",
            "Update .gitlab-ci.yml",
        ),
        (
            "tests/test_foo.py",
            "dev",
            "master",
            "Update test",
            "tests%2Ftest_foo%2Epy",
            "Update test",
        ),
    ],
)
async def test_update_file_in_repository(
    file_path, branch, start_branch, commit_message, encoded_file_path, expected_message
):
    project_id = 123
    content = "Some file content"
    expected_result = {"message": "OK"}
    gl = FakeGitLab(put=expected_result)
    result = await api.update_file_in_repository(
        gl, project_id, file_path, branch, start_branch, content, commit_message
    )
    assert len(gl.put_url) == 1
    assert (
        gl.put_url[0] == f"/projects/{project_id}/repository/files/{encoded_file_path}"
    )
    assert gl.put_data[0] == {
        "branch": branch,
        "start_branch": start_branch,
        "content": content,
        "commit_message": expected_message,
    }
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_path, branch, start_branch, commit_message, encoded_file_path, expected_message",
    [
        ("foo", "master", "master", "Fix bug", "foo", "Fix bug"),
        (
            ".gitlab-ci.yml",
            "master",
            "master",
            "",
            "%2Egitlab-ci%2Eyml",
            "Add .gitlab-ci.yml",
        ),
        (
            "tests/test_foo.py",
            "dev",
            "master",
            "",
            "tests%2Ftest_foo%2Epy",
            "Add tests/test_foo.py",
        ),
    ],
)
async def test_create_file_in_repository(
    file_path, branch, start_branch, commit_message, encoded_file_path, expected_message
):
    project_id = 123
    content = "Some file content"
    expected_result = {"message": "OK"}
    gl = FakeGitLab(post=expected_result)
    result = await api.create_file_in_repository(
        gl, project_id, file_path, branch, start_branch, content, commit_message
    )
    assert len(gl.post_url) == 1
    assert (
        gl.post_url[0] == f"/projects/{project_id}/repository/files/{encoded_file_path}"
    )
    assert gl.post_data[0] == {
        "branch": branch,
        "start_branch": start_branch,
        "content": content,
        "commit_message": expected_message,
    }
    assert result == expected_result


@pytest.mark.asyncio
async def test_commit_file_in_repository_create(
    mocker,
):
    project_id = 123
    content = "Some file content"
    file_path = "some/path"
    branch = "dev"
    start_branch = "master"
    commit_message = "Fix"
    expected_result = "OK"
    mock_get_file = mocker.patch(
        "gidgetlab_kit.api.get_file_from_repository",
        side_effect=HTTPException(status_code=http.HTTPStatus.NOT_FOUND),
    )
    mock_create_file = mocker.patch(
        "gidgetlab_kit.api.create_file_in_repository", return_value=expected_result
    )
    mock_update_file = mocker.patch("gidgetlab_kit.api.update_file_in_repository")
    gl = FakeGitLab()
    result = await api.commit_file_in_repository(
        gl, project_id, file_path, branch, start_branch, content, commit_message
    )
    mock_get_file.assert_awaited_with(gl, project_id, file_path, ref=start_branch)
    mock_create_file.assert_awaited_with(
        gl, project_id, file_path, branch, start_branch, content, commit_message
    )
    assert result == expected_result
    mock_update_file.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content, existing_content",
    [("some content", "another content"), ("Hello World", "Hello World")],
)
async def test_commit_file_in_repository_update(mocker, content, existing_content):
    project_id = 123
    file_path = "some/path"
    branch = "dev"
    start_branch = "master"
    commit_message = "Fix"
    expected_result = "OK"
    mock_get_file = mocker.patch(
        "gidgetlab_kit.api.get_file_from_repository", return_value=existing_content
    )
    mock_create_file = mocker.patch("gidgetlab_kit.api.create_file_in_repository")
    mock_update_file = mocker.patch(
        "gidgetlab_kit.api.update_file_in_repository", return_value=expected_result
    )
    gl = FakeGitLab()
    result = await api.commit_file_in_repository(
        gl, project_id, file_path, branch, start_branch, content, commit_message
    )
    mock_get_file.assert_awaited_with(gl, project_id, file_path, ref=start_branch)
    mock_create_file.assert_not_awaited()
    if content == existing_content:
        mock_update_file.assert_not_awaited()
        assert result is None
    else:
        mock_update_file.assert_awaited_with(
            gl, project_id, file_path, branch, start_branch, content, commit_message
        )
        assert result == expected_result


@pytest.mark.asyncio
async def test_list_repository_tree():
    project_id = 1042
    tree = [
        {
            "id": "e29caa07a053b72a89ad051aebc484c53d211674",
            "name": "tests",
            "type": "tree",
            "path": "tests",
            "mode": "040000",
        },
        {
            "id": "57cb82c8305cf0e212b5831deabfb8dcb28831c9",
            "name": ".gitignore",
            "type": "blob",
            "path": ".gitignore",
            "mode": "100644",
        },
        {
            "id": "36f908eafcfae64a8031a5e12eb1e155a6d2d1b3",
            "name": ".gitlab-ci.yml",
            "type": "blob",
            "path": ".gitlab-ci.yml",
            "mode": "100644",
        },
    ]
    gl = FakeGitLab(getiter=tree)
    result = await api.list_repository_tree(gl, project_id, ref="main")
    assert gl.getiter_calls == 1
    assert gl.getiter_url[0] == f"/projects/{project_id}/repository/tree"
    assert gl.params == {"ref": "main", "recursive": True}
    assert result == [TreeObject(**el) for el in tree]
