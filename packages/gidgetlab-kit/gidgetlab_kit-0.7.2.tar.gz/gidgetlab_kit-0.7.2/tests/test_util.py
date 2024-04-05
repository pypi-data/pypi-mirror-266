import pytest
from gidgetlab_kit import util


@pytest.mark.parametrize(
    "input, params",
    [
        ([], {}),
        (("a=b", "c=d", "e=f"), {"a": "b", "c": "d", "e": "f"}),
        (("archived=true",), {"archived": "true"}),
        (
            ("order_by=updated_at", "visibility=private"),
            {"order_by": "updated_at", "visibility": "private"},
        ),
    ],
)
def test_convert_params_to_dict(input, params):
    assert util.convert_params_to_dict(input) == params


@pytest.mark.parametrize("input", [("foo",), ("a=b", "archived")])
def test_convert_params_to_dict_failed(input):
    with pytest.raises(ValueError) as e:
        util.convert_params_to_dict(input)
    assert "shall be separated by '='" in str(e)


@pytest.mark.parametrize(
    "chunk, expected",
    [
        (1, [[1], [2], [3], [4], [5], [6], [7]]),
        (3, [[1, 2, 3], [4, 5, 6], [7]]),
        (10, [[1, 2, 3, 4, 5, 6, 7]]),
    ],
)
def test_divide_chunks(chunk, expected):
    MY_LIST = [1, 2, 3, 4, 5, 6, 7]
    assert list(util.divide_chunks(MY_LIST, chunk)) == expected
