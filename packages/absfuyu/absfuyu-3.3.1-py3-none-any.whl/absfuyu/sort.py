# type: ignore
"""
Absfuyu: Sort
-------------
Sort Module

Version: 1.2.4
Date updated: 20/03/2024 (mm/dd/yyyy)
"""

# Module level
###########################################################################
__all__ = [
    # Sort
    "selection_sort",
    "insertion_sort",
    # Alphabet
    "alphabetAppear",
    "AlphabetAppearResult",
    # Search
    "linear_search",
    "binary_search",
]


# Library
###########################################################################
import operator
from collections import Counter
from itertools import accumulate
from typing import Any, Dict, List, NamedTuple, Union

from deprecated import deprecated
from deprecated.sphinx import (
    deprecated as sphinx_deprecated,  # versionadded,; versionchanged,
)

from absfuyu.logger import logger


# Functions
###########################################################################
def selection_sort(iterable: list, reverse: bool = False) -> list:
    """
    Sort the list with selection sort (bubble sort) algorithm

    Parameters
    ----------
    iterable : list
        List that want to be sorted

    reverse : bool
        | if ``True``: sort in descending order
        | if ``False``: sort in ascending order
        | (default: ``False``)

    Returns
    -------
    list
        sorted list
    """

    if reverse:  # descending order
        for i in range(len(iterable)):
            for j in range(i + 1, len(iterable)):
                if iterable[i] < iterable[j]:
                    iterable[i], iterable[j] = iterable[j], iterable[i]
        return iterable

    else:  # ascending order
        for i in range(len(iterable)):
            for j in range(i + 1, len(iterable)):
                if iterable[i] > iterable[j]:
                    iterable[i], iterable[j] = iterable[j], iterable[i]
        return iterable


def insertion_sort(iterable: list) -> list:
    """
    Sort the list with insertion sort algorithm

    Parameters
    ----------
    iterable : list
        List that want to be sorted

    Returns
    -------
    list
        sorted list (ascending order)
    """

    for i in range(1, len(iterable)):
        key = iterable[i]
        j = i - 1
        while j >= 0 and key < iterable[j]:
            iterable[j + 1] = iterable[j]
            j -= 1
        iterable[j + 1] = key
    return iterable


def _alphabetAppear_old(
    lst: List[str],
) -> List[Union[Dict[str, int], List[int]]]:
    r"""
    Summary
    -------
    Make a dict that show the frequency of
    item name's first character in list
    in alphabet order

    For example:

    >>> ["apple","bee","book"]

    freq = {"a": 1, "b": 2}

    Parameters
    ----------
    lst : list
        list that want to be analyzed

    Returns
    -------
    list
        analyzed list (list[0])
        apperance incremental value index (list[1])
    """

    al_char = [x[0] for x in selection_sort(lst)]
    times_appear = dict()
    for x in al_char:
        if x in times_appear:
            times_appear[x] += 1
        else:
            times_appear[x] = 1

    times_appear_increment = []
    total = 0
    for x in times_appear.values():
        total += x
        times_appear_increment.append(total)

    # first item is character frequency
    # second item is incremental index list
    return [times_appear, times_appear_increment]


class AlphabetAppearResult(NamedTuple):
    times_appear: Dict[str, int]
    times_appear_increment: List[int]


@deprecated(version="3.0.0", reason="In absfuyu ``ListExt``")
@sphinx_deprecated(version="3.0.0", reason="In absfuyu ``ListExt``")
def alphabetAppear(iterable: list, num_of_char_sorted: int = 1) -> AlphabetAppearResult:
    """
    Make a dict that show the frequency of
    item name's first character in list
    in alphabet order

    Parameters
    ----------
    iterable : list
        List that want to be analyzed

    num_of_char_sorted : int
        Number of first character taken into account to sort
        (default: ``1`` - first character in each item)

    Returns
    -------
    AlphabetAppearResult
        | Analyzed list (``AlphabetAppearResult.times_appear``)
        | Apperance incremental value index (``AlphabetAppearResult.times_appear_increment``)


    Example:
    --------
    >>> alphabetAppear(["apple", "bee", "book"])
    AlphabetAppearResult(times_appear={'a': 1, 'b': 2}, times_appear_increment=[1, 3])
    """

    if not isinstance(num_of_char_sorted, int):
        logger.debug("num_of_char_sorted is not int")
        num_of_char_sorted = 1
    if num_of_char_sorted < 1:
        logger.debug("num_of_char_sorted < 1")
        num_of_char_sorted = 1
    if num_of_char_sorted > min([len(str(x)) for x in iterable]):
        logger.debug("num_of_char_sorted > item length")
        num_of_char_sorted = min([len(str(x)) for x in iterable])
    temp = Counter([str(x)[:num_of_char_sorted] for x in iterable])
    times_appear = dict(sorted(temp.items()))
    logger.debug(times_appear)

    temp = accumulate(times_appear.values(), operator.add)
    times_appear_increment: List[int] = list(temp)
    logger.debug(times_appear_increment)

    # first item is character frequency
    # second item is incremental index list
    return AlphabetAppearResult(times_appear, times_appear_increment)


def linear_search(iterable: list, key: Any) -> int:
    """
    Returns the position of ``key`` in the list

    Parameters
    ----------
    iterable : list
        List want to search

    key: Any
        Item want to find

    Returns
    -------
    int
        The position of ``key`` in the list if found, ``-1`` otherwise
    """
    for i, item in enumerate(iterable):
        if item == key:
            return i
    return -1


def binary_search(iterable: list, key: Any) -> int:
    """
    Returns the position of ``key`` in the list (list must be sorted)

    Parameters
    ----------
    iterable : list
        List want to search

    key: Any
        Item want to find

    Returns
    -------
    int
        The position of ``key`` in the list if found, ``-1`` otherwise
    """
    left = 0
    right = len(iterable) - 1
    while left <= right:
        middle = (left + right) // 2

        if iterable[middle] == key:
            return middle
        if iterable[middle] > key:
            right = middle - 1
        if iterable[middle] < key:
            left = middle + 1
    return -1


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
