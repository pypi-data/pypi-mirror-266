"""
Test: Obfuscator

Version: 1.0.0
Date updated: 05/06/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
import base64

import pytest

from absfuyu.tools.obfuscator import Obfuscator


# Test
###########################################################################
@pytest.fixture
def instance():
    code = "print('Hello World')"
    return Obfuscator(code=code)


# convert_to_base64_decode
def test_convert_to_base64_decode():
    assert eval(Obfuscator._convert_to_base64_decode("rot_13")) == "rot_13"


# obfuscate
def test_obfuscate(instance: Obfuscator):
    assert instance.obfuscate()
