"""
Test: Converter

Version: 1.2.0
Date updated: 22/03/2024 (dd/mm/yyyy)
"""

import pytest

from absfuyu.general.generator import Charset, Generator
from absfuyu.tools.converter import Base64EncodeDecode, Text2Chemistry


@pytest.fixture
def instance():
    return Text2Chemistry()


# convert
class TestChemistryConvert:
    @pytest.mark.parametrize(
        ["instance", "value", "output"],
        [
            (Text2Chemistry(), "jump", []),
            (Text2Chemistry(), "queen", []),
        ],
    )
    def test_convert_not_work(
        self, instance: Text2Chemistry, value: str, output: list
    ) -> None:
        assert instance.convert(value) == output

    def test_convert(self, instance: Text2Chemistry) -> None:
        assert instance.convert("bakery") != []


# base64
class TestBase64:
    def test_base64_encode(self) -> None:
        test = Base64EncodeDecode.encode("Hello, World!")
        assert test == "SGVsbG8sIFdvcmxkIQ=="

    def test_base64_decode(self) -> None:
        test = Base64EncodeDecode.decode("SGVsbG8sIFdvcmxkIQ==")
        assert test == "Hello, World!"

    def test_base64_multiple(self) -> None:
        """Run multiple times"""
        TIMES = 100
        test = []
        for x in Generator.generate_string(Charset.FULL, times=TIMES):
            encode = Base64EncodeDecode.encode(x)
            test.append(x == Base64EncodeDecode.decode(encode))
        assert all(test)
