#chess_game_show.py 25Feb2025  crs from chess_move_notation.py
""" 
Display chess position/game
Board state for do/undo/redo is kept in a chessboard stack 
chessboard_stack.py (ChessboardStack)

A new move is added to the current chess board
and then the board is pushed on to board stack.
The board index is set to stack list position of this board.

A undo is produced by decreasing the current board index so that it
references the previou board state.

A redo is produced by increasing the current board index so that it
references the board before the previous undo.

To hide the differences created with this stack level we include
the most common Chessboard functions we include the same functions
in ChessboardStack which will operate on the current board. 
"""

"""
"""
import re
import argparse

from select_trace import SlTrace


from chess_error import ChessError
from chessboard import Chessboard
from chessboard_stack import ChessboardStack
from chess_move import ChessMove
from chess_move_notation import ChessMoveNotation
from chessboard_display import ChessboardDisplay
from chessboard_print import ChessboardPrint

SlTrace.clearFlags()
#SlTrace.setFlags("no_ts=0")        # Timestamps for loging

"""
Game of the Century
From https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
[Event "Third Rosenwald Trophy"]
[Site "New York, NY USA"]
[Date "1956.10.17"]
[EventDate "1956.10.07"]
[Round "8"]
[Result "0-1"]
[White "Donald Byrne"]
[Black "Robert James Fischer"]
"""    
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
scan_max_loops = 1          # Limit scanning loops



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


# Support board/display access
cbs = None
cbd = None
move_spec_list = []

def setup_display(moves=None):
    """ Setup display
    including basic board
    :moves: chess moves
            default: no moves
    """
    global cbs, cbd, move_spec_list
    
    cb = Chessboard()           # For inital sizes
    cbs = ChessboardStack()
    cbs.push_bd(cb)
    cb.standard_setup()         # Starting position
    cbd = ChessboardDisplay(cbs, title="Begin Game", scan_max_loops=scan_max_loops)
    if cbd.is_display_fen:
        fen_str = cb.board_to_fen_str()
        SlTrace.lg(f"{fen_str}\n")
    cbp = ChessboardPrint(cb)
    if moves is not None:
        move_specs = ChessMoveNotation.game_to_specs(moves)
        move_spec_list = move_specs[:]
    cbd.display_board()
    
    
def setup_board(move_specs):
    """ Setup new game board
    :move_specs: list of move specifications
    """
    global move_spec_list
    move_spec_list = move_specs[:]       # Copy list

setup_display()
move_specs = ChessMoveNotation.game_to_specs(moves)
setup_board(move_specs)    
#cbd.mainloop()

def get_move_desc():
    """ Get move descriptor / title
        AFTER move has been made (i.e., in title of board display)
        We use the push down boards to get states before the move
        <move_no>: <white move spec>
            OR
        <move_no>: <white move spec> <black move spec>
    """
    return cbs.get_move_desc()

game_desc = None    # Game description if one
def display_board(desc=None, new_display=False):
    """ Display current board state
    :desc: description
        default: generate description
    :new_display: True - new independent display window created
        default: False - update current display window
    """
    global cbs, cbd, cbp
    global move_interval    # msec between move change
    
    if desc is None:
        desc = get_move_desc()
    display_options = "visual_s"
    #display_options = None
    cb = cbs.get_bd()           # Get current board
    if cb is None:
        SlTrace.lg("No board to display")
        return
    
    cbp = ChessboardPrint(cb)
    
    bd_str = cbp.display_board_str(display_options=display_options)
    gdesc = "" if game_desc is None else game_desc
    if cbd.scan_nfile > 0:
        desc = f"{cbd.scan_nfile:2} {cbd.scan_ngame:2}    "
    desc = f"{desc:<15}"  + gdesc
    if cbd.is_printing_board:
        SlTrace.lg("\n"
                   +desc+
                   "\n"+bd_str, replace_non_ascii=None)
    if cbd.is_printing_fen:
        fen_str = cb.board_to_fen_str()
        SlTrace.lg(f"{fen_str}\n")
    if new_display:
        cbs = cbs.copy()
        cb = cbs.get_bd()
        cbd = ChessboardDisplay(cbs, from_display=cbd)
    cbd.display_board(title=desc)    # Use current state
    move_interval = cbd.loop_interval
    cbd.update()
    pass

def get_next_move():
    """ Get next move from
        1. redo stack if any
            else
        2. move spec list if any
    :returns: None if none left
                ChessMove if a redo
                move_spec if from move spec list
    """    
    if (cm := cbs.move_redo()) is not None:  # Use redo, if any pending
        return cm   # bd_stack is adjusted
    
    if len(move_spec_list) == 0:
        return None         # No more in list
    
    move_spec = move_spec_list.pop(0)
    return move_spec    

def error_show(desc=None):
    """ Report error, saving file png text
    :desc: description
    """
    cbd.error_show(desc=desc)
    if cbd.is_looping:
        stop_loop()
        
def do_move(cm_or_spec=None):
    """ Do next move
    :cm_or_spec: move(ChessMove) or move specifiction
        default: get next move
    """
    if cm_or_spec is None:
        cm_or_spec = get_next_move()
        if cm_or_spec is None:
            return None
        
    if isinstance(cm_or_spec, str):
        cb = cbs.get_bd()
        if cb is None:
            cb = Chessboard()
        cb = cbs.push_bd(cb)
        cm = ChessMove(cb, spec=cm_or_spec)        
        SlTrace.lg(f"{cm}")
        cb.cm = cm
        if (decode_ret:=cm.decode(cm_or_spec)):
            err_prefix = f"Move: {cm.get_move_no()} {cm.spec} {cm.get_to_move()}"
            SlTrace.lg(f"{err_prefix} {decode_ret = }")
            SlTrace.lg(f"spec error:{cm.err}")
            error_show(desc=f"{err_prefix} {decode_ret = } spec error:{cm.err}")
            return None
        
        cm.make_move()
    else:
        cm = cm_or_spec
    if cm is not None and cm.game_result is not None:
        #stop_loop()
        return None
    return cm
        
def do_move_spec(spec):
    """ Do move specification (like do_move(spec))
    :spec: move specifiction
    :returns: error message, else None if OK
    """
    cbs.push_bd()
    cm = ChessMove(cbs.get_bd(), spec=spec)
    SlTrace.lg(f"{cm}")
    if (decode_ret:=cm.decode(spec)):
        err_prefix = f"Move: {cm.get_move_no()} {cm.spec} {cm.get_to_move()}"
        SlTrace.lg(f"{err_prefix} {decode_ret = }")
        SlTrace.lg(f"spec error:{cm.err}")
        return cm.err
    
    if (cm.make_move()):
        return cm.err    

    return cm.err
    
def undo_move():
    """ Undo previous move, backing up to board state
    just before that move
    """
    SlTrace.lg("UnMove")
    cm = cbs.move_undo()
    return cm

def redo_move():
    """ Redo previous undo, adjusting board state to
    just before the undo
    """
    cm = cbs.move_redo()
    if cm is not None:
        cm.make_move()
    return cm

game_looping = False    # While true we can loop
move_interval = 250     # Move interval in msec
def restart_game():
    """ Resetup original board position
    """
    while cbs.move_undo():
        pass
    return None

def do_looping():
    """ do game loop
    """
    if do_move() is None:
        display_board()
        restart_game()
        return

    display_board()

    
def loop_game():
    """ Start looping game
    """
    if cbd.is_scanning_paused:
        cbd.scan_continue(move_interval=move_interval)
        return
        
    cbd.start_looping(do_looping)
    

def stop_loop():
    """ Stop display looping
    """
    cbd.stop_looping()

def scan_pause():
    """ Pause scanning
    """
    cbd.scan_pause()
    
def scan_move(move):
    """ Do move from scan
    :move: move specification
    """
    if do_move(move) is None:
        #scan_pause()
        cm = cbs.get_move()
        SlTrace.lg(f"{cm}")
        #error_show(f"{cm}")
        return
    
    desc = get_move_desc()
    display_board(desc=desc)
    return
               

    
def scan_new_game(input):
    """ Start new scanning game
    :input: input string
    """
    global game_desc
    
    game = cbd.sel_game
    if game is None:
        return          # None to have
    
    setup_display()
    game_desc = f"{cbd.sel_short_desc} {cbd.scan_file_name}"
    setup_board(game.moves)
    display_board()
    
def get_file_games():
    """ Get games, already read, from file
        Setup game and display
    """
    global game_desc
    global move_spec_list
    
    game = cbd.sel_game
    if game is None:
        return          # None to have
    
    stop_loop()     # Stop action incase going
    restart_game()
    game_desc = cbd.sel_short_desc
    setup_board(game.moves)

def goto_move_idx(input):
    """ Go to move *set display)
    :input: input text goto_move_idx<whitespace>*<index>
    """
    if isinstance(input, int):
        move_index = input
    elif isinstance(input, str):
        if not (goto_match:=re.match(r'goto_move_idx?\s*(-?\d+)', input)):
            raise ChessError(f"goto_move_idx {input = } bad input")
    
    val_str = goto_match.group(1)
    move_idx = int(val_str)
    stop_loop()
    if move_idx < 0 or move_idx > len(cbs.board_stack)-1:
        while do_move() is not None:
            pass

    if move_idx < 0:
        move_idx = len(cbs.board_stack)+move_idx
    if move_idx >= 0 and move_idx < len(cbs.board_stack):
        cbs.set_cur_bd_index(move_idx)
        display_board()

def get_fen_cmd(fen_str):
    """ Use fen_str to setup board
    extened format:
        optional:
            FEN:<space>* <fen string>
        followed by
            optional:
                ":" if preceeded by FEN
            optional:
                <move spec list>
        followed by
            optional:
                ":" "go" - execute the move spec list
    """
    if (fen_match:=re.match(r'(FEN:\s*)?(.*)$', fen_str)):
        cmd_str = fen_match.group(2)
        cb = cbs.get_bd()
        if cb.fen_setup(cmd_str):
            SlTrace.lg(f"Bad FEN string: '{cb.err}'")
        display_board()    

def do_moves(input):
    """ Add in move(s) to current board state
    resets redo/undo operation
    :input: one or more move specifications
    """
    move_specs = ChessMoveNotation.game_to_specs(input)
    for move_spec in move_specs:
        if (err:=do_move_spec(move_spec)):
            SlTrace.lg(f"Stop with error:{err}")
            break
    display_board()            

def new_window():
    """ Create new independant window with current game state
    """
    display_board(desc="New Window", new_display=True)
                    
def display_cmd_proc(input):
    """ Process display commands
        Note to synchronize display window, all calls should include display id
    :input: command string [<display id>] removed if present
        s,n: do_move
        u: undo move
        r: redo_move
        f: read games(s) from file
        e: print FEN
        goto_move_idx n: goto move index
        get_fen: FEN: load state, given the FEN notation
        w: create new window
        we <display_id>: Set context to new display        
    """
    global cbd, cbs
    if (match_input:=re.match(r'(.*)(\[[^]]*\])$', input)):
        input, display_info = match_input.groups()
        SlTrace.lg(f"input: {input} display_info: {display_info}")
        if (match_display_info:=re.match(r'\[(\d+)([^]]*)\]$', display_info)):
            display_id, _ = match_display_info.groups()
            cbdisp = ChessboardDisplay.get_display(display_id)
            if cbdisp is None:
                raise ChessError(f"Display_id {display_id} out of range")
                return
            
            cbd = cbdisp
            cbs = cbd.cbs         
    fen_cmd_prefix = "get_fen: "
    goto_move_idx_prefix = "goto_move_idx"
    cm = None
    # Process all multicharacter commands
    if (match_multi_cmd:=re.match(r'(\w+)\s+(.*)$', input)):
        cmd,cmd_args = match_multi_cmd.groups()
        if cmd == "enter_moves":
            return do_moves(cmd_args)
        
        elif cmd == "get_fen":
            return get_fen_cmd(cmd_args)
        
        elif cmd == "goto_move_idx":
            return get_fen_cmd(cmd_args)
        
        elif cmd == "scan_new_game":
            return scan_new_game(input)
        
    if input == "f":    # Read game(s) from file
        get_file_games()
        return
    elif input == "e":  # Print FEN
        cb = cbs.get_bd()
        cb.print_board_to_fen()
        return
    
    elif input.startswith(fen_cmd_prefix):
        get_fen_cmd(input[len(fen_cmd_prefix):])
        return
    
    elif input.startswith(goto_move_idx_prefix):
        goto_move_idx(input[len(goto_move_idx_prefix):])
        return
    
    elif input.startswith("scan_new_game"):
        scan_new_game(input)
        return
    
    elif (match_cmd := re.match(r'scan_move\s+(.*)', input)) is not None:
        move = match_cmd.group(1)
        scan_move(move)
        return
    
    elif input == 'w':
        new_window()
        return
    
    elif input == 's' or input == 'n':
        cm = do_move()
    elif input == 'u':
        cm = undo_move()
        desc = get_move_desc()      # Incase at beginning
        display_board(desc=desc)
        return
    
    elif input == 'r':
        cm = redo_move()
    elif input == 'p':
        stop_loop()
    elif input == 'l':
        loop_game()
    elif input == 't':
        restart_game()
        cm = "blah"
    else:
        SlTrace.lg(f"Unrecognized cmd:{input}")
        return None
    
    if cm is not None:
        desc = get_move_desc()
        display_board(desc=desc)


cbd.set_cmd(display_cmd_proc)     
cbd.update()
            
cbd.mainloop()     
