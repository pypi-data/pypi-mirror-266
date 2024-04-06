"""
Absufyu: Utilities
------------------
Some random utilities

Version: 1.5.1
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Library
###########################################################################
import pkgutil
from datetime import datetime
from typing import Optional, Union

from absfuyu.logger import logger


# Function
###########################################################################
def get_installed_package():
    """
    Return a list of installed packages

    Returns
    -------
    list[str]
        List of installed packages
    """
    iter_modules = list(
        {module.name for module in pkgutil.iter_modules() if module.ispkg}
    )
    return sorted(iter_modules)


def set_min(
        current_value: Union[int, float],
        *,
        min_value: Union[int, float] = 0,
    ) -> Union[int, float]:
    """
    Return ``min_value`` when ``current_value`` < ``min_value``

    Parameters
    ----------
    current_value : int | float
        Current value
    
    min_value : int | float
        Minimum value 
        (Default: ``0``)
    
    Returns
    -------
    int | float
        Analyzed value


    Example:
    --------
    >>> set_min(-1)
    0
    """
    if current_value < min_value:
        current_value = min_value
    return current_value

def set_max(
        current_value: Union[int, float],
        *,
        max_value: Union[int, float] = 100,
    ) -> Union[int, float]:
    """
    Return ``max_value`` when ``current_value`` > ``max_value``

    Parameters
    ----------
    current_value : int | float
        Current value
    
    max_value : int | float
        Maximum value 
        (Default: ``100``)
    
    Returns
    -------
    int | float
        Analyzed value


    Example:
    --------
    >>> set_max(101)
    100
    """
    if current_value > max_value:
        current_value = max_value
    return current_value

def set_min_max(
        current_value: Union[int, float],
        *,
        min_value: Union[int, float] = 0,
        max_value: Union[int, float] = 100
    ) -> Union[int, float]:
    """
    Return ``min_value`` | ``max_value`` when ``current_value``
    is outside ``[min_value, max_value]``

    Parameters
    ----------
    current_value : int | float
        Current value
    
    min_value : int | float
        Minimum value 
        (Default: ``0``)
    
    max_value : int | float
        Maximum value 
        (Default: ``100``)
    
    Returns
    -------
    int | float
        Analyzed value


    Example:
    --------
    >>> set_min_max(808)
    100
    """
    current_value = set_min(current_value, min_value=min_value)
    current_value = set_max(current_value, max_value=max_value)
    return current_value


def stop_after_day(
    year: Optional[int] = None, month: Optional[int] = None, day: Optional[int] = None
) -> None:
    """
    Stop working after specified day. 
    Put the function at the begining of the code is recommended.

    Parameters
    ----------
    year : int
        Desired year
        (Default: ``None``)

    month : int
        Desired month
        (Default: ``None``)

    day : int
        Desired day
        (Default: ``None`` - 1 day trial)
    """
    # None checking - By default: 1 day trial
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    if day is None:
        day = now.day + 1

    # Logic
    end_date = datetime(year, month, day)
    result = end_date - now
    if result.days < 0:
        raise SystemExit("End of time")


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
