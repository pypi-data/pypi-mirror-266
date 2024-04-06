"""
Absfuyu: Generator
------------------
This generate stuff (Not python's ``generator``)

Version: 1.1.1
Date updated: 05/04/2024 (dd/mm/yyyy)

Features:
---------
- Generate random string
- Generate key
- Generate check digit
- Generate combinations of list in range
"""

# Module level
###########################################################################
__all__ = ["Charset", "Generator"]


# Library
###########################################################################
import string
from itertools import chain, combinations
from random import choice

# from string import (
#     ascii_letters as _ascii_letters,
#     ascii_uppercase as _ascii_uppercase,
#     ascii_lowercase as _ascii_lowercase,
#     digits as _digits,
#     printable as _printable,
#     punctuation as _punctuation,
# )
from typing import List

from absfuyu.logger import logger
from absfuyu.util import set_max, set_min_max


# Class
###########################################################################
class Charset:
    """
    Character set data class
    """

    DEFAULT = string.ascii_letters + string.digits
    ALPHABET = string.ascii_letters
    FULL = string.ascii_letters + string.digits + string.punctuation
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGIT = string.digits
    SPECIAL = string.punctuation
    ALL = string.printable
    PRODUCT_KEY = "BCDFGHJKMNPQRTVWXY2346789"  # Charset that various key makers use
    # DEFAULT = _ascii_letters + _digits
    # ALPHABET = _ascii_letters
    # FULL = _ascii_letters + _digits + _punctuation
    # UPPERCASE = _ascii_uppercase
    # LOWERCASE = _ascii_lowercase
    # DIGIT = _digits
    # SPECIAL = _punctuation
    # ALL = _printable

    def __str__(self) -> str:
        charset = [x for x in self.__class__.__dict__.keys() if not x.startswith("__")]
        return f"List of Character set: {charset}"

    def __repr__(self) -> str:
        return self.__str__()


class Generator:
    """
    Generator that generate stuffs
    """

    def __init__(self) -> None:
        logger.debug("Class initiated!")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def generate_string(
        charset: str = Charset.DEFAULT,
        size: int = 8,
        times: int = 1,
        unique: bool = False,
        string_type_if_1: bool = False,
    ):
        """
        Generate a list of random string from character set (Random string generator)

        Parameters
        ----------
        charset : str
            - Use custom character set or character sets already defined in ``Charset``
            - ``Charset.DEFAULT``: character in [a-zA-Z0-9] (default)
            - ``Charset.ALPHABET``: character in [a-zA-Z]
            - ``Charset.FULL``: character in [a-zA-Z0-9] + special characters
            - ``Charset.UPPERCASE``: character in [A-Z]
            - ``Charset.LOWERCASE``: character in [a-z]
            - ``Charset.DIGIT``: character in [0-9]
            - ``Charset.SPECIAL``: character in [!@#$%^&*()_+=-]
            - ``Charset.ALL``: character in every printable character

        size : int
            Length of each string in list
            (Default: ``8``)

        times : int
            How many random string generated
            (Default: ``1``)

        unique : bool
            Each generated text is unique
            (Default: ``False``)

        string_type_if_1 : bool
            Return a ``str`` type result if ``times == 1``
            (Default: ``False``)

        Returns
        -------
        list
            List of random string generated

        str
            When ``string_type_if_1`` is ``True``

        None
            When invalid option


        Example:
        --------
        >>> Generator.generate_string(times=3)
        ['67Xfh1fv', 'iChcGz9P', 'u82fNzlm']
        """

        try:
            char_lst = list(charset)
        except:
            char_lst = charset  # type: ignore # ! review this sometime
        # logger.debug(char_lst)

        unique_string = []
        count = 0
        logger.debug(f"Unique generated text: {unique}")

        while count < times:
            s = "".join(choice(char_lst) for _ in range(size))
            logger.debug(f"Time generated: {count+1}. Remaining: {times-count-1}. {s}")
            if not unique:
                unique_string.append(s)
                count += 1
            else:
                if s not in unique_string:
                    unique_string.append(s)
                    count += 1

        logger.debug(unique_string)
        if string_type_if_1 and times == 1:
            return unique_string[0]
        else:
            return unique_string

    @staticmethod
    def generate_key(
        charset: str = Charset.PRODUCT_KEY,
        letter_per_block: int = 5,
        number_of_block: int = 5,
        sep: str = "-",
    ) -> str:
        """
        Generate custom key

        Parameters
        ----------
        charset : str
            Character set
            (Default: ``Charset.PRODUCT_KEY``)

        letter_per_block : int
            Number of letter per key block
            (Default: ``5``)

        number_of_block : int
            Number of key block
            (Default: ``5``)

        sep : str
            Key block separator
            (Default: ``-``)

        Returns
        -------
        str
            Generated key


        Example:
        --------
        >>> Generator.generate_key(letter_per_block=10, number_of_block=2)
        'VKKPJVYD2H-M7R687QCV2'
        """
        out = sep.join(
            __class__.generate_string(  # type: ignore
                charset,
                size=letter_per_block,
                times=number_of_block,
                unique=False,
                string_type_if_1=False,
            )
        )
        logger.debug(out)
        return out

    @staticmethod
    def generate_check_digit(number: int) -> int:
        """
        Check digit generator

            "A check digit is a form of redundancy check used for
            error detection on identification numbers, such as
            bank account numbers, which are used in an application
            where they will at least sometimes be input manually.
            It is analogous to a binary parity bit used to
            check for errors in computer-generated data.
            It consists of one or more digits (or letters) computed
            by an algorithm from the other digits (or letters) in the sequence input.
            With a check digit, one can detect simple errors in
            the input of a series of characters (usually digits)
            such as a single mistyped digit or some permutations
            of two successive digits." (Wikipedia)

            This function use Luhn's algorithm to calculate

        Parameters
        ----------
        number : int
            Number to calculate check digit

        Returns
        -------
        int
            Check digit


        Example:
        --------
        >>> Generator.generate_check_digit("4129984562545")
        7
        """

        logger.debug(f"Base: {number}")
        # turn into list then reverse the order
        num = list(str(number))[::-1]
        sum = 0
        logger.debug(f"Reversed: {''.join(num)}")
        for i in range(len(num)):
            # convert back into integer
            num[i] = int(num[i])  # type: ignore
            if i % 2 == 0:
                # double value of the even-th digit
                num[i] *= 2
                # sum the character of digit if it's >= 10
                if num[i] >= 10:  # type: ignore
                    num[i] -= 9  # type: ignore
            sum += num[i]  # type: ignore
            logger.debug(f"Loop {i+1}: {num[i]}, {sum}")

        out = (10 - (sum % 10)) % 10
        logger.debug(f"Output: {out}")
        return out

    @staticmethod
    def combinations_range(
        sequence: list, *, min_len: int = 1, max_len: int = 0
    ) -> List[tuple]:
        """
        Generate all combinations of a ``sequence`` from ``min_len`` to ``max_len``

        Parameters
        ----------
        sequence : list
            A sequence that need to generate combination

        min_len : int
            Minimum ``r`` of ``combinations``
            (Default: ``1``)

        max_len : int
            Maximum ``r`` of ``combinations``
            (Default: ``0`` - len of ``sequence``)

        Returns
        -------
        list[tuple]
            A list of all combinations from range(``min_len``, ``max_len``) of ``sequence``
        """
        # Restrain
        if max_len < 1:
            max_len = len(sequence)
        max_len = int(set_max(max_len, max_value=len(sequence)))
        min_len = int(set_min_max(min_len, min_value=1, max_value=max_len))
        logger.debug(f"Combination range: [{min_len}, {max_len}]")

        # Return
        return list(
            chain.from_iterable(
                [list(combinations(sequence, i)) for i in range(min_len, max_len + 1)]
            )
        )


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)  # DEBUG
