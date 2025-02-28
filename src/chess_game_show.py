#chess_game_show.py 25Feb2025  crs from chess_move_notation.py
""" 
Display chess position/game

"""

"""
"""
import re
import argparse
import tkinter as tk

from select_trace import SlTrace
SlTrace.clearFlags()

from chessboard import Chessboard
from chess_move import ChessMove
from chess_move_notation import ChessMoveNotation
from chessboard_display import ChessboardDisplay
from chessboard_print import ChessboardPrint
    
moves = """
1.Nf3 Nf6 2.c4 g6 3.Nc3 Bg7 4.d4 O-O
5.Bf4 d5 6.Qb3 dxc4 7.Qxc4 c6 8.e4 Nbd7
9.Rd1 Nb6 10.Qc5 Bg4 11.Bg5 Na4 12.Qa3 Nxc3
13.bxc3 Nxe4 14.Bxe7 Qb6 15.Bc4 Nxc3 16.Bc5 Rfe8+
17.Kf1 Be6 18.Bxb6 Bxc4+ 19.Kg1 Ne2+ 20.Kf1 Nxd4+
21.Kg1 Ne2+ 22.Kf1 Nc3+ 23.Kg1 axb6 24.Qb4 Ra4
25.Qxb6 Nxd1 26.h3 Rxa2 27.Kh2 Nxf2 28.Re1 Rxe1
29.Qd8+ Bf8 30.Nxe1 Bd5 31.Nf3 Ne4 32.Qb8 b5
33.h4 h5 34.Ne5 Kg7 35.Kg1 Bc5+ 36.Kf1 Ng3+
37.Ke1 Bb4+ 38.Kd1 Bb3+ 39.Kc1 Ne2+ 40.Kb1
Nc3+ 41.Kc1 Rc2# 0-1
"""
step_through = True        # wait till user commands
xs = True
update_as_loaded = True     # Display board change as game loaded
    
quit_on_fail = True         # Quit on first fail    

# To support display_board access
cb = None
cbd = None
cbp = None

def check_user(prompt):
    """ Wait for user instructions
        default: execute/display move
        returns:
            s, "" ENTER for step
            u - undo previous move
            r - redo last undo

    """
    inp = input(prompt)
    return inp

def display_board(desc=None, new_display=False):
    """ Display current board state
    :desc: description
        default: no description
    :new_display: True - new display created
        default: False - update current display
    """
    global cb, cbd, cbp
    
    if desc is None:
        desc = ""
    display_options = "visual_s"
    #display_options = None
    bd_str = cbp.display_board_str(display_options=display_options)
    SlTrace.lg("\n"+desc+"\n"+bd_str, replace_non_ascii=None)
    if new_display:
        cb = cb.copy()
        cbd = ChessboardDisplay(cb)
        mw2 = tk.Toplevel()     # Subsequent window                
        cbd = ChessboardDisplay(cb, mw=mw2)
    cbd.display_board(title=desc)
    cbd.update()



parser = argparse.ArgumentParser()
parser.add_argument('-m', '--moves', default=moves,
                    help=("Move string"
                            " (default:moves"))
parser.add_argument('-f', '--file', default=None,
                    help=("Moves file"
                            " (default:use string"))

parser.add_argument('-s', '--step_through', default=step_through,
                    help=("Step through game"
                            " (default:{step_through}"))
parser.add_argument('-u', '--update_as_loaded', default=update_as_loaded,
                    help=("Update display as game loaded"
                            " (default:update"))
parser.add_argument('-q', '--quit_on_fail', action='store_true', default=quit_on_fail,
                    help=(f"Quit on first failure"
                            f" (default: {quit_on_fail}"))

args = parser.parse_args()             # or die "Illegal options"

file = args.file
moves = args.moves
quit_on_fail = args.quit_on_fail
    
mw = tk.Tk()
cb = Chessboard()
move_specs = ChessMoveNotation.game_to_specs(moves)
move_spec_list = move_specs[:]       # Copy list
cb.standard_setup()
cbd = ChessboardDisplay(cb, mw=mw, title="Begin Game")
cbp = ChessboardPrint(cb)
cbd.display_board()
#cbd.mainloop()

def get_move_desc(cm):
    """ Get move descriptor / title
        AFTER move has been made
    :cm: move ChessMove
        <move_no>: <white move spec>
            OR
        <move_no>: <white move spec> <black move spec>
    """
    if cm.board.get_prev_move() is None:
        return "Begin Game"
    
    move_spec = cm.spec
    move_no = cm.move_no
    to_move = cm.to_move
    desc = f"{move_no}:"
    if to_move == "black":
        prev_move = cm.board.get_prev_move(-2)
        if prev_move is not None:
            prev_spec = prev_move.spec
            desc += f" {prev_spec}"
    desc += f" {move_spec}"
    return desc

def get_next_move():
    """ Get next move from
        1. redo stack if any
            else
        2. move spec list if any
    :returns: ChessMove in parsed state, ready to make_move
    """    
    if (cm := cb.move_redo()) is not None:  # Use redo, if any pending
        return cm
    
    if len(move_spec_list) == 0:
        return None
    
    move_spec = move_spec_list.pop(0)
        
    cm = ChessMove(cb)
    if cm.decode(move_spec):
        SlTrace.lg(f"spec error:{cm.err}")
        return None
    return cm
        
def do_move():
    """ Do preparation for next move
    """
    cm = get_next_move()
    if cm is None:
        return None
    
    cm.make_move()
    return cm

def undo_move():
    """ Undo previous move, backing up to board state
    just before that move
    """
    cm = cb.move_undo()
    return cm

def redo_move():
    """ Redo previous undo, adjusting board state to
    just before the undo
    """
    cm = cb.move_redo()
    cm.make_move()
    return cm

def display_cmd_proc(input):
    """ Process display commands
    :input: command string
        s,n: do_move
        u: undo move
        r: redo_move
    """
    if input == 's' or input == 'n':
        cm = do_move()
    elif input == 'u':
        cm = undo_move()
    elif input == 'r':
        cm = redo_move()
    else:
        SlTrace.lg("Unrecognized cmd:{input}")
        return None
    
    if cm is not None:
        desc = get_move_desc(cm)
        display_board(desc=desc)


cbd.set_cmd(display_cmd_proc)     
cbd.update()
            
mw.mainloop()     

err_count = cb.get_err_count()
if err_count > 0:
    err_first_move_no = cb.get_err_first_move_no()
    err_first = cb.get_err_first()
    SlTrace.lg(f"Parse Errors:{err_count}")
    SlTrace.lg(f"First error: move {err_first_move_no}:"
                f" {err_first}")