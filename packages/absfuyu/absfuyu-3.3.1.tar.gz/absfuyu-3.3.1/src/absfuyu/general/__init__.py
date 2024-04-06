"""
Absfuyu: General
----------------
Collection of useful classes

Version: 1.1.4
Date updated: 15/03/2024 (dd/mm/yyyy)

Features:
---------
- content
- data_extension
- generator
- human
"""

# Libary
###########################################################################
from typing import Any, Dict, Optional

from absfuyu.general import content, data_extension, generator, human


# Class
###########################################################################
class Dummy:
    """
    Dummy class that has nothing

    Update attribute through dict
    """

    def __init__(self, data: Optional[Dict[Any, Any]] = None) -> None:
        try:
            self.__dict__.update(data)  # type: ignore
        except:
            pass

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.__dict__})"

    def __repr__(self) -> str:
        return self.__str__()

    def dir_(self):
        """List ``property``"""
        return [x for x in self.__dir__() if not x.startswith("_")]

    def update(self, data: Dict[Any, Any]) -> None:
        """
        Update with dict data

        :param data: Dict data
        :type data: dict
        """
        self.__dict__.update(data)


class ClassBase:
    """Class base for other class"""

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._get_key_and_val_for_print()})"

    def __repr__(self) -> str:
        return self.__str__()

    def _get_key_and_val_for_print(self, sep: str = ", ") -> str:
        """
        returns `self.__dict__` without `{}` symbol

        Example:
        Convert `"a": "b"` to `a=b`
        """
        keys = self.__dict__.keys()
        temp = filter(lambda x: not x.startswith("_"), keys)
        # out = [f"{x}={self.__dict__[x]}" for x in temp]
        out = [f"{x}={self.__dict__.get(x)}" for x in temp]
        return sep.join(out)

    # def _get_new_available_method(self) -> List[str]:
    #     """
    #     Return all new available methods in this particular class
    #     """
    #     available = set(dir(self.__class__)).difference(set(dir(self.__class__.__base__)))
    #     return sorted(list(available))


# Run
###########################################################################
if __name__ == "__main__":
    pass
