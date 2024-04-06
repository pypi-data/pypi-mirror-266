# type: ignore
"""
Absfuyu: Shutdownizer
---------------------
This shutdowns

Version: 1.0.0dev
Date updated: 27/11/2023 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = ["ShutDownizer"]


# Library
###########################################################################
import datetime
import os
import random
import subprocess
import sys
from pathlib import Path

from absfuyu.logger import LogLevel, logger


# Class
###########################################################################
class Dummy:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()


class ShutDownizer(Dummy):
    """
    ShutDownizer

    Shutdown tool because why not
    """

    def __init__(self) -> None:
        """doc_string"""
        self.os: str = sys.platform
        logger.debug(f"Current OS: {self.os}")

        if self.os in ["win32", "cygwin"]:  # Windows
            self.engine = ShutDownizerWin()
        elif self.os == "darwin":  # MacOS
            self.engine = ShutDownizerMac()
        elif self.os == "linux":  # Linux
            self.engine = ShutDownizerLinux()
        else:  # Other (probably linux)
            self.engine = ShutDownizerLinux()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.os})"

    def shutdown(self):
        """Shutdown"""
        self.engine.shutdown()

    def restart(self):
        """Restart"""
        self.engine.restart()

    def cancel(self):
        """Cancel"""
        self.engine.cancel()


class ShutDownizerEngine(Dummy):
    """
    Abstract class for different type of OS
    """

    def __init__(self) -> None:
        self.shutdown_cmd = ""
        self.restart_cmd = ""
        self.cancel_cmd = ""

    def _excute_cmd(self, cmd) -> None:
        """Execute the cmd"""
        try:
            if isinstance(cmd, str):
                subprocess.run(cmd.split())
            elif isinstance(cmd, list):
                subprocess.run(cmd)
            else:
                logger.error(f'"{cmd}" failed to run')
        except:
            logger.error(f'"{cmd}" failed to run')

    def shutdown(self):
        """Shutdown"""
        try:
            self._excute_cmd(self.shutdown_cmd)
        except:
            pass

    def restart(self):
        """Restart"""
        self._excute_cmd(self.restart_cmd)

    def cancel(self):
        """Cancel shutdown/restart"""
        self._excute_cmd(self.cancel_cmd)


class ShutDownizerWin(ShutDownizerEngine):
    """ShutDownizer - Windows"""

    def __init__(self) -> None:
        self.shutdown_cmd = "shutdown -f -s -t 0"
        self.cancel_cmd = "shutdown -a"

    def _punish(self):
        """Create a `batch` script that shut down computer when boot up"""
        try:
            startup_folder_win = Path(os.getenv("appdata")).joinpath(
                "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
            )
            with open(startup_folder_win.joinpath("system.bat"), "w") as f:
                f.write(self.shutdown_cmd)
        except:
            logger.error("Cannot write file to startup folder")


class ShutDownizerMac(ShutDownizerEngine):
    """ShutDownizer - MacOS"""

    def __init__(self) -> None:
        self.shutdown_cmd = ["osascript", "-e", 'tell app "System Events" to shut down']


class ShutDownizerLinux(ShutDownizerEngine):
    """ShutDownizer - Linux"""

    def __init__(self) -> None:
        self.shutdown_cmd = "shutdown -h now"


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(LogLevel.DEBUG)
    test = ShutDownizer()
    print(ShutDownizerLinux().shutdown())
