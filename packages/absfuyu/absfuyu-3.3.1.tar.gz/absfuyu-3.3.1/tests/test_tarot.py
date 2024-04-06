"""
Test: Tarot

Version: 1.0.0
Date updated: 27/11/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import pytest

from absfuyu.fun.tarot import Tarot, TarotCard


# Test
###########################################################################
def test_tarot():
    assert type(Tarot().random_card()) == TarotCard
