import datetime
import random
import pytest
from dateutil.tz import UTC
from gidgetlab_kit import pipelines
from gidgetlab_kit.pipelines import PipelineExecution
from gidgetlab_kit.models import Project
from .utils import FakeGitLab


@pytest.fixture(scope="module")
def projects():
    return [
        Project(
            id=i,
            name=f"project{i}",
            namespace="group",
            path_with_namespace=f"group/project{i}",
        )
        for i in range(10)
    ]


@pytest.fixture(scope="module")
def misc_projects():
    return [
        Project(
            id=0,
            name="dev-foo-project",
            namespace="group",
            path_with_namespace="group/dev-foo-project",
        ),
        Project(
            id=1,
            name="dev-bar-another",
            namespace="group",
            path_with_namespace="group/dev-bar-another",
        ),
        Project(
            id=2,
            name="lib-foo-bar",
            namespace="mygroup",
            path_with_namespace="mygroup/lib-foo-bar",
        ),
        Project(
            id=3,
            name="myproject",
            namespace="group",
            path_with_namespace="group/myproject",
        ),
        Project(
            id=4,
            name="bar-dev-baz",
            namespace="group",
            path_with_namespace="group/bar-dev-baz",
        ),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pipelines_response, expected",
    [
        ([], datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=UTC)),
        (
            [
                {"id": 41985, "updated_at": "2020-09-11T06:09:34.488Z"},
                {"id": 41979, "updated_at": "2020-09-11T05:21:43.487Z"},
                {"id": 41977, "updated_at": "2020-09-11T05:11:39.798Z"},
            ],
            datetime.datetime(2020, 9, 11, 6, 9, 34, 488000, tzinfo=UTC),
        ),
    ],
)
async def test_get_project_latest_pipeline_date(pipelines_response, expected):
    project_id = 459
    gl = FakeGitLab(getitem=pipelines_response)
    result = await pipelines.get_project_latest_pipeline_date(gl, project_id)
    assert gl.getitem_url == f"/projects/{project_id}/pipelines"
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pipelines_responses, expected_index",
    [
        (
            [
                [{"updated_at": "2020-09-08T06:09:34Z"}],
                [{"updated_at": "2020-09-09T06:09:34Z"}],
                [{"updated_at": "2020-09-01T09:09:34Z"}],
                [{"updated_at": "2020-09-10T06:09:34Z"}],
                [{"updated_at": "2020-09-03T06:09:34Z"}],
                [{"updated_at": "2020-09-05T06:09:34Z"}],
                [{"updated_at": "2020-09-02T06:09:34Z"}],
                [{"updated_at": "2020-09-06T06:09:34Z"}],
                [{"updated_at": "2020-09-07T06:09:34Z"}],
                [{"updated_at": "2020-09-04T06:09:34Z"}],
            ],
            [2, 6, 4, 9, 5, 7, 8, 0, 1, 3],
        ),
        (
            [
                [{"updated_at": "2020-09-08T06:09:34Z"}],
                [{"updated_at": "2020-09-01T09:09:34Z"}],
                [{"updated_at": "2020-09-10T06:09:34Z"}],
                [{"updated_at": "2020-09-03T06:09:34Z"}],
                [{"updated_at": "2020-09-05T06:09:34Z"}],
                [{"updated_at": "2020-09-02T06:09:34Z"}],
                [{"updated_at": "2020-09-06T06:09:34Z"}],
                [],
                [{"updated_at": "2020-09-07T06:09:34Z"}],
                [{"updated_at": "2020-09-04T06:09:34Z"}],
            ],
            [7, 1, 5, 3, 9, 4, 6, 8, 0, 2],
        ),
    ],
)
async def test_sort_projects_by_pipeline_date(
    pipelines_responses, expected_index, projects
):
    gl = FakeGitLab(getitems=pipelines_responses)
    result = await pipelines.sort_projects_by_pipeline_date(gl, projects)
    assert len(result) == len(expected_index)
    assert gl.getitem_calls == 10
    expected_projects = [projects[i] for i in expected_index]
    assert result == expected_projects


@pytest.mark.asyncio
@pytest.mark.parametrize("nb_projects", [0, 10, 42])
@pytest.mark.parametrize(
    "sort",
    [PipelineExecution.oldest, PipelineExecution.newest, PipelineExecution.random],
)
async def test_run_trigger_group_pipelines_all(nb_projects, sort, mocker, projects):
    # All projects shall be returned when nb_projects is 0 or greater than len(projects)
    async def projects_generator():
        for project in projects:
            yield project

    mock_trigger_pipelines = mocker.patch("gidgetlab_kit.api.trigger_pipelines")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator()
    mock_sort_projects_by_pipeline_date = mocker.patch(
        "gidgetlab_kit.pipelines.sort_projects_by_pipeline_date"
    )
    gl = FakeGitLab()
    await pipelines.run_trigger_group_pipelines(gl, "group", nb_projects, sort)
    assert not mock_sort_projects_by_pipeline_date.called
    assert mock_trigger_pipelines.called
    called_args = mock_trigger_pipelines.call_args.args
    assert called_args[0] == gl
    assert called_args[2] == "gidgetlab"
    assert called_args[1] == projects


@pytest.mark.asyncio
@pytest.mark.parametrize("nb_projects", [1, 3, 7])
async def test_run_trigger_group_pipelines_random(nb_projects, mocker, projects):
    async def projects_generator():
        for project in projects:
            yield project

    mock_trigger_pipelines = mocker.patch("gidgetlab_kit.api.trigger_pipelines")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator()
    mock_sort_projects_by_pipeline_date = mocker.patch(
        "gidgetlab_kit.pipelines.sort_projects_by_pipeline_date"
    )
    gl = FakeGitLab()
    await pipelines.run_trigger_group_pipelines(
        gl, "group", nb_projects, PipelineExecution.random
    )
    assert not mock_sort_projects_by_pipeline_date.called
    assert mock_trigger_pipelines.called
    called_args = mock_trigger_pipelines.call_args.args
    assert called_args[0] == gl
    assert called_args[2] == "gidgetlab"
    assert len(called_args[1]) == nb_projects
    # We can't convert the list to a set because Project is unhashable
    # Compare the project id instead
    assert {project.id for project in called_args[1]} <= {
        project.id for project in projects
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("nb_projects", [1, 3, 7])
@pytest.mark.parametrize("sort", [PipelineExecution.oldest, PipelineExecution.newest])
async def test_run_trigger_group_pipelines_not_random(
    nb_projects, mocker, projects, sort
):
    async def projects_generator():
        for project in projects:
            yield project

    mock_trigger_pipelines = mocker.patch("gidgetlab_kit.api.trigger_pipelines")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator()
    mock_sort_projects_by_pipeline_date = mocker.patch(
        "gidgetlab_kit.pipelines.sort_projects_by_pipeline_date"
    )
    # Shuffle the list to simulate sorting
    sorted_projects = projects[:]
    random.shuffle(sorted_projects)
    if sort == PipelineExecution.newest:
        sorted_projects.reverse()
    mock_sort_projects_by_pipeline_date.return_value = sorted_projects
    gl = FakeGitLab()
    description = "my-test"
    await pipelines.run_trigger_group_pipelines(
        gl, "group", nb_projects, sort, description
    )
    mock_sort_projects_by_pipeline_date.assert_called_once_with(
        gl, projects, reverse=sort == PipelineExecution.newest
    )
    assert mock_trigger_pipelines.called
    called_args = mock_trigger_pipelines.call_args.args
    assert called_args[0] == gl
    assert called_args[2] == description
    assert called_args[1] == sorted_projects[:nb_projects]


@pytest.mark.asyncio
@pytest.mark.parametrize("nb_projects", [5, 8])
async def test_run_trigger_group_pipelines_exclude(nb_projects, mocker, projects):
    async def projects_generator():
        for project in projects:
            yield project

    mock_trigger_pipelines = mocker.patch("gidgetlab_kit.api.trigger_pipelines")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator()
    mock_sort_projects_by_pipeline_date = mocker.patch(
        "gidgetlab_kit.pipelines.sort_projects_by_pipeline_date"
    )
    excluded_id = (1, 4, 9)
    exclude = [f"group/project{i}" for i in excluded_id]
    projects_included = [
        project for project in projects if project.id not in excluded_id
    ]
    # Shuffle the list to simulate sorting
    sorted_projects = projects_included[:]
    random.shuffle(sorted_projects)
    mock_sort_projects_by_pipeline_date.return_value = sorted_projects
    gl = FakeGitLab()
    await pipelines.run_trigger_group_pipelines(
        gl, "group", nb_projects, exclude=exclude
    )
    assert mock_trigger_pipelines.called
    called_args = mock_trigger_pipelines.call_args.args
    assert called_args[0] == gl
    assert called_args[2] == "gidgetlab"
    if nb_projects >= 7:
        # Only 7 projects can be returned as 3 are excluded
        assert not mock_sort_projects_by_pipeline_date.called
        assert called_args[1] == projects_included
    else:
        mock_sort_projects_by_pipeline_date.assert_called_once_with(
            gl, projects_included, reverse=False
        )
        assert called_args[1] == sorted_projects[:nb_projects]


@pytest.mark.asyncio
@pytest.mark.parametrize("nb_projects", [0, 1])
@pytest.mark.parametrize(
    "include, expected_id",
    [
        (None, [0, 1, 2, 3, 4]),
        ("foo", [0, 2]),
        ("^dev-", [0, 1]),
        ("^dev-|^lib-", [0, 1, 2]),
    ],
)
async def test_run_trigger_group_pipelines_include(
    nb_projects, include, expected_id, mocker, misc_projects
):
    async def projects_generator():
        for project in misc_projects:
            yield project

    mock_trigger_pipelines = mocker.patch("gidgetlab_kit.api.trigger_pipelines")
    mock_get_all_projects = mocker.patch("gidgetlab_kit.api.get_all_projects")
    mock_get_all_projects.return_value = projects_generator()
    mock_sort_projects_by_pipeline_date = mocker.patch(
        "gidgetlab_kit.pipelines.sort_projects_by_pipeline_date"
    )
    expected_projects = [
        project for project in misc_projects if project.id in expected_id
    ]
    # Shuffle the list to simulate sorting
    sorted_projects = expected_projects[:]
    random.shuffle(sorted_projects)
    mock_sort_projects_by_pipeline_date.return_value = sorted_projects
    gl = FakeGitLab()
    await pipelines.run_trigger_group_pipelines(
        gl, "group", nb_projects, include=include
    )
    assert mock_trigger_pipelines.called
    called_args = mock_trigger_pipelines.call_args.args
    assert called_args[0] == gl
    assert called_args[2] == "gidgetlab"
    if nb_projects == 0:
        assert not mock_sort_projects_by_pipeline_date.called
        assert called_args[1] == expected_projects
    else:
        mock_sort_projects_by_pipeline_date.assert_called_once_with(
            gl, expected_projects, reverse=False
        )
        assert called_args[1] == sorted_projects[:nb_projects]
