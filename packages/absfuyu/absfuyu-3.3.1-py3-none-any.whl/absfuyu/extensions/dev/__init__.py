# type: ignore
"""
Absfuyu: Development
--------------------
Some stuffs that are not ready to use yet.
Use at your own risk, everything is subject to change

Version: 2.0.0
Date updated: 23/11/2023 (dd/mm/yyyy)
"""

# Module level
###########################################################################
__all__ = [
    "password_check",
    "fib",
]


# Library
###########################################################################
import base64
import re
from collections import deque
from functools import lru_cache
from typing import Dict, Final, List, NamedTuple


# PASSWORD CHECKER
def password_check(password: str) -> bool:
    """
    Verify the strength of 'password'.
    Returns a dict indicating the wrong criteria.
    A password is considered strong if:
    - 8 characters length or more
    - 1 digit or more
    - 1 symbol or more
    - 1 uppercase letter or more
    - 1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbols = re.compile(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]')
    symbol_error = symbols.search(password) is None

    detail = {
        "password_ok": not any(
            [  # overall result
                length_error,
                digit_error,
                uppercase_error,
                lowercase_error,
                symbol_error,
            ]
        ),
        "length_error": length_error,
        "digit_error": digit_error,
        "uppercase_error": uppercase_error,
        "lowercase_error": lowercase_error,
        "symbol_error": symbol_error,
    }

    return detail["password_ok"]


# FIBONACCI WITH CACHE
@lru_cache(maxsize=5)
def fib(n: int) -> int:
    """Fibonacci (recursive)"""
    # max recursion is 484
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


# https://stackoverflow.com/questions/563022/whats-python-good-practice-for-importing-and-offering-optional-features
def optional_import(module: str, name: str = None, package: str = None):
    import importlib

    try:
        module = importlib.import_module(module)
        return module if name is None else getattr(module, name)
    except ImportError as e:
        if package is None:
            package = module
        msg = f"install the '{package}' package to make use of this feature"
        import_error = e

        def _failed_import(*args):
            raise ValueError(msg) from import_error

        return _failed_import


def load_toml_file(toml_file: str):
    """
    Load ``.toml`` file

    :param toml_file: Path to ``.toml`` file
    """
    from sys import version_info as _python_version

    if _python_version.minor < 11:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            raise ImportError("Please install tomli python package")
        except:
            raise SystemExit
    else:
        import tomllib

    with open(toml_file, "rb") as file:
        toml_data = tomllib.load(file)
        return toml_data


def get_sitemap(url: str):
    import re

    import requests

    class Url(NamedTuple):
        base: str
        extra: str

        def __str__(self) -> str:
            return f"{self.base}{self.extra}"

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}({self.base}{self.extra})"

    # robots.txt
    # sitemap.xml
    if not url.endswith("/"):
        url += "/"
    pattern = re.compile(
        r"([(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b)([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
        re.IGNORECASE,
    )
    try:
        url += "sitemap.xml"
        res = requests.get(url).text
    except:
        # W.I.P
        url += "robots.txt"
        res = requests.get(url).text
    regex = re.findall(pattern, res)
    return list(map(Url._make, regex))


from absfuyu.general import ClassBase


class SimpleStrEncrypt(ClassBase):
    """
    Simple Encryption

    Logic:
    - Base64
    - Shift characters
    """

    def __init__(self, times_to_base64_encode: int = 10, shift: int = 13) -> None:
        """
        :param times_to_base64_encode: How many time to base64 encode
        :type times_to_base64_encode: int
        :param shift: Shift characters to the right for how many position
        :type shift: int
        """
        self.times_to_base64_encode = times_to_base64_encode
        self.shift = shift

    # Support
    def _convert_table(self, text: str, shift: int) -> Dict[str, str]:
        data = text

        data = deque(sorted(list(set(data))))
        translate = data.copy()
        translate.rotate(shift)
        convert_table = dict(zip(data, translate))

        return convert_table

    @staticmethod
    def _use_convert_table(text: str, convert_table: Dict[str, str]) -> str:
        """Use convert table"""
        data = list(text)
        for i, x in enumerate(data):
            data[i] = convert_table[x]
        return "".join(data)

    @staticmethod
    def _b64encode(text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def _b64decode(text: str) -> str:
        return base64.b64decode(text).decode()

    # Main
    def encode(self, text: str) -> str:
        # Base64
        data = text
        for _ in range(self.times_to_base64_encode):
            data = self._b64encode(data)

        # Shift
        convert_table = self._convert_table(data, self.shift)
        return self._use_convert_table(data, convert_table)

    def decode(self, text: str) -> str:
        # Shift back
        data = text
        convert_table = self._convert_table(data, -self.shift)
        data = self._use_convert_table(data, convert_table)

        # Base64
        for _ in range(self.times_to_base64_encode):
            data = self._b64decode(data)

        return data


# testing
CON_VAR: Final[List[str]] = ["a", "b"]  # Declare as final


if __name__ == "__main__":
    print(get_sitemap("https://kingdomality.com/"))
