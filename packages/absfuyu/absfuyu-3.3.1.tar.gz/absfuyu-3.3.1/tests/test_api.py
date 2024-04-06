"""
Test: API

Version: 1.1.1
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Library
###########################################################################
import sys

import pytest

# from absfuyu.core import DATA_PATH
from absfuyu.util.api import APIRequest, PingResult, ping_windows


# Test
###########################################################################
@pytest.fixture
def instance() -> APIRequest:
    return APIRequest("https://dummyjson.com/quotes")


@pytest.mark.skip  # temporary skip
def test_API(instance: APIRequest) -> None:
    try:
        assert isinstance(instance.fetch_data_only().json()["quotes"], list)
    except:
        # No internet
        assert instance


def test_ping_windows() -> None:
    if sys.platform in ["win32", "cygwin"]:  # windows only
        res = ping_windows(["google.com"], 1)
        assert isinstance(res[0], PingResult)
    assert True
