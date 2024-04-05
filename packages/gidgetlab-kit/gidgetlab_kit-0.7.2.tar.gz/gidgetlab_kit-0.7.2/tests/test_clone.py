import pytest
from gidgetlab_kit import clone
from gidgetlab_kit.models import Project

PROJECT1 = Project(
    name="project1", namespace="my-group", path_with_namespace="my-group/project1"
)
PROJECT2 = Project(
    name="project2", namespace="my-group", path_with_namespace="my-group/project2"
)
PROJECT3 = Project(name="foo", namespace="my-group", path_with_namespace="my-group/foo")


@pytest.mark.parametrize(
    "projects, extra_repos, expected",
    [
        ([], ["my-group/new"], []),
        ([PROJECT1, PROJECT2, PROJECT3], [], []),
        ([PROJECT1, PROJECT2], ["my-group/foo"], ["my-group/foo"]),
        (
            [PROJECT1, PROJECT2, PROJECT3],
            ["my-group/project10", "my-group/subgroup/bar"],
            ["my-group/project10", "my-group/subgroup/bar"],
        ),
        ([PROJECT1, PROJECT2, PROJECT3], ["another-group/new"], []),
    ],
)
def test_delete_extra_repositories(projects, extra_repos, expected, tmp_path):
    # Create the git repositories
    for project in projects:
        (tmp_path / project.path_with_namespace / ".git").mkdir(parents=True)
    for extra_repo in extra_repos:
        (tmp_path / extra_repo / ".git").mkdir(parents=True)
    # Check that the repositories expected to be deleted exist
    for repo in expected:
        assert (tmp_path / repo).exists()
    # Call the function
    result = clone.delete_extra_repositories(projects, tmp_path)
    # Check that projects still exist but not the expected one to be deleted
    for project in projects:
        assert (tmp_path / project.path_with_namespace / ".git").exists()
    for repo in expected:
        assert not (tmp_path / repo).exists()
    assert result == sorted([tmp_path / repo for repo in expected])
