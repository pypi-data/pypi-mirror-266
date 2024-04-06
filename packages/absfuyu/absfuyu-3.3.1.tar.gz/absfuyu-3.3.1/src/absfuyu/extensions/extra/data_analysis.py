"""
Absfuyu: Data Analysis [W.I.P]
------------------------------
Extension for ``pd.DataFrame``

Version: 2.1.3
Date updated: 20/03/2024 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = [
    # Function
    "compare_2_list",
    # Support
    "CityData",
    "SplittedDF",
    "PLTFormatString",
    # Main
    "MatplotlibFormatString",
    "DataAnalystDataFrame",
    "DADF",
]


# Library
###########################################################################
import random
import string
from collections import deque
from datetime import datetime
from itertools import chain, product
from typing import Any, Dict, List, NamedTuple, Optional, Union

# import matplotlib.pyplot as plt
# from scipy import stats
# from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from deprecated import deprecated
from deprecated.sphinx import deprecated as sphinx_deprecated
from deprecated.sphinx import versionadded, versionchanged

from absfuyu.logger import logger  # type: ignore
from absfuyu.util import set_min, set_min_max


# Function
###########################################################################
@deprecated(reason="Not needed", version="3.1.0")
@sphinx_deprecated(reason="Not needed", version="3.1.0")
def summary(data: Union[list, np.ndarray]):  # del this
    """
    Quick summary of data

    :param data: np.ndarray | list
    """

    if not isinstance(data, np.ndarray):
        data = np.array(data)

    output = {
        "Observations": len(data),
        "Mean": np.mean(data),
        "Median": np.median(data),
        # "Mode": stats.mode(data)[0][0],
        "Standard deviation": np.std(data),
        "Variance": np.var(data),
        "Max": max(data),
        "Min": min(data),
        "Percentiles": {
            "1st Quartile": np.quantile(data, 0.25),
            "2nd Quartile": np.quantile(data, 0.50),
            "3rd Quartile": np.quantile(data, 0.75),
            # "IQR": stats.iqr(data),
        },
    }
    return output


def equalize_df(data: Dict[str, list], fillna=np.nan) -> Dict[str, list]:
    """
    Make all list in dict have equal length to make pd.DataFrame

    :param data: `dict` data that ready for `pd.DataFrame`
    :param fillna: Fill N/A value (Default: `np.nan`)
    """
    max_len = max(map(len, data.values()))
    for _, v in data.items():
        if len(v) < max_len:
            missings = max_len - len(v)
            for _ in range(missings):
                v.append(fillna)
    return data


## Update 05/10


def compare_2_list(*arr) -> pd.DataFrame:
    """
    Compare 2 lists then create DataFrame
    to see which items are missing

    Parameters
    ----------
    arr : list
        List

    Returns
    -------
    DataFrame
        Compare result
    """
    # Setup
    col_name = "list"
    arr = [sorted(x) for x in arr]  # type: ignore # map(sorted, arr)

    # Total array
    tarr = sorted(list(set(chain.from_iterable(arr))))
    # max_len = len(tarr)

    # Temp dataset
    temp_dict = {"base": tarr}
    for idx, x in enumerate(arr):
        name = f"{col_name}{idx}"

        # convert list
        temp = [item if item in x else np.nan for item in tarr]

        temp_dict.setdefault(name, temp)

    df = pd.DataFrame(temp_dict)
    df["Compare"] = np.where(
        df[f"{col_name}0"].apply(lambda x: str(x).lower())
        == df[f"{col_name}1"].apply(lambda x: str(x).lower()),
        df[f"{col_name}0"],  # Value when True
        np.nan,  # Value when False
    )
    return df


def rename_with_dict(df: pd.DataFrame, col: str, rename_dict: dict) -> pd.DataFrame:
    """
    Version: 2.0.0
    :param df: DataFrame
    :param col: Column name
    :param rename_dict: Rename dictionary
    """
    # Ver 1.0.1
    # name = f"{col}_filtered"
    # df[name] = df[col]
    # for k, v in rename_dict.items():
    #     df[name] = df[name].str.replace(k, v)
    # return df

    name = f"{col}_filtered"
    df[name] = df[col]
    rename_val = list(rename_dict.keys())
    df[name] = df[name].apply(lambda x: "Other" if x in rename_val else x)
    return df


# Class
###########################################################################
class CityData(NamedTuple):
    """
    Parameters
    ----------
    city : str
        City name

    region : str
        Region of the city

    area : str
        Area of the region
    """

    city: str
    region: str
    area: str

    @staticmethod
    def _sample_city_data(size: int = 100) -> List["CityData"]:
        """
        Generate sample city data (testing purpose)
        """
        sample_range = 10 ** len(str(size))

        # Serial list
        serials: List[str] = []
        while len(serials) != size:  # Unique serial
            serial = random.randint(0, sample_range - 1)
            serial = str(serial).rjust(len(str(size)), "0")  # type: ignore
            if serial not in serials:  # type: ignore
                serials.append(serial)  # type: ignore

        ss2 = deque(serials[: int(len(serials) / 2)])  # Cut half for region
        ss2.rotate(random.randrange(1, 5))
        [ss2.extend(ss2) for _ in range(2)]  # type: ignore # Extend back

        ss3 = deque(serials[: int(len(serials) / 4)])  # Cut forth for area
        ss3.rotate(random.randrange(1, 5))
        [ss3.extend(ss3) for _ in range(4)]  # type: ignore # Extend back

        serials = ["city_" + x for x in serials]
        ss2 = ["region_" + x for x in ss2]  # type: ignore
        ss3 = ["area_" + x for x in ss3]  # type: ignore

        ss = list(zip(serials, ss2, ss3))  # Zip back
        out = list(map(CityData._make, ss))

        return out


class SplittedDF(NamedTuple):
    """
    DataFrame splitted into contains
    missing values only and vice versa

    Parameters
    ----------
    df : DataFrame
        DataFrame without missing values

    df_na : DataFrame
        DataFrame with missing values only
    """

    df: pd.DataFrame
    df_na: pd.DataFrame

    @staticmethod
    def concat_df(df_list: List[pd.DataFrame], join: str = "inner"):
        """
        Concat the list of DataFrame (static method)

        Parameters
        ----------
        df_list : list[DataFrame]
            A sequence of DataFrame

        join : str
            Join type
            (Default: ``"inner"``)

        Returns
        -------
        DataFrame
            Joined DataFrame
        """
        df: pd.DataFrame = pd.concat(df_list, axis=0, join=join).reset_index()
        df.drop(columns=["index"], inplace=True)
        return df

    def concat(self, join: str = "inner"):
        """
        Concat the splitted DataFrame

        Parameters
        ----------
        join : str
            Join type
            (Default: ``"inner"``)

        Returns
        -------
        DataFrame
            Joined DataFrame
        """
        return self.concat_df(self, join=join)  # type: ignore

    @staticmethod
    def divide_dataframe(df: pd.DataFrame, by_column: str) -> List[pd.DataFrame]:
        """
        Divide DataFrame into a list of DataFrame

        Parameters
        ----------
        df : DataFrame
            DataFrame

        by_column : str
            By which column

        Returns
        -------
        list[DataFrame]
            Splitted DataFrame
        """
        divided = [x for _, x in df.groupby(by_column)]
        return divided


##
class PLTFormatString(NamedTuple):
    """Matplotlib format string"""

    marker: str
    line_style: str
    color: str


class _DictToAtrr:
    """Convert `keys` or `values` of `dict` into attribute"""

    def __init__(
        self,
        dict_data: dict,
        *,
        key_as_atrribute: bool = True,
        remove_char: str = r"( ) [ ] { }",
    ) -> None:
        """
        dict_data: Dictionary to convert
        key_as_atrribute: Use `dict.keys()` as atrribute when True, else use `dict.values()`
        remove_char: Characters that excluded from attribute name
        """
        self._data = dict_data

        if key_as_atrribute:
            # temp = list(map(self._remove_space, self._data.keys()))
            temp = [self._remove_space(x, remove_char) for x in self._data.keys()]
            [self.__setattr__(k, v) for k, v in zip(temp, self._data.values())]  # type: ignore
        else:
            temp = [self._remove_space(x, remove_char) for x in self._data.values()]
            [self.__setattr__(k, v) for k, v in zip(temp, self._data.keys())]  # type: ignore
        self._keys = temp

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._keys})"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def _remove_space(value: str, remove_char: str) -> str:
        """
        Remove special characters and replace space with underscore
        """
        remove_char = remove_char.split(" ")  # type: ignore
        logger.debug(remove_char)
        for x in remove_char:
            value = value.replace(x, "")
        value = value.replace(" ", "_")
        return value


class MatplotlibFormatString:
    """
    Format string format: `[marker][line][color]` or `[color][marker][line]`
    """

    MARKER_LIST = {
        ".": "point marker",
        ",": "pixel marker",
        "o": "circle marker",
        "v": "triangle_down marker",
        "^": "triangle_up marker",
        "<": "triangle_left marker",
        ">": "triangle_right marker",
        "1": "tri_down marker",
        "2": "tri_up marker",
        "3": "tri_left marker",
        "4": "tri_right marker",
        "8": "octagon marker",
        "s": "square marker",
        "p": "pentagon marker",
        "P": "plus (filled) marker",
        "*": "star marker",
        "h": "hexagon1 marker",
        "H": "hexagon2 marker",
        "+": "plus marker",
        "x": "x marker",
        "X": "x (filled) marker",
        "D": "diamond marker",
        "d": "thin_diamond marker",
        "|": "vline marker",
        "_": "hline marker",
    }
    LINE_STYLE_LIST = {
        "-": "solid line style",
        "--": "dashed line style",
        "-.": "dash-dot line style",
        ":": "dotted line style",
    }
    COLOR_LIST = {
        "b": "blue",
        "g": "green",
        "r": "red",
        "c": "cyan",
        "m": "magenta",
        "y": "yellow",
        "k": "black",
        "w": "white",
    }
    Marker = _DictToAtrr(MARKER_LIST, key_as_atrribute=False)
    LineStyle = _DictToAtrr(LINE_STYLE_LIST, key_as_atrribute=False)
    Color = _DictToAtrr(COLOR_LIST, key_as_atrribute=False)

    @staticmethod
    def all_format_string() -> List[PLTFormatString]:
        fmt_str = [
            __class__.MARKER_LIST,  # type: ignore
            __class__.LINE_STYLE_LIST,  # type: ignore
            __class__.COLOR_LIST,  # type: ignore
        ]
        return [PLTFormatString._make(x) for x in list(product(*fmt_str))]

    @staticmethod
    def get_random(alt: bool = False) -> str:
        temp = random.choice(__class__.all_format_string())  # type: ignore
        if alt:
            return f"{temp.marker}{temp.line_style}{temp.color}"
        else:
            return f"{temp.color}{temp.marker}{temp.line_style}"


# Class - DA
###########################################################################
class DataAnalystDataFrame(pd.DataFrame):
    """
    Data Analyst ``pd.DataFrame``
    """

    # Support
    # ================================================================
    # Rearrange column
    def rearrange_column(self, insert_to_col: str, num_of_cols: int = 1):
        """
        Move right-most columns to selected position

        Parameters
        ----------
        insert_to_col : str
            Name of the column that the right-most column will be moved next to

        num_of_cols : int
            Number of columns moved

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        cols = self.columns.to_list()  # List of columns
        num_of_cols = int(set_min_max(num_of_cols, min_value=1, max_value=len(cols)))
        col_index = cols.index(insert_to_col)
        cols = (
            cols[: col_index + 1]
            + cols[-num_of_cols:]
            + cols[col_index + 1 : len(cols) - num_of_cols]
        )
        self = self.__class__(self[cols])
        return self

    # Drop a list of column
    def drop_columns(self, columns: List[str]):
        """
        Drop columns in DataFrame

        Parameters
        ----------
        columns : list[str]
            List of columns need to drop

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        for column in columns:
            try:
                self.drop(columns=[column], inplace=True)
            except:
                logger.debug(f"{column} column does not exist")
                # pass
        return self

    # Drop right-most columns
    def drop_rightmost(self, num_of_cols: int = 1):
        """
        Drop ``num_of_cols`` right-most columns

        Parameters
        ----------
        num_of_cols : int
            Number of columns to drop

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        # Restrain
        # if num_of_cols < 1:
        #     num_of_cols = 1
        # if num_of_cols > self.shape[1]:
        #     num_of_cols = self.shape[1]
        num_of_cols = int(
            set_min_max(num_of_cols, min_value=1, max_value=self.shape[1])
        )

        # Logic
        for _ in range(num_of_cols):
            self.drop(self.columns[len(self.columns) - 1], axis=1, inplace=True)
        return self

    # Add blank column
    def add_blank_column(self, column_name: str, fill: Any):
        """
        Add a blank column

        Parameters
        ----------
        column_name : str
            Name of the column to add

        fill : Any
            Fill the column with data

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        self[column_name] = [fill] * self.shape[0]
        return self

    # Modify
    # ================================================================
    # Convert city
    def convert_city(
        self,
        city_column: str,
        city_list: List[CityData],
        *,
        mode: str = "ra",
    ):
        """
        Get ``region`` and ``area`` of a city

        Parameters
        ----------
        city_column : str
            Column contains city data

        city_list : list[CityData]
            List of city in correct format
            (Default: ``None``)

        mode : str
            | Detailed column to add
            | ``r``: region
            | ``a``: area
            | (Default: ``"ra"``)

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """

        # Support function
        def _convert_city_support(value: str) -> CityData:
            for x in city_list:
                if x.city.lower().startswith(value.lower()):
                    return x
            return CityData(city=value, region=np.nan, area=np.nan)  # type: ignore

        # Convert
        col_counter = 0
        if mode.find("r") != -1:
            logger.debug("Mode: 'region'")
            self["region"] = self[city_column].apply(
                lambda x: _convert_city_support(x).region
            )
            col_counter += 1
        if mode.find("a") != -1:
            logger.debug("Mode: 'area'")
            self["area"] = self[city_column].apply(
                lambda x: _convert_city_support(x).area
            )
            col_counter += 1

        # Rearrange
        return self.rearrange_column(city_column, col_counter)

    # Date related
    def add_date_from_month(self, month_column: str, *, col_name: str = "date"):
        """
        Add dummy ``date`` column from ``month`` column

        Parameters
        ----------
        month_column : str
            Month column

        col_name : str
            New date column name
            (Default: ``"date"``)

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        _this_year = datetime.now().year
        self[col_name] = pd.to_datetime(
            f"{_this_year}-" + self[month_column].astype(int).astype(str) + "-1",
            format="%Y-%m-%d",
        )
        # Rearrange
        return self.rearrange_column(month_column)

    def add_detail_date(self, date_column: str, mode: str = "dwmy"):
        """
        Add these columns from ``date_column``:
            - ``date`` (won't add if ``date_column`` value is ``"date"``)
            - ``day`` (overwrite if already exist)
            - ``week`` (overwrite if already exist)
            - ``month`` (overwrite if already exist)
            - ``year``  (overwrite if already exist)

        Parameters
        ----------
        date_column : str
            Date column

        mode : str
            | Detailed column to add
            | ``d``: day
            | ``w``: week number
            | ``m``: month
            | ``y``: year
            | (Default: ``"dwmy"``)

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        # Convert to datetime
        self["date"] = pd.to_datetime(self[date_column])

        # Logic
        col_counter = 0
        # self["weekday"] = self["day"].dt.isocalendar().day # Weekday
        if mode.find("d") != -1:
            logger.debug("Mode: 'day'")
            self["day"] = self["date"].dt.day
            col_counter += 1
        if mode.find("w") != -1:
            logger.debug("Mode: 'weekday'")
            self["week"] = self["date"].dt.isocalendar().week
            col_counter += 1
        if mode.find("m") != -1:
            logger.debug("Mode: 'month'")
            self["month"] = self["date"].dt.month
            col_counter += 1
        if mode.find("y") != -1:
            logger.debug("Mode: 'year'")
            self["year"] = self["date"].dt.year
            col_counter += 1

        # Return
        return self.rearrange_column(date_column, col_counter)

    def delta_date(
        self, date_column: str, mode: str = "now", *, col_name: str = "delta_date"
    ):
        """
        Calculate date interval

        Parameters
        ----------
        date_column : str
            Date column

        mode : str
            | Mode to calculate
            | ``"between_row"``: Calculate date interval between each row
            | ``"now"``: Calculate date interval to current date
            | (Default: ``"between_row"``)

        col_name : str
            | New delta date column name
            | (Default: ``"delta_date"``)

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        if mode.lower().startswith("between_row"):
            dated = self[date_column].to_list()
            cal = []
            for i in range(len(dated)):
                if i == 0:
                    cal.append(dated[i] - dated[i])
                    # cal.append(relativedelta(dated[i], dated[i]))
                else:
                    cal.append(dated[i] - dated[i - 1])
                    # cal.append(relativedelta(dated[i], dated[i - 1]))
            self[col_name] = [x.days for x in cal]
            return self
        else:  # mode="now"
            self[col_name] = self[date_column].apply(
                lambda x: (datetime.now() - x).days
            )
            return self

    # Fill missing value
    def fill_missing_values(
        self, column_name: str, fill: Any = np.nan, *, fill_when_not_exist: Any = np.nan
    ):
        """
        Fill missing values in specified column

        Parameters
        ----------
        column_name : str
            Column name

        fill : Any
            Fill the missing values with
            (Default: ``np.nan``)

        fill_when_not_exist : Any
            When ``column_name`` does not exist,
            create a new column and fill with ``fill_when_not_exist``
            (Default: ``np.nan``)

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        try:
            self[column_name] = self[column_name].fillna(fill)
        except:
            self.add_blank_column(column_name, fill_when_not_exist)
        return self

    # Split DataFrame
    def split_na(self, by_column: str) -> SplittedDF:
        """
        Split DataFrame into 2 parts:
            - Without missing value in specified column
            - With missing value in specified column

        Parameters
        ----------
        by_column : str
            Split by column

        Returns
        -------
        SplittedDF
            Splitted DataFrame
        """
        out = SplittedDF(
            df=self[~self[by_column].isna()],  # DF
            df_na=self[self[by_column].isna()],  # DF w/o NA
        )
        return out

    # Threshold filter
    # @versionchanged(version="3.2.0", reason="Optimized the code")
    def threshold_filter(
        self,
        destination_column: str,
        threshold: Union[int, float] = 10,
        *,
        top: Optional[int] = None,
        replace_with: Any = "Other",
    ):
        """
        Filter out percentage of data that smaller than the ``threshold``,
        replace all of the smaller data to ``replace_with``.
        As a result, pie chart is less messy.

        Parameters
        ----------
        destination_column : str
            Column to be filtered

        threshold : int | float
            Which percentage to cut-off
            (Default: 10%)

        top : int
            Only show top ``x`` categories in pie chart
            (replace threshold mode)
            (Default: ``None``)

        replace_with : Any
            Replace all of the smaller data with specified value

        Returns
        -------
        DataAnalystDataFrame
            Modified DataFrame
        """
        # Clean
        try:
            self[destination_column] = self[
                destination_column
            ].str.strip()  # Remove trailing space
        except:
            pass

        # Logic
        col_df = self.show_distribution(destination_column)

        # Rename
        if top is not None:
            list_of_keep: list = (
                col_df[destination_column]
                .head(set_min_max(top - 1, min_value=1, max_value=col_df.shape[0]))
                .to_list()
            )
            # logger.debug(list_of_keep)
        else:
            list_of_keep = col_df[col_df["percentage"] >= threshold][
                destination_column
            ].to_list()  # values that will not be renamed
        self[f"{destination_column}_filtered"] = self[destination_column].apply(
            lambda x: replace_with if x not in list_of_keep else x
        )

        # Return
        return self

    # Info
    # ================================================================
    # Total observation
    @property
    @versionadded(version="3.2.0")
    def total_observation(self) -> int:
        """Returns total observation of the DataFrame"""
        return self.shape[0] * self.shape[1]  # type: ignore

    # Quick info
    @versionadded(version="3.2.0")
    def qinfo(self) -> str:
        """
        Show quick infomation about DataFrame
        """
        mv = self.isnull().sum().sum()  # missing values
        to = self.total_observation
        info = (
            f"Dataset Information:\n"
            f"- Number of Rows: {self.shape[0]:,}\n"
            f"- Number of Columns: {self.shape[1]:,}\n"
            f"- Total observation: {to:,}\n"
            f"- Missing value: {mv:,} ({(mv / to * 100):.2f}%)\n\n"
            f"Column names:\n{self.columns.to_list()}"
        )
        return info

    # Quick describe
    @versionadded(version="3.2.0")
    def qdescribe(self) -> pd.DataFrame:
        """
        Quick ``describe()`` that exclude ``object`` and ``datetime`` dtype
        """
        return self[
            self.select_dtypes(exclude=["object", "datetime"]).columns
        ].describe()

    # Missing values analyze
    def get_missing_values(
        self, hightlight: bool = True, *, percentage_round_up: int = 2
    ) -> pd.DataFrame:
        """
        Get a DataFrame contains count of missing values for each column

        Parameters
        ----------
        hightlight : bool
            Shows only columns with missing values when ``True``
            (Default: ``True``)

        percentage_round_up : int
            Round up to which decimals
            (Default: ``2``)

        Returns
        -------
        DataFrame
            Missing value DataFrame
        """
        # Check for missing value
        df_na = self.isnull().sum().sort_values(ascending=False)
        if hightlight:
            out = df_na[df_na != 0].to_frame()
        else:
            out = df_na.to_frame()
        out.rename(columns={0: "Num of N/A"}, inplace=True)
        out["Percentage"] = (out["Num of N/A"] / self.shape[0] * 100).round(
            percentage_round_up
        )

        # logger.debug(
        #     f"Percentage of N/A over entire DF: "
        #     f"{(self.isnull().sum().sum() / (self.shape[0] * self.shape[1]) * 100).round(percentage_round_up)}%"
        # )
        return out

    # Show distribution
    @versionadded(version="3.2.0")
    def show_distribution(
        self,
        column_name: str,
        dropna: bool = True,
        *,
        show_percentage: bool = True,
        percentage_round_up: int = 2,
    ) -> pd.DataFrame:
        """
        Show distribution of a column

        Parameters
        ----------
        column_name : str
            Column to show distribution

        dropna : bool
            Count N/A when ``False``
            (Default: ``True``)

        show_percentage : bool
            Show proportion in range 0% - 100% instead of [0, 1]
            (Default: ``True``)

        percentage_round_up : int
            Round up to which decimals
            (Default: ``2``)

        Returns
        -------
        DataFrame
            Distribution DataFrame


        Example:
        --------
        >>> DataAnalystDataFrame.sample_df().show_distribution("number_range")
          number_range  count  percentage
        0          900     16        16.0
        1          700     15        15.0
        2          300     12        12.0
        3          200     12        12.0
        4          400     11        11.0
        5          600     11        11.0
        6          800     10        10.0
        7          100      9         9.0
        8          500      4         4.0
        """
        out = self[column_name].value_counts(dropna=dropna).to_frame().reset_index()
        if show_percentage:
            out["percentage"] = (out["count"] / self.shape[0] * 100).round(
                percentage_round_up
            )
        else:
            out["percentage"] = (out["count"] / self.shape[0]).round(
                percentage_round_up
            )
        return out

    # Help
    @staticmethod
    def dadf_help() -> List[str]:
        """
        Show all available method of DataAnalystDataFrame
        """
        list_of_method = list(set(dir(__class__)) - set(dir(pd.DataFrame)))  # type: ignore
        return sorted(list_of_method)

    # Sample DataFrame
    @classmethod
    def sample_df(cls, size: int = 100):
        """
        Create sample DataFrame

        Parameters
        ----------
        size : int
            Number of observations
            (Default: ``100``)

        Returns
        -------
        DataAnalystDataFrame
            DataFrame with these columns:
            [number, number_big, number_range, missing_value, text, date]


        Example:
        --------
        >>> DataAnalystDataFrame.sample_df()
              number  number_big number_range  missing_value      text       date
        0  -2.089770         785          700            NaN  vwnlqoql 2013-11-20
        1  -0.526689         182          100           24.0  prjjcvqc 2007-04-13
        2  -1.596514         909          900            8.0  cbcpzlac 2023-05-24
        3   2.982191         989          900           21.0  ivwqwuvd 2022-04-28
        4   1.687803         878          800            NaN  aajtncum 2005-10-05
        ..       ...         ...          ...            ...       ...        ...
        95 -1.295145         968          900           16.0  mgqunkhi 2016-04-12
        96  1.296795         255          200            NaN  lwvytego 2014-05-10
        97  1.440746         297          200            5.0  lqsoykun 2010-04-03
        98  0.327702         845          800            NaN  leadkvsy 2005-08-05
        99  0.556720         981          900           36.0  bozmxixy 2004-02-22
        [100 rows x 6 columns]
        """
        # Restrain
        size = int(set_min(size, min_value=1))

        # Number col
        df = pd.DataFrame(np.random.randn(size, 1), columns=["number"])
        df["number_big"] = [
            random.choice(range(100, 999)) for _ in range(size)
        ]  # Big number in range 100-999
        df["number_range"] = df["number_big"].apply(lambda x: str(x)[0] + "00")

        # Missing value col
        na_rate = random.randint(1, 99)
        d = [random.randint(1, 99) for _ in range(size)]
        df["missing_value"] = list(map(lambda x: x if x < na_rate else np.nan, d))
        # df["missing_value"] = [random.choice([random.randint(1, 99), np.nan]) for _ in range(observations)]

        # Text col
        df["text"] = [
            "".join([random.choice(string.ascii_lowercase) for _ in range(8)])
            for _ in range(size)
        ]

        # Random date col
        df["date"] = [
            datetime(
                year=random.randint(datetime.now().year - 20, datetime.now().year),
                month=random.randint(1, 12),
                day=random.randint(1, 28),
            )
            for _ in range(size)
        ]

        # Return
        return cls(df)


class DADF(DataAnalystDataFrame):
    """Short name for ``DataAnalystDataFrame``"""

    pass


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
