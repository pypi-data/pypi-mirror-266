# type: ignore
"""
Absfuyu: Passwordlib
--------------------
Password library

Version: 1.0.0dev1
Date updated: 30/11/2023 (dd/mm/yyyy)
"""


# Library
###########################################################################
# from collections import namedtuple
import hashlib
import os
import random
import re
from typing import Dict, List, Optional, Union

from absfuyu_res import DATA

from absfuyu.general.data_extension import DictExt, Text
from absfuyu.general.generator import Charset, Generator
from absfuyu.logger import logger
from absfuyu.util import set_min
from absfuyu.util.pkl import Pickler


# Function
###########################################################################
def password_check(password: str) -> bool:
    """
    Verify the strength of ``password``.
    A password is considered strong if:

    - 8 characters length or more
    - 1 digit or more
    - 1 symbol or more
    - 1 uppercase letter or more
    - 1 lowercase letter or more

    :param password: Password want to be checked
    :type password: str
    :rtype: bool
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
        "length_error": length_error,
        "digit_error": digit_error,
        "uppercase_error": uppercase_error,
        "lowercase_error": lowercase_error,
        "symbol_error": symbol_error,
    }
    logger.debug(f"Password error summary: {detail}")

    return not any(
        [
            length_error,
            digit_error,
            uppercase_error,
            lowercase_error,
            symbol_error,
        ]
    )


# Class
###########################################################################
class Password:
    """Password"""

    def __init__(self) -> None:
        """doc_string"""
        self.password: str = None
        self._words: List[str] = Pickler.load(DATA.PASSWORDLIB)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()

    def password_hash(self):
        """
        Generate hash for password
        """
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=self.password.encode("utf-8"),
            salt=salt,
            iterations=100000,
        )
        out = {
            "salt": salt,
            "key": key,
        }
        return out

    @staticmethod
    def password_check(password: str):
        data = Text(password).analyze()
        data.__setitem__("length", len(password))
        data = DictExt(data).apply(lambda x: True if x > 0 else False)
        return data

    @property
    def words(self) -> List[str]:
        """
        Word list to generate passphrase

        :rtype: list[str]
        """
        return self._words

    # Password generator
    @staticmethod
    def generate_password(
        length: int = 8,
        include_uppercase: bool = True,
        include_number: bool = True,
        include_special: bool = True,
    ) -> str:
        r"""
        Generate a random password

        Parameters
        ----------
        length : int
            | Length of the password.
            | Minimum value: ``8``
            | (Default: ``8``)

        include_uppercase : bool
            Include uppercase character in the password (Default: ``True``)

        include_number : bool
            Include digit character in the password (Default: ``True``)

        include_special : bool
            Include special character in the password (Default: ``True``)

        Returns
        -------
        str
            Generated password


        Example:
        --------
        >>> Password.generate_password()
        [T&b@mq2
        """
        charset = Charset.LOWERCASE
        check = 0

        if include_uppercase:
            charset += Charset.UPPERCASE
            check += 1

        if include_number:
            charset += Charset.DIGIT
            check += 1

        if include_special:
            charset += r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]'
            check += 1

        while True:
            pwd = Generator.generate_string(
                charset=charset,
                size=set_min(length, min_value=8),
                times=1,
                string_type_if_1=True,
            )

            analyze = Text(pwd).analyze()  # Count each type of char

            s = sum([1 for x in analyze.values() if x > 0])
            if s > check:  # Break loop if each type of char has atleast 1
                break
        return pwd

    def generate_passphrase(
        self,
        num_of_blocks: int = 5,
        block_divider: Optional[str] = None,
        first_letter_cap: bool = True,
        include_number: bool = True,
    ) -> str:
        """
        Generate a random passphrase

        Parameters
        ----------
        num_of_blocks : int
            Number of word used (Default: ``5``)

        block_divider : str
            Character symbol that between each word (Default: ``"-"``)

        first_letter_cap : bool
            Capitalize first character of each word (Default: ``True``)

        include_number : bool
            Add number to the end of each word (Default: ``True``)

        Returns
        -------
        str
            Generated passphrase


        Example:
        --------
        >>> print(Password().generate_passphrase())
        Myomectomies7-Sully4-Torpedomen7-Netful2-Begaud8
        """

        def convert_func(value: str):
            if first_letter_cap:
                value = value.title()
            if include_number:
                value += str(random.choice(range(0, 10)))
            return value

        if not block_divider:
            block_divider = "-"

        return block_divider.join(
            [convert_func(random.choice(self.words)) for _ in range(num_of_blocks)]
        )


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
    # print(os.urandom(32))
    print(Password.password_check(Password.generate_password()))
