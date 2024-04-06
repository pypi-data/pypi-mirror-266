# type: ignore
"""
Absfuyu: Beautiful
------------------
A decorator that makes output more beautiful

Version: 1.0.2
Date updated: 24/11/2023 (dd/mm/yyyy)
"""


# Module level
###########################################################################
__all__ = [
    "beautiful_output",
    "print",
    "demo",
]


# Library
###########################################################################
from functools import wraps as __wraps
from time import perf_counter as __perf
from typing import Optional as __Optional

BEAUTIFUL_MODE = False
try:
    # from rich import print
    from rich.align import Align as __Align
    from rich.console import Console as __Console
    from rich.console import Group as __Group
    from rich.panel import Panel as __Panel
    from rich.table import Table as __Table
    from rich.text import Text as __Text
except ImportError:
    from absfuyu.config import ABSFUYU_CONFIG

    if ABSFUYU_CONFIG._get_setting("auto-install-extra").value:
        __cmd: str = "python -m pip install -U absfuyu[beautiful]".split()
        from subprocess import run as __run

        __run(__cmd)
    else:
        raise SystemExit("This feature is in absfuyu[beautiful] package")
else:
    BEAUTIFUL_MODE = True


# Function
###########################################################################
def beautiful_output(
    layout_option: int = 2,
    header_visible: __Optional[bool] = True,
    footer_visible: __Optional[bool] = False,
):
    """
    Beautify function output

    Parameters
    ----------
    header_visible : True | False | None
        Show header

    footer_visible : True | False | None
        Show footer
    """

    if not BEAUTIFUL_MODE:
        raise SystemExit("This feature is in absfuyu[beautiful] package")

    def decorator(func):
        @__wraps(func)
        def wrapper(*args, **kwargs):
            # Measure performance
            start_time = __perf()
            f = func(*args, **kwargs)
            finished_time = __perf()
            elapsed = f"Time elapsed: {finished_time - start_time:,.6f} s"

            # Make header
            header_table = __Table.grid(expand=True)
            header_table.add_row(
                __Panel(
                    __Align(f"[b]Function: {func.__name__}", align="center"),
                    style="white on blue",
                ),
            )

            # Make footer
            footer_table = __Table.grid(expand=True)
            footer_table.add_row(
                __Panel(
                    __Align("[b]END PROGRAM", align="center"),
                    style="white on blue",
                ),
            )

            # Make output table
            out_table = __Table.grid(expand=True)
            out_table.add_column(ratio=2)  # result
            out_table.add_column()  # performance
            r_txt = __Text(
                str(f),
                overflow="fold",
                no_wrap=False,
                tab_size=2,
            )
            result_panel = __Panel(
                __Align(r_txt, align="center"),
                title="[bold]Result[/]",
                border_style="green",
                highlight=True,
            )
            performance_panel = __Panel(
                __Align(elapsed, align="center"),
                title="[bold]Performance[/]",
                border_style="red",
                highlight=True,
                height=result_panel.height,
            )
            out_table.add_row(
                result_panel,
                performance_panel,
            )

            # Make a blue line for no reason
            line = __Table.grid(expand=True)
            line.add_row(__Text(style="white on blue"))

            # Make layout
            header = {
                True: header_table,
                False: line,
                None: __Text(),
            }  # header[header_visible]
            footer = {
                True: footer_table,
                False: line,
                None: __Text(),
            }  # footer[footer_visible]
            layout = {
                1: __Group(header[header_visible], out_table, footer[footer_visible]),
                2: __Group(
                    header[header_visible],
                    result_panel,
                    performance_panel,
                    footer[footer_visible],
                ),
                3: __Group(result_panel),
            }
            if layout_option in layout:
                return layout[layout_option]
            else:
                return layout[2]
            # return layout[3]

        return wrapper

    return decorator


# rich's console.print wrapper
if BEAUTIFUL_MODE:
    print = __Console().print


# demo
@beautiful_output()
def __demo_decorator(x: any = None):
    code = """\
# demo
from absfuyu.extensions import beautiful as bu
@bu.beautiful_output()
def testcode():
  test = [x for x in range(100)]
  return test
bu.print(testcode())"""
    if x is None:
        x = code
    return x


def demo(x: any = None):
    print(__demo_decorator(x))


if __name__ == "__main__":
    demo()
