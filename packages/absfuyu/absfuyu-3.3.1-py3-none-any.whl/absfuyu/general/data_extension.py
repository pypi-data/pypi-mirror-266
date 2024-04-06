"""
Absfuyu: Data extension
-----------------------
Extension for data type such as ``list``, ``str``, ``dict``, ...

Version: 1.14.3
Date updated: 05/04/2024 (dd/mm/yyyy)

Features:
---------
- DictExt
- IntNumber
- ListExt
- Text

Usage:
------
>>> from absfuyu.general.data_extension import DictExt, IntNumber, ListExt, Text
"""

# Module level
###########################################################################
__all__ = [
    # Main
    "Text",
    "IntNumber",
    "ListExt",
    "DictExt",
    # Sub
    "Pow",
    "ListREPR",
    "ListNoDunder",
    "DictBoolTrue",
    "DictBoolFalse",
    # "DictNoDunder",
    # Dict format
    "TextAnalyzeDictFormat",
    # Support
    "DictAnalyzeResult",
]


# Library
###########################################################################
import math
import operator
import random
from collections import Counter
from itertools import accumulate, chain, groupby
from sys import version_info as _python_version
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

if _python_version.minor >= 11:
    from typing import NotRequired
else:
    from typing_extensions import NotRequired  # type: ignore

from deprecated.sphinx import versionadded, versionchanged

from absfuyu.general.generator import Charset, Generator
from absfuyu.logger import _compress_list_for_print, logger
from absfuyu.util import set_min, set_min_max


# Function
###########################################################################
def _dict_bool(dict_object: dict, option: bool) -> Optional[dict]:
    """
    Support function DictBool class
    """
    out = dict()
    for k, v in dict_object.items():
        if v == option:
            out[k] = v
    if out:
        return out
    else:
        return None


# Sub class
###########################################################################
class Pow:
    """Number power by a number"""

    def __init__(self, number: Union[int, float], power_by: Union[int, float]) -> None:
        self.number = number
        self.power_by = power_by

    def __str__(self) -> str:
        if self.power_by == 1:
            return str(self.number)
        else:
            return f"{self.number}^{self.power_by}"
        # return f"{self.__class__.__name__}({self.number}, {self.power_by})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_list(self) -> List[Union[int, float]]:
        """
        Convert into list

        :rtype: list[int | float]
        """
        return [self.number] * int(self.power_by)

    def calculate(self) -> float:
        """
        Calculate the ``self.number`` to the power of ``self.power_by``

        :rtype: float
        """
        # return self.number**self.power_by
        return math.pow(self.number, self.power_by)


class ListREPR(list):
    """Show ``list`` in shorter form"""

    def __repr__(self) -> str:
        return _compress_list_for_print(self, 9)


class ListNoDunder(List[str]):
    """Use with ``object.__dir__()``"""

    def __repr__(self) -> str:
        out = [x for x in self if not x.startswith("__")]
        return out.__repr__()


class DictBoolTrue(Dict[Any, bool]):
    """Only show items when ``values == True`` in ``__repr__()``"""

    def __repr__(self) -> str:
        temp = self.copy()
        return _dict_bool(temp, True).__repr__()


class DictBoolFalse(Dict[Any, bool]):
    """Only show items when ``values == False`` in ``__repr__()``"""

    def __repr__(self) -> str:
        temp = self.copy()
        return _dict_bool(temp, False).__repr__()


# class DictNoDunder(dict):  # W.I.P
#     """Remove dunder methods in ``__repr__()`` of dict"""

#     def __repr__(self) -> str:
#             temp = self.copy()
#             out = dict()
#             for k, v in temp.items():
#                 if not str(k).startswith("__"):
#                     out.__setattr__(k, v)
#             return out.__repr__()


class TextAnalyzeDictFormat(TypedDict):
    """
    Dict format for ``Text.analyze()`` method

    Parameters
    ----------
    digit : int
        Number of digit characters

    uppercase : int
        Number of uppercase characters

    lowercase : int
        Number of lowercase characters

    other : int
        Number of other printable characters

    is_pangram : NotRequired[bool]
        Is a pangram (Not required)

    is_palindrome : NotRequired[bool]
        Is a palindrome (Not required)
    """

    digit: int
    uppercase: int
    lowercase: int
    other: int
    is_pangram: NotRequired[bool]
    is_palindrome: NotRequired[bool]


class DictAnalyzeResult(NamedTuple):
    """
    Result for ``DictExt.analyze()``
    """

    max_value: Union[int, float]
    min_value: Union[int, float]
    max_list: list
    min_list: list


# Class
###########################################################################
class Text(str):
    """
    ``str`` extension
    """

    def divide(self, string_split_size: int = 60) -> List[str]:
        """
        Divide long string into smaller size

        Parameters
        ----------
        string_split_size : int
            Divide string every ``x`` character
            (Default: ``60``)

        Returns
        -------
        list[str]
            A list in which each item is a smaller
            string with the size of ``string_split_size``
            (need to be concaternate later)


        Example:
        --------
        >>> test = Text("This is an extremely long line of text!")
        >>> test.divide(string_split_size=20)
        ['This is an extremely', ' long line of text!']
        """
        temp = str(self)
        output = []
        while len(temp) != 0:
            output.append(temp[:string_split_size])
            temp = temp[string_split_size:]
        return output

    def divide_with_variable(
        self,
        split_size: int = 60,
        split_var_len: int = 12,
        custom_var_name: Optional[str] = None,
    ) -> list:
        """
        Divide long string into smaller size,
        then assign a random variable to splited
        string for later use

        Parameters
        ----------
        split_size : int
            Divide string every ``x`` character
            (Default: ``60``)

        split_var_len : int
            Length of variable name assigned to each item
            (Default: ``12``)

        custom_var_name : str
            Custom variable name when join string

        Returns
        -------
        list
            A list in which each item is a smaller
            string with the size of ``split_size``
            and a way to concaternate them (when using ``print()``)


        Example:
        --------
        >>> test = Text("This is an extremely long line of text!")
        >>> test.divide_with_variable(split_size=20)
        [
            "qNTCnmkFPTJg='This is an extremely'",
            "vkmLBUykYYDG=' long line of text!'",
            'sBoSwEfoxBIH=qNTCnmkFPTJg+vkmLBUykYYDG',
            'sBoSwEfoxBIH'
        ]

        >>> test = Text("This is an extremely long line of text!")
        >>> test.divide_with_variable(split_size=20, custom_var_name="test")
        [
            "test1='This is an extremely'",
            "test2=' long line of text!'",
            'test=test1+test2',
            'test'
        ]
        """

        temp = self.divide(split_size)
        output = []

        # split variable
        splt_len = len(temp)

        if custom_var_name is None:
            splt_name = Generator.generate_string(
                charset=Charset.ALPHABET, size=split_var_len, times=splt_len + 1
            )
            for i in range(splt_len):
                output.append(f"{splt_name[i]}='{temp[i]}'")
        else:
            for i in range(splt_len):
                output.append(f"{custom_var_name}{i+1}='{temp[i]}'")

        # joined variable
        temp = []
        if custom_var_name is None:
            for i in range(splt_len):
                if i == 0:
                    temp.append(f"{splt_name[-1]}=")
                if i == splt_len - 1:
                    temp.append(f"{splt_name[i]}")
                else:
                    temp.append(f"{splt_name[i]}+")
        else:
            for i in range(splt_len):
                if i == 0:
                    temp.append(f"{custom_var_name}=")
                if i == splt_len - 1:
                    temp.append(f"{custom_var_name}{i+1}")
                else:
                    temp.append(f"{custom_var_name}{i+1}+")

        output.append("".join(temp))
        if custom_var_name is None:
            output.append(splt_name[-1])
        else:
            output.append(custom_var_name)

        return output

    @versionchanged(version="3.3.0", reason="Update functionality")
    def analyze(self, full: bool = False) -> TextAnalyzeDictFormat:
        """
        String analyze (count number of type of character)

        Parameters
        ----------
        full : bool
            Full analyze when ``True``
            (Default: ``False``)

        Returns
        -------
        dict | TextAnalyzeDictFormat
            A dictionary contains number of digit character,
            uppercase character, lowercase character, and
            special character


        Example:
        --------
        >>> test = Text("Random T3xt!")
        >>> test.analyze()
        {'digit': 1, 'uppercase': 2, 'lowercase': 7, 'other': 2}
        """

        temp = self

        detail: TextAnalyzeDictFormat = {
            "digit": 0,
            "uppercase": 0,
            "lowercase": 0,
            "other": 0,
        }

        for x in temp:
            if ord(x) in range(48, 58):  # num
                detail["digit"] += 1
            elif ord(x) in range(65, 91):  # cap
                detail["uppercase"] += 1
            elif ord(x) in range(97, 123):  # low
                detail["lowercase"] += 1
            else:
                detail["other"] += 1

        if full:
            detail["is_palindrome"] = self.is_palindrome()
            detail["is_pangram"] = self.is_pangram()

        return detail

    def reverse(self) -> "Text":
        """
        Reverse the string

        Returns
        -------
        Text
            Reversed string


        Example:
        --------
        >>> test = Text("Hello, World!")
        >>> test.reverse()
        '!dlroW ,olleH'
        """
        return self.__class__(self[::-1])

    def is_pangram(self) -> bool:
        """
        Check if string is a pangram

            A pangram is a unique sentence in which
            every letter of the alphabet is used at least once

        Returns
        -------
        bool
            | ``True`` if string is a pangram
            | ``False`` if string is not a pangram
        """
        text = self
        alphabet = set("abcdefghijklmnopqrstuvwxyz")
        return not set(alphabet) - set(text.lower())

    def is_palindrome(self) -> bool:
        """
        Check if string is a palindrome

            A palindrome is a word, verse, or sentence
            or a number that reads the same backward or forward

        Returns
        -------
        bool
            | ``True`` if string is a palindrome
            | ``False`` if string is not a palindrome
        """
        text = self
        # Use string slicing [start:end:step]
        return text == text[::-1]

    def to_hex(self, raw: bool = False) -> str:
        r"""
        Convert string to hex form

        Parameters
        ----------
        raw : bool
            | ``False``: hex string in the form of ``\x`` (default)
            | ``True``: normal hex string

        Returns
        -------
        str
            Hexed string


        Example:
        --------
        >>> test = Text("Hello, World!")
        >>> test.to_hex()
        '\\x48\\x65\\x6c\\x6c\\x6f\\x2c\\x20\\x57\\x6f\\x72\\x6c\\x64\\x21'
        """
        text = self

        byte_str = text.encode("utf-8")
        hex_str = byte_str.hex()

        if not raw:
            temp = []
            str_len = len(hex_str)

            for i in range(str_len):
                if i % 2 == 0:
                    temp.append(f"\\x")
                temp.append(hex_str[i])
            return "".join(temp)
        else:
            return hex_str

    def random_capslock(self, probability: int = 50) -> "Text":
        """
        Randomly capslock letter in string

        Parameters
        ----------
        probability : int
            Probability in range [0, 100]
            (Default: ``50``)

        Returns
        -------
        Text
            Random capslocked text


        Example:
        --------
        >>> test = Text("This is an extremely long line of text!")
        >>> test.random_capslock()
        'tHis iS An ExtREmELY loNg liNE oF tExT!'
        """
        probability = int(set_min_max(probability))
        text = self.lower()

        temp = []
        for x in text:
            if random.randint(1, 100) <= probability:
                x = x.upper()
            temp.append(x)
        logger.debug(temp)
        return self.__class__("".join(temp))

    def reverse_capslock(self) -> "Text":
        """
        Reverse capslock in string

        Returns
        -------
        Text
            Reversed capslock ``Text``


        Example:
        --------
        >>> test = Text("Foo")
        >>> test.reverse_capslock()
        'fOO'
        """
        temp = list(self)
        for i, x in enumerate(temp):
            if x.isupper():
                temp[i] = x.lower()
            else:
                temp[i] = x.upper()
        return self.__class__("".join(temp))

    def to_list(self) -> List[str]:
        """
        Convert into list

        Returns
        -------
        list[str]
            List of string


        Example:
        --------
        >>> test = Text("test")
        >>> test.to_list()
        ['t', 'e', 's', 't']
        """
        return list(self)

    @versionadded(version="3.3.0")
    def to_listext(self) -> "ListExt":
        """
        Convert into ``ListExt``

        Returns
        -------
        ListExt[str]
            List of string


        Example:
        --------
        >>> test = Text("test")
        >>> test.to_listext()
        ['t', 'e', 's', 't']
        """
        return ListExt(self)

    @versionadded(version="3.3.0")
    def count_pattern(self, pattern: str, ignore_capslock: bool = False) -> int:
        """
        Returns how many times ``pattern`` appears in text
        (Inspired by hackerrank exercise)

        Parameters
        ----------
        pattern : str
            Pattern to count

        ignore_capslock : bool
            Ignore the pattern uppercase or lowercase
            (Default: ``False`` - Exact match)

        Returns
        -------
        int
            How many times pattern appeared


        Example:
        --------
        >>> Text("test").count_pattern("t")
        2
        """
        if len(pattern) > len(self):
            raise ValueError(f"len(pattern) must not larger than {len(self)}")

        temp = str(self)
        if ignore_capslock:
            pattern = pattern.lower()
            temp = temp.lower()

        out = [
            1
            for i in range(0, len(temp) - len(pattern) + 1)
            if temp[i : i + len(pattern)] == pattern
        ]
        return sum(out)

    @versionadded(version="3.3.0")
    def hapax(self, strict: bool = False) -> List[str]:
        """
        A hapax legomenon (often abbreviated to hapax)
        is a word which occurs only once in either
        the written record of a language, the works of
        an author, or in a single text.

        This function returns a list of hapaxes (if any)
        (Lettercase is ignored)

        Parameters
        ----------
        strict : bool
            Remove all special characters before checking for hapax
            (Default: ``False``)

        Returns
        -------
        list[str]
            A list of hapaxes


        Example:
        --------
        >>> test = Text("A a. a, b c c= C| d d")
        >>> test.hapax()
        ['a', 'a.', 'a,', 'b', 'c', 'c=', 'c|']

        >>> test.hapax(strict=True)
        ['b']
        """
        word_list: List[str] = self.lower().split()
        if strict:
            remove_characters: List[str] = list("\"'.,:;|()[]{}\/!@#$%^&*-_=+?<>`~")
            temp = str(self)
            for x in remove_characters:
                temp = temp.replace(x, "")
            word_list = temp.lower().split()

        hapaxes = filter(lambda x: word_list.count(x) == 1, word_list)
        return list(hapaxes)


class IntNumber(int):
    """
    ``int`` extension
    """

    # convert stuff
    def to_binary(self) -> str:
        """
        Convert to binary number

        Returns
        -------
        str
            Binary number


        Example:
        --------
        >>> test = IntNumber(10)
        >>> test.to_binary()
        '1010'
        """
        return format(self, "b")

    def to_celcius_degree(self) -> float:
        """
        Convert into Celcius degree as if ``self`` is Fahrenheit degree

        Returns
        -------
        float
            Celcius degree


        Example:
        --------
        >>> test = IntNumber(10)
        >>> test.to_celcius_degree()
        -12.222222222222221
        """
        c_degree = (self - 32) / 1.8
        return c_degree

    def to_fahrenheit_degree(self) -> float:
        """
        Convert into Fahrenheit degree as if ``self`` is Celcius degree

        Returns
        -------
        float
            Fahrenheit degree


        Example:
        --------
        >>> test = IntNumber(10)
        >>> test.to_fahrenheit_degree()
        50.0
        """
        f_degree = (self * 1.8) + 32
        return f_degree

    # is_stuff
    def is_even(self) -> bool:
        """
        An even number is a number which divisible by 2

        Returns
        -------
        bool
            | ``True`` if an even number
            | ``False`` if not an even number
        """
        return self % 2 == 0

    def is_prime(self) -> bool:
        """
        Check if the integer is a prime number or not

            A prime number is a natural number greater than ``1``
            that is not a product of two smaller natural numbers.
            A natural number greater than ``1`` that is not prime
            is called a composite number.

        Returns
        -------
        bool
            | ``True`` if a prime number
            | ``False`` if not a prime number
        """
        number = self

        if number <= 1:
            return False
        for i in range(2, int(math.sqrt(number)) + 1):  # divisor range
            if number % i == 0:
                return False
        return True

    def is_twisted_prime(self) -> bool:
        """
        A number is said to be twisted prime if
        it is a prime number and
        reverse of the number is also a prime number

        Returns
        -------
        bool
            | ``True`` if a twisted prime number
            | ``False`` if not a twisted prime number
        """
        prime = self.is_prime()
        logger.debug(f"is prime: {prime}")
        rev = self.reverse().is_prime()
        logger.debug(f"is prime when reversed: {rev}")
        return prime and rev

    def is_perfect(self) -> bool:
        """
        Check if integer is perfect number

            Perfect number: a positive integer that is
            equal to the sum of its proper divisors.
            The smallest perfect number is ``6``, which is
            the sum of ``1``, ``2``, and ``3``.
            Other perfect numbers are ``28``, ``496``, and ``8,128``.

        Returns
        -------
        bool
            | ``True`` if a perfect number
            | ``False`` if not a perfect number
        """
        # ---
        """
        # List of known perfect number
        # Source: https://en.wikipedia.org/wiki/List_of_Mersenne_primes_and_perfect_numbers
        perfect_number_index = [
            2, 3, 5, 7,
            13, 17, 19, 31, 61, 89,
            107, 127, 521, 607,
            1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941,
            11_213, 19_937, 21_701, 23_209, 44_497, 86_243,
            110_503, 132_049, 216_091, 756_839, 859_433,
            # 1_257_787, 1_398_269, 2_976_221, 3_021_377, 6_972_593,
            # 13_466_917, 20_996_011, 24_036_583, 25_964_951,
            # 30_402_457, 32_582_657, 37_156_667, 42_643_801,
            # 43_112_609, 57_885_161,
            ## 74_207_281, 77_232_917, 82_589_933
        ]
        perfect_number = []
        for x in perfect_number_index:
            # a perfect number have a form of (2**(n-1))*((2**n)-1)
            perfect_number.append((2**(x-1))*((2**x)-1))
        """
        number = int(self)

        perfect_number = [
            6,
            28,
            496,
            8128,
            33_550_336,
            8_589_869_056,
            137_438_691_328,
            2_305_843_008_139_952_128,
        ]

        if number in perfect_number:
            return True

        elif number < perfect_number[-1]:
            return False

        else:
            # Faster way to check
            perfect_number_index: List[int] = [
                61,
                89,
                107,
                127,
                521,
                607,
                1279,
                2203,
                2281,
                3217,
                4253,
                4423,
                9689,
                9941,
                11_213,
                19_937,
                21_701,
                23_209,
                44_497,
                86_243,
                110_503,
                132_049,
                216_091,
                756_839,
                859_433,
                1_257_787,
                # 1_398_269,
                # 2_976_221,
                # 3_021_377,
                # 6_972_593,
                # 13_466_917,
                # 20_996_011,
                # 24_036_583,
                # 25_964_951,
                # 30_402_457,
                # 32_582_657,
                # 37_156_667,
                # 42_643_801,
                # 43_112_609,
                # 57_885_161,
                ## 74_207_281,
                ## 77_232_917,
                ## 82_589_933
            ]
            for x in perfect_number_index:
                # a perfect number have a form of (2**(n-1))*((2**n)-1)
                perfect_number = (2 ** (x - 1)) * ((2**x) - 1)
                if number < perfect_number:  # type: ignore
                    return False
                elif number == perfect_number:  # type: ignore
                    return True

            # Manual way when above method not working
            # sum
            s = 1
            # add all divisors
            i = 2
            while i * i <= number:
                if number % i == 0:
                    s += +i + number / i  # type: ignore
                i += 1
            # s == number -> perfect
            return True if s == number and number != 1 else False

    def is_narcissistic(self) -> bool:
        """
        Check if a narcissistic number

            In number theory, a narcissistic number
            (also known as a pluperfect digital invariant (PPDI),
            an Armstrong number (after Michael F. Armstrong)
            or a plus perfect number) in a given number base ``b``
            is a number that is the sum of its own digits
            each raised to the power of the number of digits.

        Returns
        -------
        bool
            | ``True`` if a narcissistic number
            | ``False`` if not a narcissistic number
        """
        try:
            check = sum([int(x) ** len(str(self)) for x in str(self)])
            res = int(self) == check
            return res  # type: ignore
        except:
            return False

    def reverse(self) -> "IntNumber":
        """
        Reverse a number. Reverse ``abs(number)`` if ``number < 0``

        Returns
        -------
        IntNumber
            Reversed number


        Example:
        --------
        >>> test = IntNumber(102)
        >>> test.reverse()
        201
        """
        number = int(self)
        if number <= 1:
            number *= -1
        return self.__class__(str(number)[::-1])

    def is_palindromic(self) -> bool:
        """
        A palindromic number (also known as a numeral palindrome
        or a numeric palindrome) is a number (such as ``16461``)
        that remains the same when its digits are reversed.

        Returns
        -------
        bool
            | ``True`` if a palindromic number
            | ``False`` if not a palindromic number
        """
        return self == self.reverse()

    def is_palindromic_prime(self) -> bool:
        """
        A palindormic prime is a number which is both palindromic and prime

        Returns
        -------
        bool
            | ``True`` if a palindormic prime number
            | ``False`` if not a palindormic prime number
        """
        return self.is_palindromic() and self.is_prime()

    # calculation stuff
    @versionchanged(version="3.3.0", reason="Fix bug")
    def lcm(self, with_number: int) -> "IntNumber":
        """
        Least common multiple of ``self`` and ``with_number``

        Parameters
        ----------
        with_number : int
            The number that want to find LCM with

        Returns
        -------
        IntNumber
            Least common multiple


        Example:
        --------
        >>> test = IntNumber(102)
        >>> test.lcm(5)
        510
        """
        try:
            return self.__class__(math.lcm(self, with_number))
        except:
            return self.__class__((self * with_number) // math.gcd(self, with_number))

    @versionchanged(version="3.3.0", reason="Fix bug")
    def gcd(self, with_number: int) -> "IntNumber":
        """
        Greatest common divisor of ``self`` and ``with_number``

        Parameters
        ----------
        with_number : int
            The number that want to find GCD with

        Returns
        -------
        IntNumber
            Greatest common divisor


        Example:
        --------
        >>> test = IntNumber(1024)
        >>> test.gcd(8)
        8
        """
        return self.__class__(math.gcd(self, with_number))

    def add_to_one_digit(self, master_number: bool = False) -> "IntNumber":
        """
        Convert ``self`` into 1-digit number
        by adding all of the digits together

        Parameters
        ----------
        master_number : bool
            | Break when sum = ``22`` or ``11`` (numerology)
            | (Default: ``False``)

        Returns
        -------
        IntNumber
            IntNumber


        Example:
        --------
        >>> test = IntNumber(119)
        >>> test.add_to_one_digit()
        2

        >>> test = IntNumber(119)
        >>> test.add_to_one_digit(master_number=True)
        11
        """
        number = int(self)
        if number < 0:
            number *= -1
        logger.debug(f"Current number: {number}")
        while len(str(number)) != 1:
            number = sum(map(int, str(number)))
            if master_number:
                if number == 22 or number == 11:
                    break  # Master number
            logger.debug(f"Sum after loop: {number}")
        return self.__class__(number)

    def divisible_list(self, short_form: bool = True) -> List[int]:
        """
        A list of divisible number

        Parameters
        ----------
        short_form : bool
            | Show divisible list in short form
            | Normal example: ``[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]``
            | Short form example: ``[1, 2, 4, 8, ...,128, 256, 512, 1024] [Len: 11]``
            | (Default: ``True``)

        Returns
        -------
        list[int]
            A list of divisible number


        Example:
        --------
        >>> test = IntNumber(1024)
        >>> test.divisible_list(short_form=False)
        [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        """

        if self <= 1:
            return [1]
        divi_list = [x for x in range(1, int(self / 2) + 1) if self % x == 0] + [self]

        if short_form:
            return divi_list
            # return ListREPR(divi_list) ## FIX LATER
        return divi_list

    def prime_factor(self, short_form: bool = True) -> Union[List[int], List[Pow]]:
        """
        Prime factor

        Parameters
        ----------
        short_form : bool
            | Show prime list in short form
            | Normal example: ``[2, 2, 2, 3, 3]``
            | Short form example: ``[2^3, 3^2]``
            | (Default: ``True``)

        Returns
        -------
        list[int] | list[Pow]
            | List of prime number that when multiplied together == ``self``
            | list[int]: Long form
            | list[Pow]: Short form


        Example:
        --------
        >>> test = IntNumber(1024)
        >>> test.prime_factor()
        [2^10]

        >>> test = IntNumber(1024)
        >>> test.prime_factor(short_form=False)
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        """
        # Generate list
        factors = []
        divisor = 2
        number = int(self)
        if number <= 1:
            return [number]
        while divisor <= number:
            if number % divisor == 0:
                factors.append(divisor)
                number //= divisor  # number = number // divisor
            else:
                divisor += 1

        # Output
        if short_form:
            temp = dict(Counter(factors))
            return [Pow(k, v) for k, v in temp.items()]
        return factors

    # analyze
    def analyze(self, short_form: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the number with almost all ``IntNumber`` method

        Parameters
        ----------
        short_form : bool
            | Enable short form for some items
            | (Default: ``True``)

        Returns
        -------
        dict[str, dict[str, Any]]
            Detailed analysis


        Example:
        --------
        >>> test = IntNumber(1024)
        >>> test.analyze()
        {
            'summary': {'number': 1024, 'length': 4, 'even': True, 'prime factor': [2^10], 'divisible': [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]},
            'convert': {'binary': '10000000000', 'octa': '2000', 'hex': '400', 'reverse': 4201, 'add to one': 7},
            'characteristic': {'prime': False, 'twisted prime': False, 'perfect': False, 'narcissistic': False, 'palindromic': False, 'palindromic prime': False}
        }
        """
        output = {
            "summary": {
                "number": self,
                "length": len(str(self)),
                "even": self.is_even(),
                "prime factor": self.prime_factor(short_form=short_form),
                "divisible": self.divisible_list(short_form=short_form),
            },
            "convert": {
                "binary": bin(self)[2:],
                "octa": oct(self)[2:],
                "hex": hex(self)[2:],
                # "hash": hash(self),
                "reverse": self.reverse(),
                "add to one": self.add_to_one_digit(),
            },
        }
        characteristic = {
            "prime": self.is_prime(),
            "twisted prime": self.is_twisted_prime(),
            "perfect": self.is_perfect(),
            "narcissistic": self.is_narcissistic(),
            "palindromic": self.is_palindromic(),
            "palindromic prime": self.is_palindromic_prime(),
        }
        if short_form:
            characteristic = DictBoolTrue(characteristic)

        output["characteristic"] = characteristic
        return output  # type: ignore


class ListExt(list):
    """
    ``list`` extension
    """

    def stringify(self) -> "ListExt":
        """
        Convert all item in ``list`` into string

        Returns
        -------
        ListExt
            A list with all items with type <str`>


        Example:
        --------
        >>> test = ListExt([1, 1, 1, 2, 2, 3])
        >>> test.stringify()
        ['1', '1', '1', '2', '2', '3']
        """
        return ListExt(map(str, self))

    def head(self, number_of_items: int = 5) -> list:
        """
        Show first ``number_of_items`` items in ``ListExt``

        Parameters
        ----------
        number_of_items : int
            | Number of items to shows at once
            | (Default: ``5``)

        Returns
        -------
        list
            Filtered list
        """
        number_of_items = int(
            set_min_max(number_of_items, min_value=0, max_value=len(self))
        )
        return self[:number_of_items]

    def tail(self, number_of_items: int = 5) -> list:
        """
        Show last ``number_of_items`` items in ``ListExt``

        Parameters
        ----------
        number_of_items : int
            | Number of items to shows at once
            | (Default: ``5``)

        Returns
        -------
        list
            Filtered list
        """
        number_of_items = int(
            set_min_max(number_of_items, min_value=0, max_value=len(self))
        )
        return self[::-1][:number_of_items][::-1]

    def sorts(self, reverse: bool = False) -> "ListExt":
        """
        Sort all items (with different type) in ``list``

        Parameters
        ----------
        reverse : bool
            | if ``True`` then sort in descending order
            | if ``False`` then sort in ascending order
            | (Default: ``False``)

        Returns
        -------
        ListExt
            A sorted list


        Example:
        --------
        >>> test = ListExt([9, "abc", 3.5, "aaa", 1, 1.4])
        >>> test.sorts()
        [1, 9, 'aaa', 'abc', 1.4, 3.5]
        """
        lst = self.copy()
        type_weights: dict = {}
        for x in lst:
            if type(x) not in type_weights:
                type_weights[type(x)] = len(type_weights)
        logger.debug(f"Type weight: {type_weights}")

        output = sorted(
            lst, key=lambda x: (type_weights[type(x)], str(x)), reverse=reverse
        )

        logger.debug(output)
        return self.__class__(output)

    def freq(
        self,
        sort: bool = False,
        num_of_first_char: Optional[int] = None,
        appear_increment: bool = False,
    ) -> Union[dict, List[int]]:
        """
        Find frequency of each item in list

        Parameters
        ----------
        sort : bool
            | if ``True``: Sorts the output in ascending order
            | if ``False``: No sort

        num_of_first_char : int | None
            | Number of first character taken into account to sort
            | (Default: ``None``)
            | (num_of_first_char = ``1``: first character in each item)

        appear_increment : bool
            | return incremental index list of each item when sort
            | (Default: ``False``)

        Returns
        -------
        dict
            A dict that show frequency

        list[int]
            Incremental index list


        Example:
        --------
        >>> test = ListExt([1, 1, 2, 3, 5, 5])
        >>> test.freq()
        {1: 2, 2: 1, 3: 1, 5: 2}

        >>> test = ListExt([1, 1, 2, 3, 3, 4, 5, 6])
        >>> test.freq(appear_increment=True)
        [2, 3, 5, 6, 7, 8]
        """

        if sort:
            data = self.sorts().copy()
        else:
            data = self.copy()

        if num_of_first_char is None:
            temp = Counter(data)
        else:
            max_char: int = min([len(str(x)) for x in data])
            logger.debug(f"Max character: {max_char}")
            if num_of_first_char not in range(1, max_char):
                logger.debug(f"Not in {range(1, max_char)}. Using default value...")
                temp = Counter(data)
            else:
                logger.debug(f"Freq of first {num_of_first_char} char")
                temp = Counter([str(x)[:num_of_first_char] for x in data])

        try:
            times_appear = dict(sorted(temp.items()))
        except:
            times_appear = dict(self.__class__(temp.items()).sorts())
        logger.debug(times_appear)

        if appear_increment:
            times_appear_increment: List[int] = list(
                accumulate(times_appear.values(), operator.add)
            )
            logger.debug(times_appear_increment)
            return times_appear_increment
        else:
            return times_appear

    def slice_points(self, points: list) -> List[list]:
        """
        Slices a list at specific indices into constituent lists.

        Parameters
        ----------
        points : list
            List of indices to slice

        Returns
        -------
        list[list]
            Sliced list


        Example:
        --------
        >>> test = ListExt([1, 1, 2, 3, 3, 4, 5, 6])
        >>> test.slice_points([2, 5])
        [[1, 1], [2, 3, 3], [4, 5, 6]]
        """
        points.append(len(self))
        data = self.copy()
        # return [data[points[i]:points[i+1]] for i in range(len(points)-1)]
        return [data[i1:i2] for i1, i2 in zip([0] + points[:-1], points)]

    def pick_one(self) -> Any:
        """
        Pick one random items from ``list``

        Returns
        -------
        Any
            Random value


        Example:
        --------
        >>> test = ListExt(["foo", "bar"])
        >>> test.pick_one()
        'bar'
        """
        if len(self) != 0:
            out = random.choice(self)
            logger.debug(out)
            return out
        else:
            logger.debug("List empty!")
            raise IndexError("List empty!")

    def get_random(self, number_of_items: int = 5) -> list:
        """
        Get ``number_of_items`` random items in ``ListExt``

        Parameters
        ----------
        number_of_items : int
            | Number random of items
            | (Default: ``5``)

        Returns
        -------
        list
            Filtered list
        """
        return [self.pick_one() for _ in range(number_of_items)]

    def len_items(self) -> "ListExt":
        """
        ``len()`` for every item in ``list[str]``

        Returns
        -------
        ListExt
            List of ``len()``'ed value


        Example:
        --------
        >>> test = ListExt(["foo", "bar", "pizza"])
        >>> test.len_items()
        [3, 3, 5]
        """
        out = ListExt([len(str(x)) for x in self])
        # out = ListExt(map(lambda x: len(str(x)), self))
        logger.debug(out)
        return out

    def mean_len(self) -> float:
        """
        Average length of every item

        Returns
        -------
        float
            Average length


        Example:
        --------
        >>> test = ListExt(["foo", "bar", "pizza"])
        >>> test.mean_len()
        3.6666666666666665
        """
        out = sum(self.len_items()) / len(self)
        logger.debug(out)
        return out

    def apply(self, func: Callable) -> "ListExt":
        """
        Apply function to each entry

        Parameters
        ----------
        func : Callable
            Callable function

        Returns
        -------
        ListExt
            ListExt


        Example:
        --------
        >>> test = ListExt([1, 2, 3])
        >>> test.apply(str)
        ['1', '2', '3']
        """
        # return __class__(func(x) for x in self)
        return self.__class__(map(func, self))

    def unique(self) -> "ListExt":
        """
        Remove duplicates

        Returns
        -------
        ListExt
            Duplicates removed list


        Example:
        --------
        >>> test = ListExt([1, 1, 1, 2, 2, 3])
        >>> test.unique()
        [1, 2, 3]
        """
        return self.__class__(set(self))

    def group_by_unique(self) -> "ListExt":
        """
        Group duplicated elements into list

        Returns
        -------
        ListExt
            Grouped value


        Example:
        --------
        >>> test = ListExt([1, 2, 3, 1, 3, 3, 2])
        >>> test.group_by_unique()
        [[1, 1], [2, 2], [3, 3, 3]]
        """
        # Old
        # out = self.sorts().slice_points(self.freq(appear_increment=True))
        # return __class__(out[:-1])

        # New
        temp = groupby(self.sorts())
        return self.__class__([list(g) for _, g in temp])

    @staticmethod
    def _group_by_unique(iterable: list) -> List[list]:
        """
        Static method for ``group_by_unique``
        """
        return list([list(g) for _, g in groupby(iterable)])

    def group_by_pair_value(self, max_loop: int = 3) -> List[list]:
        """
        Assume each ``list`` in ``list`` is a pair value,
        returns a ``list`` contain all paired value

        Parameters
        ----------
        max_loop : int
            Times to run functions (minimum: ``3``)

        Returns
        -------
        list[list]
            Grouped value


        Example:
        --------
        >>> test = ListExt([[1, 2], [2, 3], [4, 3], [5, 6]])
        >>> test.group_by_pair_value()
        [[1, 2, 3, 4], [5, 6]]

        >>> test = ListExt([[8, 3], [4, 6], [6, 3], [5, 2], [7, 2]])
        >>> test.group_by_pair_value()
        [[8, 3, 4, 6], [2, 5, 7]]

        >>> test = ListExt([["a", 4], ["b", 4], [5, "c"]])
        >>> test.group_by_pair_value()
        [['a', 4, 'b'], ['c', 5]]
        """

        iter = self.copy()

        # Init loop
        for _ in range(int(set_min(max_loop, min_value=3))):
            temp: Dict[Any, list] = {}
            # Make dict{key: all `item` that contains `key`}
            for item in iter:
                for x in item:
                    if temp.get(x, None) is None:
                        temp[x] = [item]
                    else:
                        temp[x].append(item)

            # Flatten dict.values
            for k, v in temp.items():
                temp[k] = list(set(chain(*v)))

            iter = list(temp.values())

        return list(x for x, _ in groupby(iter))

    def flatten(self) -> "ListExt":
        """
        Flatten the list

        Returns
        -------
        ListExt
            Flattened list


        Example:
        --------
        >>> test = ListExt([["test"], ["test", "test"], ["test"]])
        >>> test.flatten()
        ['test', 'test', 'test', 'test']
        """
        try:
            return ListExt(chain(*self))
        except:
            temp = list(map(lambda x: x if isinstance(x, list) else [x], self))
            return ListExt(chain(*temp))

    def numbering(self, start: int = 0) -> "ListExt":
        """
        Number the item in list
        (``enumerate`` wrapper)

        Parameters
        ----------
        start : int
            Start from which number
            (Default: ``0``)

        Returns
        -------
        ListExt
            Counted list


        Example:
        --------
        >>> test = ListExt([9, 9, 9])
        >>> test.numbering()
        [(0, 9), (1, 9), (2, 9)]
        """
        start = int(set_min(start, min_value=0))
        return ListExt(enumerate(self, start=start))

    @staticmethod
    def _numbering(iterable: list, start: int = 0) -> List[Tuple[int, Any]]:
        """
        Static method for ``numbering``
        """
        start = int(set_min(start, min_value=0))
        return list(enumerate(iterable, start=start))


class DictExt(dict):
    """
    ``dict`` extension
    """

    @versionchanged(
        version="3.3.0",
        reason="Change function output; Before: <dict>, Now: DictAnalyzeResult",
    )
    def analyze(self) -> DictAnalyzeResult:
        """
        Analyze all the key values (``int``, ``float``)
        in ``dict`` then return highest/lowest index

        Returns
        -------
        dict
            Analyzed data


        Example:
        --------
        >>> test = DictExt({
        >>>     "abc": 9,
        >>>     "def": 9,
        >>>     "ghi": 8,
        >>>     "jkl": 1,
        >>>     "mno": 1
        >>> })
        >>> test.analyze()
        DictAnalyzeResult(max_value=9, min_value=1, max_list=[('abc', 9), ('def', 9)], min_list=[('jkl', 1), ('mno', 1)])
        """
        try:
            dct: dict = self.copy()

            max_val: Union[int, float] = max(list(dct.values()))
            min_val: Union[int, float] = min(list(dct.values()))
            max_list = []
            min_list = []

            for k, v in dct.items():
                if v == max_val:
                    max_list.append((k, v))
                if v == min_val:
                    min_list.append((k, v))

            # output = {
            #     "max_value": max_val,
            #     "min_value": min_val,
            #     "max": max_list,
            #     "min": min_list,
            # }

            # logger.debug(output)
            # return output
            return DictAnalyzeResult(max_val, min_val, max_list, min_list)

        except:
            err_msg = "Value must be int or float"
            logger.error(err_msg)
            raise ValueError(err_msg)

    def swap_items(self) -> "DictExt":
        """
        Swap ``dict.keys()`` with ``dict.values()``

        Returns
        -------
        DictExt
            Swapped dict


        Example:
        --------
        >>> test = DictExt({"abc": 9})
        >>> test.swap_items()
        {9: 'abc'}
        """
        return self.__class__(zip(self.values(), self.keys()))

    def apply(self, func: Callable, apply_to_value: bool = True) -> "DictExt":
        """
        Apply function to ``DictExt.keys()`` or ``DictExt.values()``

        Parameters
        ----------
        func : Callable
            Callable function

        apply_to_value : bool
            | ``True``: Apply ``func`` to ``DictExt.values()``
            | ``False``: Apply ``func`` to ``DictExt.keys()``

        Returns
        -------
        DictExt
            DictExt


        Example:
        --------
        >>> test = DictExt({"abc": 9})
        >>> test.apply(str)
        {'abc': '9'}
        """
        if apply_to_value:
            k = self.keys()
            v = map(func, self.values())
        else:
            k = map(func, self.keys())  # type: ignore
            v = self.values()  # type: ignore
        return self.__class__(zip(k, v))


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
