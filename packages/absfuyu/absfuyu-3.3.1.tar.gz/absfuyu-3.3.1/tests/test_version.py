"""
Test: Version

Version: 1.2.0
Date updated: 22/03/2024 (dd/mm/yyyy)
"""

from itertools import product
from typing import List, Tuple

import pytest

from absfuyu.version import Bumper, ReleaseLevel, ReleaseOption, Version


# Version
class TestVersion:
    @pytest.mark.parametrize("tuple_", [(1, 0, 0), (1, 0, 0, "dev", 0)])
    def test_from_tuple(self, tuple_: tuple) -> None:
        try:
            _ = Version.from_tuple(tuple_)
            assert True
        except:
            assert False

    def test_from_tuple_error(self) -> None:
        with pytest.raises(ValueError) as excinfo:
            _ = Version.from_tuple((1, 0))
        assert str(excinfo.value)


# Bumper
def list_of_bumper_bump_test() -> (
    List[Tuple[Tuple[int, int, int, str, int], str, str, str]]
):
    bumper_list: List[Tuple[int, int, int, str, int]] = [
        (1, 0, 0, ReleaseLevel.FINAL, 0),
        (1, 3, 2, ReleaseLevel.FINAL, 0),
        (2, 4, 6, ReleaseLevel.RC, 0),
        (2, 4, 6, ReleaseLevel.DEV, 0),
    ]
    release_options: List[str] = [
        ReleaseOption.MAJOR,
        ReleaseOption.MINOR,
        ReleaseOption.PATCH,
    ]
    release_levels: List[str] = [ReleaseLevel.FINAL, ReleaseLevel.DEV, ReleaseLevel.RC]
    merged = list(product(bumper_list, release_options, release_levels))
    # TODO: Improve this
    result_list: List[str] = [
        # 1.0.0
        "2.0.0",  # major final
        "2.0.0.dev0",  # major dev
        "2.0.0.rc0",  # major rc
        "1.1.0",  # minor final
        "1.1.0.dev0",  # minor dev
        "1.1.0.rc0",  # minor rc
        "1.0.1",  # patch final
        "1.0.1.dev0",  # patch dev
        "1.0.1.rc0",  # patch rc
        # 1.3.2
        "2.0.0",  # major
        "2.0.0.dev0",
        "2.0.0.rc0",
        "1.4.0",  # minor
        "1.4.0.dev0",
        "1.4.0.rc0",
        "1.3.3",  # patch
        "1.3.3.dev0",
        "1.3.3.rc0",
        # 2.4.6.rc0
        "2.4.6",  # major
        "3.0.0.dev0",
        "2.4.6.rc1",
        "2.4.6",  # minor
        "2.5.0.dev0",
        "2.4.6.rc1",
        "2.4.6",  # patch
        "2.4.7.dev0",
        "2.4.6.rc1",
        # 2.4.6.dev0
        "2.4.6",  # major
        "2.4.6.dev1",
        "2.4.6.rc0",
        "2.4.6",  # minor
        "2.4.6.dev1",
        "2.4.6.rc0",
        "2.4.6",  # patch
        "2.4.6.dev1",
        "2.4.6.rc0",
    ]
    if not len(result_list) == len(merged):
        # Check length
        raise ValueError("length of result_list is not in correct length")
    out: List[Tuple[Bumper, str, str, str]] = [
        (x[0], x[1], x[2], result_list[i]) for i, x in enumerate(merged)
    ]
    return out


class TestBumper:
    @pytest.mark.parametrize(
        "bumper, release_option, release_channel, desired_output",
        list_of_bumper_bump_test(),
    )
    def test_bump(
        self,
        bumper: Tuple[int, int, int, str, int],
        release_option: str,
        release_channel: str,
        desired_output: str,
    ) -> None:
        bumper: Bumper = Bumper.from_tuple(bumper)
        bumper.bump(option=release_option, channel=release_channel)
        assert str(bumper) == desired_output
