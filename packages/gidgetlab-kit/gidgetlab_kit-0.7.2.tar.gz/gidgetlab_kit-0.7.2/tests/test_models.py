import pytest
from gidgetlab_kit.models import Project, Group, Tag
from .utils import sample


@pytest.mark.parametrize(
    "filename, expected_name, expected_ssh_url",
    [
        (
            "project_from_pipeline_event.json",
            "foo-recipe",
            "git@gitlab.com:my-group/foo-recipe.git",
        ),
        (
            "project_from_tag_push_event.json",
            "my-project",
            "git@gitlab.com:test-group/my-project.git",
        ),
        (
            "projects_id_auth.json",
            "xtpico-recipe",
            "git@gitlab.com:my-group/xtpico-recipe.git",
        ),
        (
            "projects_id_no_auth.json",
            "xtpico-recipe",
            "git@gitlab.com:my-group/xtpico-recipe.git",
        ),
        (
            "projects_id_subgroup.json",
            "test-project",
            "git@gitlab.com:test-group/subgroup-1/new-group/test-project.git",
        ),
        (
            "projects_empty.json",
            "ics-ans-zfs-snapshot-cleanup",
            "git@gitlab.com:ics-ansible-galaxy/ics-ans-zfs-snapshot-cleanup.git",
        ),
        (
            "project_null_description.json",
            "ics-ans-nas",
            "git@gitlab.com:ics-ansible-galaxy/ics-ans-nas.git",
        ),
    ],
)
def test_project_class(filename, expected_name, expected_ssh_url):
    # No error should be raised - extra keys are added
    project = Project(**sample(filename))
    assert project.name == expected_name
    assert project.ssh_url == expected_ssh_url


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {"name": "foo", "namespace": "bar"},
            "bar",
        ),
        (
            {"name": "foo", "namespace": {"name": "bar"}},
            "bar",
        ),
        (
            {
                "name": "foo",
                "namespace": "bar",
                "path_with_namespace": "test-group/subgroup-1/foo",
            },
            "test-group",
        ),
        (
            {
                "name": "my-project",
                "namespace": {"name": "bar"},
                "path_with_namespace": "group1/my-project",
            },
            "group1",
        ),
    ],
)
def test_project_base_namespace(data, expected):
    project = Project(**data)
    assert project.base_namespace == expected


@pytest.mark.parametrize(
    "filename, expected_name",
    [
        ("groups_id.json", "test-group"),
        ("groups_id_subgroup.json", "subgroup-2"),
        ("subgroup.json", "subgroup-1"),
    ],
)
def test_group_class(filename, expected_name):
    # No error should be raised - extra keys are ignored
    group = Group(**sample(filename))
    assert group.name == expected_name


def test_tag_class():
    name = "v0.4.1"
    target = "c06eae1694c526a797d47960ab78bf4729af6336"
    data = {
        "name": name,
        "message": "v0.4.1",
        "target": target,
        "commit": {
            "id": "c4863f5d4af58756944ef3bcc15a188f89148bcb",
            "short_id": "c4863f5d",
            "created_at": "2020-08-21T13:04:53.000+02:00",
            "parent_ids": ["8558d5bb65191886e36ddf4713e873475dfbe38f"],
            "title": "Update to molecule v3",
            "message": "Update to molecule v3\n",
            "committed_date": "2020-08-21T13:04:53.000+02:00",
            "web_url": "https://gitlab.com/ics-ansible-galaxy/ics-ans-role-conda-bot/-/commit/c4863f5d4af58756944ef3bcc15a188f89148bcb",
        },
        "release": None,
        "protected": False,
    }
    tag = Tag(**data)
    assert tag.name == name
    assert tag.target == target
