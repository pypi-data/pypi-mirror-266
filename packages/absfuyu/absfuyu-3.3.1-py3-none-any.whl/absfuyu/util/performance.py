"""
Absfuyu: Performance
--------------------
Performance Check

Version: 1.2.3
Date updated: 05/04/2024 (dd/mm/yyyy)

Feature:
--------
- measure_performance
- function_debug
- retry
- var_check
- Checker
"""

# Module level
###########################################################################
__all__ = [
    # Wrapper
    "function_debug",
    "measure_performance",
    "retry",
    # Functions
    "var_check",
    # Class
    "Checker",
]


# Library
###########################################################################
import time
import tracemalloc
from functools import wraps
from inspect import getsource
from typing import Any, Callable, Dict, List, Union

from deprecated.sphinx import versionadded, versionchanged

from absfuyu.general.data_extension import ListNoDunder

# from absfuyu.logger import logger, LogLevel


# Function
###########################################################################
@versionchanged(version="3.2.0", reason="Clean up code")
def measure_performance(func: Callable) -> Callable:  # type: ignore
    r"""
    Measure performance of a function

    Parameters
    ----------
    func : Callable
        A callable function

    Returns
    -------
    Callable
        A callable function


    Usage
    -----
    Use this as a decorator (``@measure_performance``)

    Example:
    --------
    >>> @measure_performance
    >>> def test():
    ...     return 1 + 1
    >>> test()
        --------------------------------------
        Function: test
        Memory usage:		 0.000000 MB
        Peak memory usage:	 0.000000 MB
        Time elapsed (seconds):	 0.000002
        --------------------------------------
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Performance check
        tracemalloc.start()  # Start memory measure
        start_time = time.perf_counter()  # Start time measure
        output = func(*args, **kwargs)  # Run function and save result into a variable
        current, peak = tracemalloc.get_traced_memory()  # Get memory stats
        finish_time = time.perf_counter()  # Get finished time
        tracemalloc.stop()  # End memory measure

        # Print output
        print(
            f"{'-' * 38}\n"
            f"Function: {func.__name__}\n"
            f"Memory usage:\t\t {current / 10**6:,.6f} MB\n"
            f"Peak memory usage:\t {peak / 10**6:,.6f} MB\n"
            f"Time elapsed (seconds):\t {finish_time - start_time:,.6f}\n"
            f"{'-' * 38}"
        )

        # Return
        return output

    return wrapper


@versionadded(version="3.2.0")
def function_debug(func: Callable) -> Callable:  # type: ignore
    """
    Print the function signature and return value

    Parameters
    ----------
    func : Callable
        A callable function

    Returns
    -------
    Callable
        A callable function


    Usage
    -----
    Use this as a decorator (``@function_debug``)

    Example:
    --------
    >>> @function_debug
    >>> def test(a: int, b: int):
    ...     return a + b
    >>> test(6, 8)
    Calling test(6, 8)
    test() returned 14
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Get all parameters inputed
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        # Output
        print(f"Calling {func.__name__}({signature})")
        # logger.debug(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__}() returned {repr(value)}")
        # logger.debug(f"{func.__name__}() returned {repr(value)}")
        return value

    return wrapper


@versionadded(version="3.2.0")
def retry(retries: int = 3, delay: float = 1) -> Callable:  # type: ignore
    """
    Attempt to call a function, if it fails, try again with a specified delay.

    Parameters
    ----------
    retries : int
        The max amount of retries you want for the function call

    delay : int
        The delay (in seconds) between each function retry

    Returns
    -------
    Callable
        A callable function


    Usage
    -----
    Use this as a decorator (``@retry``)

    Example:
    --------
    >>> @retry(retries=3, delay=1)
    >>> def test() -> None:
    ...     time.sleep(1)
    ...     raise Exception("Function error")
    >>> test()
    Running (1): test()
    Error: Exception('Function error') -> Retrying...
    Running (2): test()
    Error: Exception('Function error') -> Retrying...
    Running (3): test()
    Error: Exception('Function error').
    "test()" failed after 3 retries.
    """

    # Condition
    if retries < 1 or delay <= 0:
        raise ValueError("retries must be >= 1, delay must be >= 0")

    def decorator(func: Callable) -> Callable:  # type: ignore
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for i in range(1, retries + 1):
                try:
                    print(f"Running ({i}): {func.__name__}()")
                    return func(*args, **kwargs)
                except Exception as e:
                    # Break out of the loop if the max amount of retries is exceeded
                    if i == retries:
                        print(f"Error: {repr(e)}.")
                        print(f'"{func.__name__}()" failed after {retries} retries.')
                        break
                    else:
                        print(f"Error: {repr(e)} -> Retrying...")
                        time.sleep(
                            delay
                        )  # Add a delay before running the next iteration

        return wrapper

    return decorator


def _deprecated_warning(func: Callable):  # type: ignore
    """
    Notice that the function is deprecated and should not be used

    Parameters
    ----------
    func : Callable
        A callable function

    Usage
    -----
    Use this as the decorator (``@deprecated_warning``)
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        print(f"[WARNING] {func.__name__}() is deprecated")
        value = func(*args, **kwargs)
        return value

    return wrapper


# Class
###########################################################################
class Checker:
    """
    Check a variable

    Parameters
    ----------
    variable : Any
        Variable that needed to check


    Example:
    --------
    >>> test = "test"
    >>> Checker(test).check()
    {'name': None, 'value': 'test', 'class': <class 'str'>, 'id': ...}
    """

    def __init__(self, variable: Any) -> None:
        self.item_to_check = variable

    def __str__(self) -> str:
        return self.item_to_check.__str__()  # type: ignore

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.item_to_check})"

    @property
    def name(self) -> Union[Any, None]:
        """``__name__`` of variable (if any)"""
        try:
            return self.item_to_check.__name__
        except:
            return None

    @property
    def value(self) -> Any:
        """Value of the variable"""
        return self.item_to_check

    @property
    def docstring(self) -> Union[str, None]:
        """``__doc__`` of variable (if any)"""
        return self.item_to_check.__doc__  # type: ignore

    @property
    def class_(self) -> Any:
        """``class()`` of variable"""
        return type(self.item_to_check)

    @property
    def id_(self) -> int:
        """``id()`` of variable"""
        return id(self.item_to_check)

    @property
    def dir_(self) -> List[str]:
        """``dir()`` of variable"""
        # return self.item_to_check.__dir__()
        return ListNoDunder(self.item_to_check.__dir__())

    @property
    def source(self) -> Union[str, None]:
        """Source code of variable (if available)"""
        try:
            return getsource(self.item_to_check)
        except:
            return None

    def check(self, full: bool = False) -> Dict[str, Any]:
        """
        Check the variable

        Parameters
        ----------
        full : bool
            | ``True``: Shows full detail
            | ``False``: Hides ``dir``, ``docstring`` and source code
            | Default: ``False``

        Returns
        -------
        dict[str, Any]
            Check result
        """
        out = {
            "name": self.name,
            "value": self.value,
            "class": self.class_,
            "id": self.id_,
        }
        if full:
            out["dir"] = self.dir_
            out["docs"] = self.docstring
            out["source"] = self.source
        return out


# Run
###########################################################################
if __name__ == "__main__":
    pass
