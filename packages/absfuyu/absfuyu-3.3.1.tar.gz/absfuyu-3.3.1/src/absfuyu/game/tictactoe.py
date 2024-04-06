# type: ignore
"""
Game: Tic Tac Toe
-----------------

Version: 1.0.3
Date update: 24/11/2023 (mm/dd/yyyy)
"""


# Library
##############################################################
import random as __random
import time as __time
from typing import List as __List
from typing import Optional as __Optional

from absfuyu import core as __core
from absfuyu.game.tictactoe2 import GameMode

# Tic Tac Toe
##############################################################

# GAME SETTING
X = "X"
O = "O"
BLANK = " "
POS_SPLIT = ","
END_BREAK = "END"
__C = __core.Color


# FUNCTIONS
def __test_case_3x3(num: int = 0):
    case = {
        1: [[X,X,X],
            [BLANK,BLANK,BLANK],
            [BLANK,BLANK,BLANK]],
        2: [[BLANK,BLANK,BLANK],
            [X,X,X],
            [BLANK,BLANK,BLANK]],
        3: [[BLANK,BLANK,BLANK],
            [BLANK,BLANK,BLANK],    
            [X,X,X]],
        4: [[X,BLANK,BLANK],
            [X,BLANK,BLANK],
            [X,BLANK,BLANK]],
        5: [[BLANK,X,BLANK],
            [BLANK,X,BLANK],
            [BLANK,X,BLANK]],
        6: [[BLANK,BLANK,X],
            [BLANK,BLANK,X],
            [BLANK,BLANK,X]],
        7: [[X,BLANK,BLANK],
            [BLANK,X,BLANK],
            [BLANK,BLANK,X]],
        8: [[BLANK,BLANK,X],
            [BLANK,X,BLANK],
            [X,BLANK,BLANK]],
    }
    try:
        import numpy as np
        for k, v in case.items():
            case[k] = np.array(v)
    except:
        pass
    
    if num < 1:
        return case
    return case[num]


def __gen_board(row_size: int, col_size: int, content: str = BLANK):
    """
    Generate board game (with or without `numpy`)

    Parameter:
    ---
    row_size : int
        Number of rows

    col_size : int
        Number of columns

    content : str
        What should be filled inside the board
    
    Return:
    ---
    Game board
    """
    
    try:
        import numpy as np
    except:
        np = None
    
    if np is None:
        board = [[BLANK for _ in range(row_size)] for _ in range(col_size)]
    else:
        board = np.full((row_size, col_size), content)
    return board

def __check_state(table):
    """
    Check game winning state
    
    Parameter:
    ---
    table : numpy.ndarray | list[list[str]]
        Game board
    
    Return:
    ---
    X | O | BLANK
    """

    # Data
    nrow, ncol = len(table), len(table[0])

    # Check rows
    for row in range(nrow):
        if len(set(table[row])) == 1:
            # return list(set(table[row]))[0]
            key = list(set(table[row]))[0]
            return {"key": key, "location": "row", "pos": row} # modified

    # Check cols
    for col in range(ncol):
        temp = [table[row][col] for row in range(nrow)]
        if len(set(temp)) == 1:
            # return list(set(temp))[0]
            key = list(set(temp))[0]
            return {"key": key, "location": "col", "pos": col} # modified
    
    # Check diagonal
    diag1 = [table[i][i] for i in range(len(table))]
    if len(set(diag1)) == 1:
        # return list(set(diag1))[0]
        key = list(set(diag1))[0]
        return {"key": key, "location": "diag", "pos": 1} # modified
    
    diag2 = [table[i][len(table)-i-1] for i in range(len(table))]
    if len(set(diag2)) == 1:
        # return list(set(diag2))[0]
        key = list(set(diag2))[0]
        return {"key": key, "location": "diag", "pos": 2} # modified
    
    # Else
    # return BLANK
    return {"key": BLANK}

def __print_board(table):
    """
    Print Tic Tac Toe board

    Parameter:
    ---
    table : numpy.ndarray | list[list[str]]
        Game board
    """
    nrow, ncol = len(table), len(table[0])
    length = len(table)
    print(f"{'+---'*length}+")
    for row in range(nrow):
        for col in range(ncol):
            print(f"| {table[row][col]} ", end="")
        print(f"|\n{'+---'*length}+")

def __win_hightlight(table):
    """
    Hight light the win by removing other placed key

    Parameter:
    ---
    table : numpy.ndarray | list[list[str]]
        Game board
    """

    # Get detailed information
    detail = __check_state(table)
    loc = detail["location"]
    loc_line = detail["pos"]

    # Make new board
    board = __gen_board(len(table), len(table[0]))

    # Fill in the hightlighted content
    if loc.startswith("col"):
        for i in range(len(board)):
            board[i][loc_line] = detail['key']
    elif loc.startswith("row"):
        for i in range(len(board)):
            board[loc_line][i] = detail['key']
    else:
        if loc_line == 1:
            for i in range(len(board)):
                board[i][i] = detail['key']
        else:
            for i in range(len(board)):
                board[i][len(board)-i-1] = detail['key']
    
    # Output
    return board

def __is_blank(table, pos: __List[int]):
    """Check if current slot is filled"""
    return table[pos[0]][pos[1]] == BLANK

def __convert_bot_output(pos: __List[int]):
    """
    Turn to real pos by:
    - +1 to row and col
    - convert into str
    """
    for i in range(len(pos)):
        pos[i] = str(int(pos[i])+1)
    return pos

def __generate_surround_move(table, pos: __List[int]):
    """
    Generate all surrounding move of a position
    """
    surround_move = [
        [pos[0]-1, pos[1]], # Up pos
        [pos[0]+1, pos[1]], # Down pos
        [pos[0], pos[1]-1], # Left pos
        [pos[0], pos[1]+1], # Right pos
        [pos[0]-1, pos[1]-1], # Up left pos
        [pos[0]-1, pos[1]+1], # Up right pos
        [pos[0]+1, pos[1]-1], # Down left pos
        [pos[0]+1, pos[1]+1], # Down right pos
    ]
    surround_move = {
        "U": [pos[0]-1, pos[1]], # Up pos
        "D": [pos[0]+1, pos[1]], # Down pos
        "L": [pos[0], pos[1]-1], # Left pos
        "R": [pos[0], pos[1]+1], # Right pos
        "UL": [pos[0]-1, pos[1]-1], # Up left pos
        "UR": [pos[0]-1, pos[1]+1], # Up right pos
        "DL": [pos[0]+1, pos[1]-1], # Down left pos
        "DR": [pos[0]+1, pos[1]+1], # Down right pos
    }
    # Remove value outside of board
    # output = []
    # for x in surround_move:
    #     condition = [
    #         x[0] < 0 or x[1] < 0,
    #         x[0] >= len(table) or x[1] >= len(table)
    #     ]
    #     if any(condition):
    #         continue
    #     output.append(x)
    # return output
    for k, v in surround_move.items():
        condition = [
            v[0] < 0 or v[1] < 0,
            v[0] >= len(table) or v[1] >= len(table)
        ]
        if any(condition):
            surround_move.pop(k)
            continue
        # output.append(x)
    return surround_move

def __generate_random_move(table):
    """
    Generate a random move from board game
    """
    while True:
        output = [
            __random.randint(0, len(table)-1),
            __random.randint(0, len(table)-1)
        ]
        if __is_blank(table, output):
            break
    return __convert_bot_output(output)

def __bot_move(table, pos: __List[int] = None, debug: bool = False):
    """
    Calculate position to place for BOT

    Parameters:
    ---
    table : numpy.ndarray | list[list[str]]
        Game board
    
    pos : list[int]
        previous move
    """

    if debug:
        print("Init Data:")
        print(table)
        print(pos)
        # print(opponent)

    if pos is None:
        return __generate_random_move(table)

    # Smart move: position that around previous game move
    valid_move = __generate_surround_move(table, pos)
    valid_move = list(valid_move.values())
    if debug:
        print("Smart move:")
        print(valid_move)
    
    # Filtered smart move: take only the placable position
    filtered_move = []
    for x in valid_move:
        if __is_blank(table, x):
            filtered_move.append(x)
        # else:
        #     opponent = table[pos[0], pos[1]]
        #     if table[x[0], x[1]] == opponent:
        #         temp = __generate_surround_move(table, x)
        #         for v in temp:
        #             if __is_blank(table, v):
        #                 filtered_move.append(v)
                # print(temp)

    
    if debug:
        print("Filtered move:")
        print(filtered_move)
    
    if not filtered_move:
        # If invalid then return a random move
        return __generate_random_move(table)
    
    # else
    while True:
        rand_move = __random.choice(filtered_move)
        if any([
            rand_move[0] < 0,
            rand_move[0] >= len(table),
            rand_move[1] < 0,
            rand_move[1] >= len(table)
        ]):
            continue
        
        if __is_blank(table, rand_move):
            rand_move = __convert_bot_output(rand_move)
            if debug:
                print("Chosen smart move:")
                print(rand_move)
            break
    
    # print(rand_move)
    return rand_move

def bot_ttt(table, pos: __List[int] = None):
    """Smart bot i guess"""
    free_slots = []
    for i in range(len(table)):
        for j in range(len(table[0])):
            if table[i][j] == BLANK:
                free_slots.append([i, j])
    if not free_slots:
        return None
    
    if pos is not None:
        sur = __generate_surround_move(table, pos)
        print(sur)

        counter = []
        for k, v in sur.items():
            if table[v[0]][v[1]] == table[pos[0]][pos[1]]:
                try:
                    if k == "R": counter.append(sur["L"])
                except: pass
                try:
                    if k == "L": counter.append(sur["R"])
                except: pass
                try:
                    if k == "U": counter.append(sur["D"])
                except: pass
                try:
                    if k == "D": counter.append(sur["U"])
                except: pass
                try:
                    if k == "UL": counter.append(sur["DR"])
                except: pass
                try:
                    if k == "UR": counter.append(sur["DL"])
                except: pass
                try:
                    if k == "DL": counter.append(sur["UR"])
                except: pass
                try:
                    if k == "DR": counter.append(sur["UL"])
                except: pass

        if not counter:
            pass

    return free_slots

def game_tictactoe(
        size: int = 3,
        mode: str = GameMode.ONE_V_BOT,
        smarter_bot: bool = False,
        board_game: __Optional[bool] = True,
        bot_time: float = 0,
        show_stats: bool = False,
    ):
    """
    Tic Tac Toe

    Parameters
    ----------
    size : int
        board size

    mode : str
        "1v1": Player vs player
        "1v0": Player vs BOT
        "0v0": BOT vs BOT
    
    smarter_bot : bool
        W.I.P
        New bot's behaviour
    
    board_game : True | False | None
        True: draw board
        False: print array
        None: no board or array

    bot_time : float
        time sleep between each bot move
        [Default: 0]
    
    show_stats : bool
        Print current game stats
        [Default: False]
    
    Returns
    ------
    dict
        Game stats
    """

    # Init game
    board = __gen_board(size, size)
    filled = 0
    current_player = X
    # state = __check_state(board)
    state = __check_state(board)["key"]
    BOT = False
    BOT2 = False

    # Welcome message
    if board_game is not None:
        print(f"""\
{__C['GREEN']}Welcome to Tic Tac Toe!

{__C['YELLOW']}Rules: Match lines vertically, horizontally or diagonally
{__C['YELLOW']}{X} goes first, then {O}
{__C['RED']}Type '{END_BREAK}' to end the game{__C['reset']}""")
    else:
        print("Tic Tac Toe")

    # Check gamemode
    game_mode = [
        "1v1", # Player vs player
        "1v0", # Player vs BOT
        "0v0" # BOT vs BOT
    ]
    if mode not in game_mode:
        mode = game_mode[1] # Force vs BOT
    if mode.startswith("1v0"):
        BOT = True
    if mode.startswith("0v0"):
        BOT = True
        BOT2 = True
    
    # Game
    if board_game:
        __print_board(board)
    elif board_game is None:
        pass
    else:
        print(board)

    place_pos = None
    while state == BLANK and filled < size**2:
        if board_game is not None:
            print(f"{__C['BLUE']}{current_player}'s turn:{__C['reset']}")
        
        try: # Error handling
            if (BOT and current_player == O) or BOT2:
                if smarter_bot:
                    move = __bot_move(board, place_pos)
                else:
                    move = __generate_random_move(board)
                str_move = POS_SPLIT.join(move)
                move = str_move

            else:
                move = input(f"Place {__C['BLUE']}{current_player}{__C['reset']} at {__C['BLUE']}<row{POS_SPLIT}col>:{__C['reset']} ")
            
            if move.upper() == END_BREAK: # Failsafe
                print(f"{__C['RED']}Game ended{__C['reset']}")
                break
            
            move = move.split(POS_SPLIT)
            row = int(move[0])
            col = int(move[1])
            place_pos = [row-1, col-1]

            if __is_blank(board, place_pos):
                board[place_pos[0]][place_pos[1]] = current_player
                filled += 1
            
            else: # User and BOT error
                if board_game is not None:
                    print(f"{__C['RED']}Invalid move, please try again{__C['reset']}")
                continue
        
        except: # User error
            if board_game is not None:
                print(f"{__C['RED']}Invalid move, please try again{__C['reset']}")
            continue
        
        state = __check_state(board)["key"]
        if board_game:
            __print_board(board)
        elif board_game is None:
            pass
        else:
            print(board)

        # state = __check_state(board)
        if state != BLANK:
            print(f"{__C['GREEN']}{state} WON!{__C['reset']}")
            if board_game:
                __print_board(__win_hightlight(board))
            break

        # Change turn
        if BOT2: # BOT delay
            __time.sleep(bot_time)
        
        if current_player == X:
            current_player = O
        else:
            current_player = X

    if state == BLANK and filled == size**2:
        print(f"{__C['YELLOW']}Draw Match!{__C['reset']}")
    
    # Game stats
    game_stats = {
        "Total move": filled,
        "Win by": None if state==BLANK else state,
    }
    if show_stats:
        print(f"{__C['BLUE']}GAME STATS:{__C['reset']}")
        for k, v in game_stats.items():
            print(f"{__C['YELLOW']}{k}: {v}{__C['reset']}")
    return game_stats
