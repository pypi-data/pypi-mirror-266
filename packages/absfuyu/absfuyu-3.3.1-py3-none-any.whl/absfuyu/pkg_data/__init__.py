"""
Absfuyu: Package data
---------------------
Load package data

Version: 2.2.2
Date updated: 30/11/2023 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = [
    "PkgData"
]


# Library
###########################################################################
from ast import literal_eval
from importlib.resources import read_binary
from pathlib import Path
from typing import List, Union
import zlib
import sys

if sys.version_info.minor >= 10:
    from importlib.resources import files
else:
    try:
        from importlib_resources import files
    except:
        raise ImportError("Please install importlib-resources")

from absfuyu.core import DATA_PATH
from absfuyu.logger import logger


# External Data
###########################################################################
_EXTERNAL_DATA = {
    "chemistry.json": "https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json",
    "countries.json": "https://github.com/dr5hn/countries-states-cities-database/blob/master/countries.json",
    "tarot.json": "https://raw.githubusercontent.com/dariusk/corpora/master/data/divination/tarot_interpretations.json",
    "word_list.json": "https://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json",
}


# Class
###########################################################################
class DataList:
    CHEMISTRY = files("absfuyu.pkg_data").joinpath("chemistry.pkl")
    TAROT = files("absfuyu.pkg_data").joinpath("tarot.pkl")


class PkgData:
    """Package data maker/loader"""
    def __init__(self, data_name: str) -> None:
        self.name = data_name
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    def __repr__(self) -> str:
        return self.__str__()
    
    def _make_dat(self, data: str, name: Union[str, Path]):
        """
        data: string data
        name: name and location of the data
        """
        compressed_data = zlib.compress(str(data).encode(), zlib.Z_BEST_COMPRESSION)
        with open(name, "wb") as file:
            file.write(compressed_data)
    
    def load_dat_data(self, evaluate: bool = False):
        """
        Load ``.dat`` data from package resource
        
        :param evaluate: use ``ast.literal_eval()`` to evaluate string data
        :type evaluate: bool
        :returns: Loaded data
        :rtype: Any
        """
        compressed_data = read_binary("absfuyu.pkg_data", self.name)
        data = zlib.decompress(compressed_data).decode()
        # return data
        return literal_eval(data) if evaluate else data

    def update_data(self, new_data: str):
        """
        Update existing data

        :param new_data: Data to be updated
        """
        self._make_dat(data=new_data, name=DATA_PATH.joinpath(self.name))
        logger.debug("Data updated")


class _ManagePkgData:
    """Manage this package data"""
    def __init__(self, pkg_data_loc: Union[str, Path]) -> None:
        """
        pkg_data_loc: Package data location
        """
        self.data_loc = Path(pkg_data_loc)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.data_loc.name})"
    def __repr__(self) -> str:
        return self.__str__()
    
    def get_data_list(self, *, pattern: str = "*") -> List[Path]:
        """Get a list of data available"""
        excludes = [x for x in self.data_loc.glob("*.[pP][yY]")] # exclude python scripts
        return [x for x in self.data_loc.glob(pattern) if x not in excludes and x.is_file()]
    
    @property
    def data_list(self) -> List[str]:
        """List of available data"""
        return [x.name for x in self.get_data_list()]
    
    def download_all_data(self):
        """
        Download all external data
        """
        
        logger.debug("Downloading data...")
        try:
            from absfuyu.util.api import APIRequest
            
            for data_name, data_link in _EXTERNAL_DATA.items():
                logger.debug(f"Downloading {data_name}...")
                data = APIRequest(data_link, encoding="utf-8")
                data.fetch_data(update=True, json_cache=DATA_PATH.joinpath(data_name))
                logger.debug(f"Downloading {data_name}...DONE")
            logger.debug("Downloading data...DONE")
        except:
            logger.debug("Downloading data...FAILED")
    
    def clear_data(self) -> None:
        """Clear data in data list"""
        for x in self.get_data_list():
            x.unlink()


PACKAGE_DATA = _ManagePkgData(DATA_PATH)


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
