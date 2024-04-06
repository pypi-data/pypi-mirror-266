"""
Test: DictExt

Version: 1.3.1
Date updated: 22/03/2024 (dd/mm/yyyy)
"""

import pytest

from absfuyu.general.data_extension import DictAnalyzeResult, DictExt


@pytest.fixture
def example():
    return DictExt({
        "Line 1": 99,
        "Line 2": 50
    })

@pytest.fixture
def example_2():
    return DictExt({
        "Line 1": 99,
        "Line 2": "test"
    })


@pytest.mark.data_extension
class TestDictExt:
    # analyze
    def test_analyze(self, example: DictExt) -> None:
        # assert example.analyze() == {'max_value': 99, 'min_value': 50, 'max': [('Line 1', 99)], 'min': [('Line 2', 50)]}
        assert example.analyze() == DictAnalyzeResult(
            99, 50, [("Line 1", 99)], [("Line 2", 50)]
        )

    def test_analyze_error(self, example_2: DictExt) -> None:
        """When values are not int or float"""
        with pytest.raises(ValueError) as excinfo:
            example_2.analyze()
        assert str(excinfo.value)

    # swap
    def test_swap(self, example: DictExt) -> None:
        assert example.swap_items() == {99: "Line 1", 50: "Line 2"}

    # apply
    def test_apply(self, example: DictExt) -> None:
        """Values"""
        assert example.apply(str) == {"Line 1": "99", "Line 2": "50"}

    def test_apply_2(self) -> None:
        """Keys"""
        assert DictExt({1: 1}).apply(str, apply_to_value=False) == {"1": 1}
