"""
Test: Path

Version: 1.0.0
Date updated: 27/05/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import pytest

from absfuyu.core import CORE_PATH
from absfuyu.util.path import Directory


# Test
###########################################################################
@pytest.fixture
def instance():
    return Directory(source_path=CORE_PATH)


def test_DirStructure(instance: Directory):
    assert instance.list_structure_pkg()
