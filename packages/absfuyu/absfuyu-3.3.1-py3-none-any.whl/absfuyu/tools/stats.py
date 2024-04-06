"""
Absfuyu: Stats
--------------
List's stats

Version: 2.0.3
Date updated: 26/11/2023 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = [
    "ListStats"
]


# Library
###########################################################################
import math
from typing import List, Union

from absfuyu.general.data_extension import ListExt
from absfuyu.logger import logger


# Class
###########################################################################
class ListStats(List[Union[int, float]]):
    """Stats"""
    def mean(self) -> float:
        """
        Mean/Average

        Returns
        -------
        float
            Mean/Average value


        Example:
        --------
        >>> test = ListStats([1, 2, 3, 4, 5, 6])
        >>> test.mean()
        3.5
        """
        s = sum(self)
        return s/len(self)

    def median(self) -> Union[int, float]:
        """
        Median/Middle
        
        Returns
        -------
        int | float
            Median/Middle value


        Example:
        --------
        >>> test = ListStats([1, 2, 3, 4, 5, 6])
        >>> test.median()
        3.5
        """
        lst = sorted(self)
        LENGTH = len(lst)
        if LENGTH % 2 != 0:
            return lst[math.floor(LENGTH / 2)]
        else:
            num1 = lst[math.floor(LENGTH / 2) - 1]
            num2 = lst[math.floor(LENGTH / 2)]
            med = (num1 + num2) / 2
            return med

    def mode(self) -> List[Union[int, float]]:
        """
        Mode:
        
            The Mode value is the value that appears the most number of times
        
        Returns
        -------
        list[int | float]
            Mode value


        Example:
        --------
        >>> test = ListStats([1, 1, 2, 3, 4, 5, 6])
        >>> test.mode()
        [1]
        """
        lst = self
        frequency = ListExt(lst).freq()

        max_val = max(frequency.values())  # type: ignore
        keys = []

        for k, v in frequency.items():  # type: ignore
            if v == max_val:
                keys.append(k)

        return keys

    def var(self) -> float:
        """
        Variance
        
        Returns
        -------
        float
            Variance value


        Example:
        --------
        >>> test = ListStats([1, 2, 3, 4, 5, 6])
        >>> test.var()
        2.9166666666666665
        """
        lst = self
        MEAN = self.mean()
        v = [(x-MEAN)**2 for x in lst]
        out = sum(v)/len(v)
        return out

    def std(self) -> float:
        """
        Standard deviation
        
        Returns
        -------
        float
            Standard deviation value


        Example:
        --------
        >>> test = ListStats([1, 2, 3, 4, 5, 6])
        >>> test.std()
        1.707825127659933
        """
        sd = math.sqrt(self.var())
        return sd

    def percentile(self, percent: int = 50) -> Union[int, float]:
        """
        Percentile

        Parameters
        ----------
        percent : int
            Which percentile 
            (Default: ``50``)
        
        Returns
        -------
        int | float
            Percentile value


        Example:
        --------
        >>> test = ListStats([1, 2, 3, 4, 5, 6])
        >>> test.percentile()
        4
        """
        lst = self
        idx = math.floor(len(lst) / 100 * percent)
        if idx == len(lst):
            idx -= 1
        return sorted(lst)[idx]

    def summary(self):
        """
        Quick summary of data
        
        Returns
        -------
        dict
            Summary of data


        Example:
        --------
        >>> test = ListStats([1, 2, 3, 4, 5, 6])
        >>> test.summary()
        {
            'Observations': 6,
            'Mean': 3.5,
            'Median': 3.5,
            'Mode': [1, 2, 3, 4, 5, 6],
            'Standard deviation': 1.707825127659933,
            'Variance': 2.9166666666666665,
            'Max': 6,
            'Min': 1,
            'Percentiles': {'1st Quartile': 2, '2nd Quartile': 4, '3rd Quartile': 5}
        }
        """
        lst = self
        output = {
            "Observations": len(lst),
            "Mean": self.mean(),
            "Median": self.median(),
            "Mode": self.mode(),
            "Standard deviation": self.std(),
            "Variance": self.var(),
            "Max": max(lst),
            "Min": min(lst),
            "Percentiles": {
                "1st Quartile": self.percentile(25),
                "2nd Quartile": self.percentile(50),
                "3rd Quartile": self.percentile(75),
            }
        }
        return output


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
    from rich import print
    test = ListStats([1,8,9,2,3,4,4])
    print(test.summary())
