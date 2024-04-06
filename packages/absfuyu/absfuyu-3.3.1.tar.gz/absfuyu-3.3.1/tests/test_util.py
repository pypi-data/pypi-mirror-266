"""
Test: Util

Version: 1.0.0
Date updated: 05/06/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import pytest

from absfuyu import util


# Test
###########################################################################
# set_min
def test_set_min():
    """Larger than min val"""
    assert util.set_min(10, min_value=0) == 10


def test_set_min_2():
    """Smaller than min val"""
    assert util.set_min(-5, min_value=0) == 0


# set_max
def test_set_max():
    """Larger than max val"""
    assert util.set_max(200, max_value=100) == 100


def test_set_max_2():
    """Smaller than max val"""
    assert util.set_max(10, max_value=100) == 10


# set_min_max
def test_set_min_max():
    """In range [min, max]"""
    assert util.set_min_max(50, min_value=0, max_value=100) == 50


def test_set_min_max_2():
    """Smaller than min"""
    assert util.set_min_max(-10, min_value=0, max_value=100) == 0


def test_set_min_max_3():
    """Larger than max"""
    assert util.set_min_max(200, min_value=0, max_value=100) == 100
