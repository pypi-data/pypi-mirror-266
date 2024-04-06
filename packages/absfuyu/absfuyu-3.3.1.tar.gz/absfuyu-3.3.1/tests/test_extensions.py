"""
Test: Extensions

Version: 1.0.0
Date updated: 24/11/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import pytest
from absfuyu import extensions as ext


def test_ext_load():
    assert ext.is_loaded() is True
