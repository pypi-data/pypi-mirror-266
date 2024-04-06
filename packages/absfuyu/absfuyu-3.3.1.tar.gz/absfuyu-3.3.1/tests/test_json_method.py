"""
Test: Json Method

Version: 1.1.0
Date updated: 22/11/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import pytest

from absfuyu.core import CONFIG_PATH
from absfuyu.util.json_method import JsonFile


# Test
###########################################################################
# @pytest.fixture
# def instance():
#     return JsonFile(path)


def test_json():
    test = JsonFile(CONFIG_PATH)
    ...
