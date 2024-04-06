"""
Test: Everything

Version: 1.1.20
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Library
###########################################################################
import pytest

from absfuyu import everything as ab
from absfuyu.config import (
    _SPACE_REPLACE,
    ABSFUYU_CONFIG,
    Config,
    ConfigFormat,
    Setting,
    SettingDictFormat,
    VersionDictFormat,
)

# --- Loading test --------------------------------------------------------
# from absfuyu.core import *
from absfuyu.core import (
    CONFIG_PATH,
    CORE_PATH,
    DATA_PATH,
    CLITextColor,
    Color,
    ModuleList,
    ModulePackage,
)
from absfuyu.extensions import *
from absfuyu.extensions.beautiful import beautiful_output, demo  # Has rich
from absfuyu.extensions.extra import *
from absfuyu.extensions.extra.data_analysis import (  # Has pandas, numpy
    CityData,
    DataAnalystDataFrame,
    MatplotlibFormatString,
    PLTFormatString,
    SplittedDF,
    _DictToAtrr,
    compare_2_list,
    equalize_df,
    rename_with_dict,
    summary,
)
from absfuyu.fun import force_shutdown, happy_new_year, im_bored, zodiac_sign
from absfuyu.fun.tarot import Tarot, TarotCard
from absfuyu.fun.WGS import WGS
from absfuyu.game import game_escapeLoop, game_RockPaperScissors
from absfuyu.game.sudoku import Sudoku
from absfuyu.game.tictactoe import *
from absfuyu.game.wordle import Wordle  # Has requests

# --- Sub-package ---
from absfuyu.general import ClassBase, Dummy
from absfuyu.general.content import (  # Has unidecode
    Content,
    ContentLoader,
    LoadedContent,
)
from absfuyu.general.data_extension import DictExt, IntNumber, ListExt, Text
from absfuyu.general.generator import Charset, Generator
from absfuyu.general.human import BloodType, Human, Person  # Has python-dateutil

# from absfuyu.logger import *
from absfuyu.logger import LogLevel, compress_for_log, logger
from absfuyu.pkg_data import PACKAGE_DATA, DataList, PkgData
from absfuyu.sort import (
    alphabetAppear,
    binary_search,
    insertion_sort,
    linear_search,
    selection_sort,
)
from absfuyu.tools import *
from absfuyu.tools.converter import (
    Base64EncodeDecode,
    ChemistryElement,
    Str2Pixel,
    Text2Chemistry,
)
from absfuyu.tools.keygen import Keygen
from absfuyu.tools.obfuscator import Obfuscator, ObfuscatorLibraryList
from absfuyu.tools.stats import ListStats
from absfuyu.tools.web import gen_random_commit_msg, soup_link  # Has bs4, requests
from absfuyu.util import (
    get_installed_package,
    set_max,
    set_min,
    set_min_max,
    stop_after_day,
)
from absfuyu.util.api import APIRequest, ping_windows  # Has requests
from absfuyu.util.json_method import JsonFile
from absfuyu.util.lunar import LunarCalendar
from absfuyu.util.path import Directory, SaveFileAs
from absfuyu.util.performance import Checker, function_debug, measure_performance, retry
from absfuyu.util.pkl import Pickler
from absfuyu.util.zipped import Zipper
from absfuyu.version import (
    Bumper,
    PkgVersion,
    ReleaseLevel,
    ReleaseOption,
    Version,
    __version__,
    _AbsfuyuPackage,
)

# Test
###########################################################################
# def test_ev():
#     assert ab.__IS_EVERYTHING is True

def test_everything():
    assert True
