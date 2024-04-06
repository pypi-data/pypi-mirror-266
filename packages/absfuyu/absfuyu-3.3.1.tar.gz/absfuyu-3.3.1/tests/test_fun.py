"""
Test: Fun

Version: 1.0.1
Date updated: 16/11/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import pytest

from absfuyu.fun import zodiac_sign, im_bored


# Test
###########################################################################
# zodiac
def test_zodiac():
    assert zodiac_sign(1, 1) == "Capricorn"


def test_zodiac_2():
    assert zodiac_sign(1, 1, zodiac13=True) == "Sagittarius"


# im_bored
def test_im_bored():
    # Basically True but put it in anyway
    assert im_bored()
