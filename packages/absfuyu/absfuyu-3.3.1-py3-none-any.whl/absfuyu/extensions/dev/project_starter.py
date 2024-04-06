# type: ignore
"""
Absfuyu: Project starter
------------------------

Version: 1.0.0dev1
Date updated: 01/12/2023 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = ["get_parser"]


# Library
###########################################################################
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from typing import Optional


# Function
###########################################################################
def get_parser(
    name: Optional[str] = None,
    description: Optional[str] = None,
    epilog: Optional[str] = None,
    *,
    version: str = "",
    add_help: bool = True,
) -> ArgumentParser:
    arg_parser = ArgumentParser(
        prog=name,
        description=description,
        epilog=epilog,
        add_help=add_help,
        formatter_class=ArgumentDefaultsHelpFormatter,
        # allow_abbrev=False, # Disable long options recognize
        # exit_on_error=True
    )
    arg_parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version}"
    )
    _ll_val = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    arg_parser.add_argument(
        "--log-level",
        metavar="LOG_LEVEL",
        dest="log_level",
        choices=_ll_val,
        default="INFO",
        help=f"Log level: {_ll_val}",
    )
    return arg_parser


# Run
###########################################################################
if __name__ == "__main__":
    pass
