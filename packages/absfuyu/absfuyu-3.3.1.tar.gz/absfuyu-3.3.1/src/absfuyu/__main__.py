"""
ABSFUYU
---
COMMAND LINE INTERFACE

Version: 2.0.2
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Library
###########################################################################
import subprocess
from random import choice as __randc

import click
import colorama

from absfuyu import core as __core
from absfuyu import version as __v
from absfuyu.config import ABSFUYU_CONFIG
from absfuyu.game import game_escapeLoop, game_RockPaperScissors  # type: ignore
from absfuyu.game.tictactoe import game_tictactoe  # type: ignore

# Color stuff
###########################################################################
colorama.init(autoreset=True)
__COLOR = __core.Color


# Main group
###########################################################################
@click.command()
def welcome():
    """Welcome message"""
    import os as __os

    try:
        user = __os.getlogin()
    except:
        import getpass

        user = getpass.getuser()
    welcome_msg = f"{__COLOR['green']}Welcome {__COLOR['red']}{user} {__COLOR['green']}to {__COLOR['blue']}absfuyu's cli"
    click.echo(
        f"""
        {__COLOR['reset']}{'='*(len(welcome_msg)-20)}
        {welcome_msg}
        {__COLOR['reset']}{'='*(len(welcome_msg)-20)}
    """
    )
    ABSFUYU_CONFIG.welcome()


@click.command()
@click.argument("name")
def greet(name):
    """Greet"""
    click.echo(f"{__COLOR['yellow']}Hello {name}")


@click.command()
@click.option(
    "--setting",
    "-s",
    type=click.Choice(["luckgod", "install-extra"]),
    help="Toggle on/off selected setting",
)
def toggle(setting: str):
    """Toggle on/off setting"""

    # Dictionary
    trans = {
        "luckgod": "luckgod-mode",
        "install-extra": "auto-install-extra",
    }  # trans[setting]

    if setting is None:
        click.echo(f"{__COLOR['red']}Invalid setting")  # type: ignore
    else:
        ABSFUYU_CONFIG.toggle_setting(trans[setting])
        out = ABSFUYU_CONFIG._get_setting(trans[setting])
        click.echo(f"{__COLOR['red']}{out}")
    pass


@click.command()
def version():
    """Check current version"""
    click.echo(f"{__COLOR['green']}absfuyu: {__v.__version__}")


# Do group
###########################################################################
@click.command()
@click.option(
    "--force_update/--no-force-update",
    "-F/-f",
    "force_update",
    type=bool,
    default=True,
    show_default=True,
    help="Update the package",
)
def update(force_update: bool):
    """Update the package to latest version"""
    click.echo(__COLOR["green"])
    __v._AbsfuyuPackage.check_for_update(force_update=force_update)


@click.command()
def reset():
    """Reset config to default value"""
    ABSFUYU_CONFIG.reset_config()
    click.echo(f"{__COLOR['green']}All settings have been reseted")


@click.command()
@click.option(
    "--game-name",
    "-g",
    type=click.Choice(["random", "esc", "rps", "ttt"], case_sensitive=False),
    default="random",
    show_default=True,
    help="Play game",
)
@click.option(
    "--size",
    "-s",
    type=int,
    default=3,
    show_default=True,
    help="Change game's size (if any)",
)
@click.option(
    "--mode", "-m", type=str, default=None, help="Change game's gamemode (if any)"
)
@click.option(
    "--board-style",
    "-b",
    "board_style",
    type=str,
    default="1",
    help="Change game's board style (if any)",
)
def game(game_name: str, size: int, mode: str, board_style):
    """
    Play game

    Game list:
    - esc: Escape loop
    - rps: Rock Paper Scissors
    - ttt: Tic Tac Toe
    """
    if game_name.startswith("random"):
        if __randc([0, 1]) == 0:
            game_escapeLoop()
        else:
            game_RockPaperScissors()
    else:
        if game_name.startswith("esc"):
            game_escapeLoop()
        elif game_name.startswith("rps"):
            game_RockPaperScissors(hard_mode=mode)
        elif game_name.startswith("ttt"):
            if board_style == "None":
                board_style = None
            elif board_style == "1":
                board_style = True
            else:
                board_style = False
            game_tictactoe(size=size, mode=mode, board_game=board_style)


@click.command()
@click.argument("pkg", type=click.Choice(__core.ModulePackage))
def install(pkg: str):
    """Install absfuyu's extension"""
    cmd = f"pip install -U absfuyu[{pkg}]".split()
    try:
        subprocess.run(cmd)
    except:
        try:
            cmd2 = f"python -m pip install -U absfuyu[{pkg}]".split()
            subprocess.run(cmd2)
        except:
            click.echo(f"{__COLOR['red']}Unable to install absfuyu[{pkg}]")
        else:
            click.echo(f"{__COLOR['green']}absfuyu[{pkg}] installed")
    else:
        click.echo(f"{__COLOR['green']}absfuyu[{pkg}] installed")


@click.command()
def advice():
    """Give some recommendation when bored"""
    from .fun import im_bored

    click.echo(f"{__COLOR['green']}{im_bored()}")


@click.group(name="do")
def do_group():
    """Perform functionalities"""
    pass


do_group.add_command(reset)
do_group.add_command(update)
do_group.add_command(game)
do_group.add_command(install)
do_group.add_command(advice)


# Main group init
###########################################################################
@click.group()
def main():
    """
    absfuyu's command line interface

    Usage:
        python -m absfuyu --help
        fuyu --help
    """
    pass


main.add_command(welcome)
main.add_command(greet)
main.add_command(toggle)
main.add_command(version)
main.add_command(do_group)


# Run
###########################################################################
if __name__ == "__main__":
    main()
