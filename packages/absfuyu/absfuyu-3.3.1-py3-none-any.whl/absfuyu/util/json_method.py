"""
Absfuyu: Json Method
--------------------
``.json`` file handling

Version: 1.1.3
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Module level
###########################################################################
__all__ = ["JsonFile"]


# Library
###########################################################################
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


# Function
###########################################################################
def load_json(json_file_location: Path):  # Deprecated
    """Load JSON file"""
    print("This function is deprecated as of version 3.0.0")
    with open(Path(json_file_location), "r") as json_file:
        data = json.load(json_file)
    return data


# Class
###########################################################################
class JsonFile:
    """
    ``.json`` file handling
    """

    def __init__(
        self,
        json_file_location: Union[str, Path],
        *,
        encoding: Optional[str] = "utf-8",
        indent: Union[int, str, None] = 4,
        sort_keys: bool = True,
    ) -> None:
        """
        json_file_location: json file location
        encoding: data encoding (Default: utf-8)
        indent: indentation when export to json file
        sort_keys: sort the keys before export to json file
        """
        self.json_file_location = Path(json_file_location)
        self.encoding = encoding
        self.indent = indent
        self.sort_keys = sort_keys
        self.data: Dict[Any, Any] = {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.json_file_location.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def load_json(self) -> Dict[Any, Any]:
        """
        Load ``.json`` file

        :returns: ``.json`` data
        :rtype: dict
        """
        with open(self.json_file_location, "r", encoding=self.encoding) as file:
            self.data = json.load(file)
        return self.data

    def save_json(self) -> None:
        """Save ``.json`` file"""
        json_data = json.dumps(self.data, indent=self.indent, sort_keys=self.sort_keys)
        with open(self.json_file_location, "w", encoding=self.encoding) as file:
            file.writelines(json_data)

    def update_data(self, data: Dict[Any, Any]) -> None:
        """
        Update ``.json`` data without save

        :param data: ``.json`` data
        :type data: dict
        """
        self.data = data


# Run
###########################################################################
if __name__ == "__main__":
    pass
