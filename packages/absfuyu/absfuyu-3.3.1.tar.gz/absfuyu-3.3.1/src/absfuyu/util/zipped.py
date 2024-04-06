"""
Absfuyu: Zipped
---------------
Zipping stuff

Version: 1.0.1
Date updated: 24/11/2023 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = [
    "Zipper"
]


# Library
###########################################################################
import shutil
import zipfile
from pathlib import Path
from typing import Union

from absfuyu.logger import logger


###########################################################################
class Zipper:
    """Zip file or folder"""
    def __init__(
            self,
            path_to_zip: Union[str, Path],
            name: Union[str, None] = None
        ) -> None:
        """
        path_to_zip: source location
        name: zipped file name
        """
        self.source_path = Path(path_to_zip)
        if name is None:
            self.name = self.source_path.name + ".zip"
        else:
            self.name = name
        self.destination = self.source_path.parent.joinpath(self.name)
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    def __repr__(self) -> str:
        return self.__str__()
    
    def zip_stuff(self, delete_after_zip: bool = False) -> None:
        """
        Zip file/folder

        :param delete_after_zip: Delete source after zip (Default: ``False``)
        :type delete_after_zip: bool
        """

        # Zip
        logger.debug(f"Zipping...")
        if self.source_path.is_dir(): # zip entire folder
            try:
                with zipfile.ZipFile(self.destination, "w", zipfile.ZIP_DEFLATED) as f:
                    for file in self.source_path.rglob("*"):
                        f.write(file, file.relative_to(self.source_path))
            except:
                logger.error("Zip failed!")
                # shutil.make_archive(zip_file, format="zip", root_dir=zip_path) # Method 2
        else: # zip a file
            # Implement later
            pass

        # Delete folder
        if delete_after_zip:
            try:
                logger.debug(f"Deleting unused folder...")
                shutil.rmtree(self.source_path)
                logger.debug(f"Files deleted")
            except OSError as e:
                logger.error(f"Error: {e.filename} - {e.strerror}.")


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
