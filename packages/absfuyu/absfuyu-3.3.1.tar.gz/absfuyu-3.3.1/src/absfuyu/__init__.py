"""
ABSFUYU
-------
A small collection of code

LINKS
-----
- [Home page](https://pypi.org/project/absfuyu/)
- [Documentation](https://absolutewinter.github.io/absfuyu/)

USAGE
-----

Normal import: 
>>> import absfuyu
>>> help(absfuyu)

Using in cmd (`absfuyu[cli]` required): 
``$ fuyu --help``
"""


__title__ = "absfuyu"
__author__ = "AbsoluteWinter"
__license__ = "MIT License"
# __version__ = "3.4.0.dev0"
__all__ = [
    "core",
    "config",
    "everything",
    "extensions",
    "logger",
    "fun",
    "game",
    "general",
    "pkg_data",
    "sort",
    "tools",
    "util",
    "version",
]


from .version import __version__
