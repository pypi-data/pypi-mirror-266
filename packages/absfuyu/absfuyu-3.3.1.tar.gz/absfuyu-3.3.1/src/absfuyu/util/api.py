"""
Absufyu: API
------------
Fetch data stuff

Version: 1.2.0
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Module level
###########################################################################
__all__ = [
    "APIRequest",
    "ping_windows",
]


# Library
###########################################################################
import json
import re
import subprocess
from pathlib import Path
from typing import List, NamedTuple, Optional, Union

import requests
from deprecated.sphinx import versionchanged

from absfuyu.logger import logger


# Function
###########################################################################
class PingResult(NamedTuple):
    """
    :param host: Host name/IP
    :param result: Ping result in ms
    """

    host: str
    result: str


@versionchanged(version="3.4.0", reason="Change function's return")
def ping_windows(host: List[str], ping_count: int = 3) -> List[PingResult]:
    """
    Ping web

    Parameters
    ----------
    host : list[str]
        List of host to ping

    ping_count : int
        Number of time to ping to take average
        (Default: ``3``)

    Returns
    -------
    list
        List of host with pinged value


    Example:
    --------
    >>> ping_windows(["1.1.1.1", "google.com"])
    ['1.1.1.1 : xxms', 'google.com : xxms']
    """
    out: List[PingResult] = []

    for ip in host:
        output = subprocess.run(
            f"ping {ip.strip()} -n {ping_count}",
            encoding="utf-8",
            capture_output=True,
            text=True,
        )
        logger.debug(output)

        data: str = "".join(output.stdout)
        res = re.findall(r"Average = (.*)", data)
        if res:
            out.append(PingResult(ip, res[0]))
        else:
            out.append(PingResult(ip, "FAILED"))

    return out


# Class
###########################################################################
class APIRequest:
    """API data with cache feature"""

    def __init__(
        self,
        api_url: str,
        *,  # Use "*" to force using keyword in function parameter | Example: APIRequest(url, encoding="utf-8")
        encoding: Optional[str] = "utf-8",
    ) -> None:
        """
        :param api_url: api link
        :param encoding: data encoding (Default: utf-8)
        """
        self.url = api_url
        self.encoding = encoding

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.url})"

    def __repr__(self) -> str:
        return self.__str__()

    def fetch_data(self, *, update: bool = False, json_cache: Union[str, Path]):
        """
        Fetch data from an API then cache it for later use

        Parameters
        ----------
        update :
            Refresh the cache when ``True``
            (Default: ``False``)

        json_cache : Path | str
            Name of the cache

        Returns
        -------
        Any
           Data

        None
            No data fetched/unable to fetch data
        """
        if update:
            json_data = None
        else:
            try:
                with open(json_cache, "r", encoding=self.encoding) as file:
                    json_data = json.load(file)
                    logger.debug("Fetched data from local cache!")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.debug(f"No local cache found... ({e})")
                json_data = None

        if not json_data:
            logger.debug("Fetching new json data... (Creating local cache)")
            try:
                json_data = requests.get(self.url).json()
                with open(json_cache, "w", encoding=self.encoding) as file:
                    json.dump(json_data, file, indent=2)
            except FileNotFoundError as e:
                logger.error(f"Can't create cache due to Path error - {e}")

        return json_data

    def fetch_data_only(self) -> requests.Response:
        """
        Fetch data without cache

        Returns
        -------
        Response
            ``requests.Response``
        """
        return requests.get(self.url)


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
