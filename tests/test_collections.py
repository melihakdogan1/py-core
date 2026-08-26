from pycore.collections import (
    are_disjoint_lists,
    chunk_list,
    create_student_record,
    filter_dict_by_keys,
    find_duplicates,
    find_missing_number,
    find_top_k_frequent,
    flatten_list,
    get_deep_value,
    group_by_key,
    invert_dict,
    list_difference,
    merge_dicts_sum,
    remove_duplicates_ordered,
    sliding_window_max,
)


def test_merge_dicts_sum() -> None:
    assert merge_dicts_sum({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {
        "a": 1,
        "b": 5,
        "c": 4,
    }


def test_group_by_key() -> None:
    data = [
        {"role": "admin", "name": "A"},
        {"role": "user", "name": "B"},
        {"role": "admin", "name": "C"},
    ]
    res = group_by_key(data, "role")
    assert len(res["admin"]) == 2
    assert len(res["user"]) == 1


def test_find_top_k_frequent() -> None:
    assert find_top_k_frequent([1, 1, 1, 2, 2, 3], 2) == [1, 2]


def test_invert_dict() -> None:
    assert invert_dict({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}


def test_sliding_window_max() -> None:
    assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]


def test_find_duplicates() -> None:
    assert sorted(find_duplicates([1, 2, 3, 2, 4, 1])) == [1, 2]


def test_flatten_list() -> None:
    assert flatten_list([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]


def test_chunk_list() -> None:
    assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_remove_duplicates_ordered() -> None:
    assert remove_duplicates_ordered([3, 1, 2, 3, 1, 4]) == [3, 1, 2, 4]


def test_list_difference() -> None:
    assert list_difference([1, 2, 3, 4], [2, 4]) == [1, 3]


def test_find_missing_number() -> None:
    assert find_missing_number([1, 2, 4, 5, 6], 6) == 3


def test_get_deep_value() -> None:
    data = {"user": {"profile": {"age": 22}}}
    assert get_deep_value(data, "user.profile.age") == 22
    assert get_deep_value(data, "user.settings.theme", default="dark") == "dark"


def test_filter_dict_by_keys() -> None:
    d = {"a": 1, "b": 2, "c": 3}
    assert filter_dict_by_keys(d, {"a", "c"}) == {"a": 1, "c": 3}


def test_create_student_record() -> None:
    s = create_student_record(1, "Melih", 3.85)
    assert s.id == 1
    assert s.name == "Melih"


def test_are_disjoint_lists() -> None:
    assert are_disjoint_lists([1, 2], [3, 4]) is True
    assert are_disjoint_lists([1, 2], [2, 3]) is False
