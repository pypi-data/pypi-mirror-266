"""
Test: ListExt

Version: 1.3.0
Date updated: 22/03/2024 (dd/mm/yyyy)
"""

import pytest

from absfuyu.general.data_extension import ListExt


@pytest.fixture
def example():
    return ListExt([
        3, 8, 5,
        "Test", "String", "ABC",
        [1,2,3], [0,8,6]
    ])

@pytest.fixture
def example_2():
    return ListExt([
        "Test", "String", "ABC",
        "Tension", "Tent", "Strong"
    ])


@pytest.mark.data_extension
class TestListExt:
    # stringify
    def test_stringify(self, example: ListExt) -> None:
        assert all([isinstance(x, str) for x in example.stringify()]) is True

    # sorts
    def test_sorts(self, example: ListExt) -> None:
        assert example.sorts() == [
            3,
            5,
            8,
            "ABC",
            "String",
            "Test",
            [0, 8, 6],
            [1, 2, 3],
        ]

    # freq
    def test_freq(self, example_2: ListExt) -> None:
        assert example_2.freq(sort=True) == {
            "ABC": 1,
            "String": 1,
            "Strong": 1,
            "Tension": 1,
            "Tent": 1,
            "Test": 1,
        }

    def test_freq_2(self, example_2: ListExt) -> None:
        assert example_2.freq(sort=True, num_of_first_char=2) == {
            "AB": 1,
            "St": 2,
            "Te": 3,
        }

    def test_freq_3(self, example_2: ListExt) -> None:
        assert example_2.freq(
            sort=True, num_of_first_char=2, appear_increment=True
        ) == [1, 3, 6]

    # slice_points
    def test_slice_points(self, example_2: ListExt) -> None:
        assert example_2.slice_points([1, 3]) == [
            ["Test"],
            ["String", "ABC"],
            ["Tension", "Tent", "Strong"],
        ]

    # pick_one
    def test_pick_one(self) -> None:
        """Empty list"""
        try:
            ListExt([]).pick_one()
        except:
            assert True

    def test_pick_one_2(self, example_2: ListExt) -> None:
        assert len([example_2.pick_one()]) == 1

    # len_items
    def test_len_items(self, example_2: ListExt) -> None:
        assert example_2.len_items() == [4, 6, 3, 7, 4, 6]

    # mean_len
    def test_mean_len(self, example_2: ListExt) -> None:
        assert example_2.mean_len() == 5.0

    # apply
    def test_apply(self, example: ListExt) -> None:
        assert example.apply(str) == example.stringify()

    # unique
    def test_unique(self) -> None:
        assert ListExt([1, 1, 1, 1]).unique() == [1]

    # head
    def test_head(self, example: ListExt) -> None:
        assert example.head(3) == [3, 8, 5]

    def test_head_2(self, example: ListExt) -> None:
        """Max head len"""
        assert example.head(100) == list(example)

    # tail
    def test_tail(self, example_2: ListExt) -> None:
        assert example_2.tail(2) == ["Tent", "Strong"]

    def test_tail_2(self, example_2: ListExt) -> None:
        assert example_2.tail(100) == list(example_2)

    # get_random
    def test_get_random(self, example_2: ListExt) -> None:
        test = example_2.get_random(20)
        assert len(test) == 20

    # flatten
    def test_flatten(self, example: ListExt) -> None:
        test = example.flatten()
        assert test
