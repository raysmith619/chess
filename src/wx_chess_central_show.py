#wx_chess_central_show.py frome wx_chess_game_show.py
#           25Feb2025  crs from chess_game_show.py
"""
Converted to a class ChessCentralShow from
wx_chess_game_show.py to provide more symetric command/event
processing between ChessCentralShow, ChessGameDisplay,
and ChessGotoMove.

wx_chess_game_show.py was developed from
chess_game_display.py particularly:
    1. display_dispatch(self, cmd, *args, **kwargs)
    2. cmd_<menu><sub_menu> functions run from 
        wx_cgd_menus.py tables
    
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

To minimize the differences created with this stack level we include
the most common Chessboard functions.  The functins we include
from Chessboard in ChessboardStack operate on the current board. 
"""

import re
import argparse
import multiprocessing as mp
import wx
import pgn

from graphics_braille.select_trace import SlTrace

###from graphics_braille.wx_speaker_control import SpeakerControlLocal

from chess_error import ChessError
from chessboard import Chessboard
from chessboard_stack import ChessboardStack
from chess_move import ChessMove
from chess_move_notation import ChessMoveNotation
from wx_chess_game_display import ChessGameDisplay
from chessboard_print import ChessboardPrint

class ChessCentralShow:
    def __init__(self,
        width = int(80*8+80*1.3),
        height = int(80*8+80*2.5),
        move_interval=255,   # Move interval in msec
        game_desc = None,
        ):
        self.frame = wx.Frame(None,
                size=wx.Size(width,height)) 
        
        self.speaker_control = None  # Set up for speaker
        # Setup centralized speaker control
        ###if __name__ == '__main__':
            ###mp.freeze_support()
            ###self.speaker_control = SpeakerControlLocal()   # centralized access to sound/speech engine
        self.game_looping = False    # While true we can loop
        if move_interval is None:
            move_interval = self.move_interval
        self.move_interval = move_interval     
        if game_desc is None:
            game_desc = "No Game Yet"
        self.game_desc = game_desc
        # Support board/display access
        self.cbs = None
        self.cbd = None
        self.do_looping_count = 0       # looping coung

    def setup_display(self, game):
        """ Setup display
        including basic board
        :game: chess game as pgn string
                default: no game
        """
        SlTrace.lg(f"setup_display: {game=}")
        ###if self.cbd is not None:
        ###    self.cbd.on_close_window()   # Remove existing display
        if self.cbd is None:
            self.cb = Chessboard()           # For inital sizes
            self.cb.standard_setup()         # Starting position
            self.cbs = ChessboardStack()
            self.cbs.push_bd(self.cb)
            self.cbd = ChessGameDisplay(self, self.cbs, title="-",
                                win_width=width, win_height=height,
                                speaker_control=self.speaker_control)
        else:
            self.cbd.setup_display(game)
            self.cbs = self.cbd.cbs
        self.cbd.setup_chess_goto_move(game=game)
        
    def setup_board(self, game):
        """ Setup new game board
        :game: game in pgn 
        """
        self.cbd.setup_board(game)
        
    def get_move_desc(self):
        """ Get move descriptor / title
            AFTER move has been made (i.e., in title of board display)
            We use the push down boards to get states before the move
            <move_no>: <white move spec>
                OR
            <move_no>: <white move spec> <black move spec>
        """
        return self.cbs.get_move_desc()

    def display_board(self, desc=None, new_display=False,
                    move_type=None):
        """ Display current board state
        :desc: description
            default: generate description
        :new_display: True - new independent display window created
            default: False - update current display window
        :move_type: END_GAME, END_SCAN, None
        """

        # If we want to force display and print
        xdisp = (self.cbd.setting_is_final_position_display
                and move_type == self.cbd.END_GAME)
        if desc is None:
            desc = self.get_move_desc()
        self.cbd.move_desc = desc
        display_options = "visual_s"
        #display_options = None
        self.cb = self.cbs.get_bd()           # Get current board
        if self.cb is None:
            SlTrace.lg("No board to display")
            return
        
        self.cbp = ChessboardPrint(self.cb)
        
        bd_str = self.cbp.display_board_str(display_options=display_options)
        gdesc = self.cbd.get_game_desc()
        desc = gdesc
        if xdisp or self.cbd.setting_is_printing_board:
            SlTrace.lg("\n"
                    f"{self.get_move_desc():7}   {desc}" +
                    "\n"+bd_str, replace_non_ascii=None)
        if xdisp or self.cbd.setting_is_printing_fen:
            fen_str = self.cb.board_to_fen_str()
            SlTrace.lg(f"{fen_str}\n")
        if new_display:
            self.cbs = self.cbs.copy()
            self.cb = self.cbs.get_bd()
            self.cbd = ChessGameDisplay(self.cbs,
                            speaker_control=self.speaker_control)
        if xdisp or self.cbd.setting_is_move_display:
            self.cbd.display_board(title=desc)    # Use current state
        self.move_interval = self.cbd.loop_interval
        #self.cbd.update()

    def get_next_move(self):
        """ Get next move from
            1. redo stack if any
                else
            2. current game, if any
        :returns: None if none left
                    ChessMove if a redo
                    move_spec if from move spec list
        """
            
        if (cm := self.cbs.move_redo()) is not None:  # Use redo, if any pending
            return cm   # bd_stack is adjusted
        
        return self.cbd.get_next_input_move()

    def error_show(self, desc=None):
        """ Report error, saving file png text
        :desc: description
        """
        self.cbd.error_show(desc=desc)
        self.display_board(move_type=self.cbd.END_GAME)
        if self.cbd.is_looping:
            self.stop_loop()
            
    def do_move(self, cm_or_spec=None):
        """ Do next move
        :cm_or_spec: move(ChessMove) or move specifiction
            default: get next move
        """
        SlTrace.lg(f"do_move({cm_or_spec =})")
        if self.cbd.is_end_game():
            self.display_board(move_type=self.cbd.END_GAME)
            return None
            
        if cm_or_spec is None:
            cm_or_spec = self.get_next_move()
            if cm_or_spec is None:
                SlTrace.lg("    No more moves")
                return None
            
        if isinstance(cm_or_spec, str):
            self.cb = self.cbs.get_bd()
            if self.cb is None:
                self.cb = Chessboard()
            self.cb = self.cbs.push_bd(self.cb)
            cm = ChessMove(self.cb, spec=cm_or_spec)
            SlTrace.lg(f"{cm}", "move_trace")
            self.cb.cm = cm
            if (decode_ret:=cm.decode(cm_or_spec)):
                err_prefix = f"Move: {cm.get_move_no()} {cm.spec} {cm.get_to_move()}"
                SlTrace.lg(f"{err_prefix} {decode_ret = }")
                SlTrace.lg(f"spec error:{cm.err}")
                self.error_show(desc=f"{err_prefix} {decode_ret = } spec error:{cm.err}")
                return None
            
        else:
            cm = cm_or_spec
        if cm is not None and cm.game_result is not None:
            self.cbd.set_end_game()
            self.display_board(move_type=self.cbd.END_GAME)
            return None
        
        if self.cbd.going_to_move_no == cm.move_no:
            SlTrace.lg(f"going_to {cm.move_no =}")        
            SlTrace.lg(f"{cm}")
            if self.cbd.is_scanning:
                self.cbd.scan_pause()
            '''
            else:
                self.cbd.stop_looping()
            '''
            SlTrace.lg("Ready to make move")
        cm.make_move()
        self.cbd.display_board()     # Use self.display_board???
        return cm
                
    def do_move_spec(self, spec):
        """ Do move specification (like do_move(spec))
        :spec: move specifiction
        :returns: error message, else None if OK
        """
        self.cbs.push_bd()
        cm = ChessMove(self.cbs.get_bd(), spec=spec)
        SlTrace.lg(f"{cm}")
        if (decode_ret:=cm.decode(spec)):
            err_prefix = f"Move: {cm.get_move_no()} {cm.spec} {cm.get_to_move()}"
            SlTrace.lg(f"{err_prefix} {decode_ret = }")
            SlTrace.lg(f"spec error:{cm.err}")
            return cm.err
        
        if (cm.make_move()):
            return cm.err    

        return cm.err
        
    def undo_move(self):
        """ Undo previous move, backing up to board state
        just before that move
        """
        SlTrace.lg("UnMove")
        cm = self.cbs.move_undo()
        return cm

    def redo_move(self):
        """ Redo previous undo, adjusting board state to
        just before the undo
        """
        cm = self.cbs.move_redo()
        if cm is not None:
            cm.make_move()
        return cm

    def restart_game(self):
        """ Resetup original board position
        """
        self.cbd.cmd_btn_restart()
        return None

    def do_looping(self):
        """ do game loop
        """
        self.do_looping_count += 1
        SlTrace.lg(f"do_Looping: {self.do_looping_count}")
        wx.GetApp().Yield()     # Allow ChessGotoMove refresh
        if self.cbd.move_index == 0:    # Begin Game
            ck_msg = self.cbd.ck_bd_setup()
            if ck_msg:
                SlTrace.lg(f"ERROR: Unexpected startup {ck_msg}")
                self.cbd.is_looping = False
                self.cbd.is_scanning = False
        new_move_index = self.cbd.cdata.chess_move()
        if new_move_index < 0:
            if self.cbd.is_scanning:
                self.cbd.scan_next_game()
            else:
                self.restart_game()
            return

        self.display_board()
        err_msg = self.cbd.get_err_msg()
        if err_msg is not None:
            SlTrace.lg(f"ERROR: {err_msg=}")
            self.cbd.is_looping = 0
            self.cbd.is_scanning = 0
        
    def loop_game(self):
        """ Start looping game
        """
        if self.cbd.is_scanning_paused:
            self.cbd.scan_continue(move_interval=self.move_interval)
            return
        
        self.do_looping_count = 0       # looping coung
        self.cbd.start_looping(self.do_looping)
        

    def stop_loop(self):
        """ Stop display looping
        """
        self.cbd.stop_looping()

    def scan_pause(self):
        """ Pause scanning
        """
        self.cbd.scan_pause()
        
    def scan_move(self, move):
        """ Do move from scan
        :move: move specification
                NEW_GAME for new game
                END_GAME at end of game
                END_SCAN at end of scan
        """
        if move == self.cbd.NEW_GAME:
            self.scan_new_game(self.cbd.sel_game)
            return
        
        elif self.cbd.is_end_game() or move == self.cbd.END_GAME:
            SlTrace.lg("Game end", "game_end")
            if self.cbd.setting_is_final_position_display:
                self.display_board(move_type=self.cbd.END_GAME)
            return
        
        elif move == '*':
            SlTrace.lg("Undecided end '*'")
            if self.cbd.setting_is_final_position_display:
                self.display_board()
            return
        
        elif move == self.cbd.END_SCAN:
            SlTrace.lg("End of scanning")
            self.cbd.stop_looping()
            return
            
        if self.do_move(move) is None:
            SlTrace.lg(f"Game result: {move =}", "game_result")
            return
        
        desc = self.get_move_desc()
        if self.cbd.setting_is_move_display:
            self.display_board(desc=desc)
        return
                

        
    def scan_new_game(self, input):
        """ Start new scanning game
        :input: input string
        """
        
        game = self.cbd.sel_game
        if game is None:
            return          # None to have
        
        #setup_display()
        self.game_desc = f"{self.cbd.sel_short_desc} {self.cbd.scan_file_name}"
        self.setup_board(game)
        self.display_board()

    def game_to_desc(self, game):
        """ Get PGN game description
        :game: PNG game
        """        
        return self.cbd.get_game_desc(game)
    
    def scan_next_game(self):
        """ Go to next scaned game
        """
        self.cbd.scan_next_game()
        self.scan_new_game()
            
    def get_file_games(self, *args, **kwargs):
        """ Get games, already read, from file
            Setup game and display
        """
        selection = kwargs["selection"]
        index = selection[0]
        game = selection[-1]
        SlTrace.lg(f"get_file_games: {game=} {index=}")
        if game is None:
            return None         # None to have
        
        short_desc = self.game_to_desc(game=game)
        SlTrace.lg(f"get_file_games: {short_desc=} {game=}")
        
        self.stop_loop()     # Stop action incase going
        self.game_desc = short_desc
        self.setup_display(game)
        self.setup_board(game)
        return None

    def cgd_goto_move(self, move_no, moved="white"):
        """ Go to move (after) and set display
        :move_no: table index, 0 - game beginning, before white's first move
        :moved: "-","white","black" last moved default: "white"
        """
        SlTrace.lg(f"ccs: cmd_goto_move({move_no =}, {moved=})")
        if move_no < 1:
            move_index = 0
        else:
            move_index = (move_no-1)*2+1
            if moved == "black":
                move_index += 1
        SlTrace.lg(f"cmd_goto_move: {move_no=}, {moved=}, {move_index=}")
        return self.cgd_goto_move_index(move_index)
        
    def cgd_goto_move_index(self, move_index):    
        if move_index < 0 or move_index > len(self.cbs.board_stack)-1:
            while self.do_move() is not None:
                pass

        if move_index < 0:
            move_index = len(self.cbs.board_stack)+move_index
        if move_index >= 0 and move_index < len(self.cbs.board_stack):
            self.cbs.set_cur_bd_index(move_index)
            self.display_board()
            return move_index
        
        return -1

    def get_fen_cmd(self, fen_str):
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
            cb = self.cbs.get_bd()
            if cb.fen_setup(cmd_str):
                SlTrace.lg(f"Bad FEN string: '{cb.err}'")
            self.display_board()    

    def do_moves(self, input):
        """ Add in move(s) to current board state
        resets redo/undo operation
        :input: one or more move specifications
        """
        move_specs = ChessMoveNotation.game_to_specs(input)
        for move_spec in move_specs:
            if (err:=self.do_move_spec(move_spec)):
                SlTrace.lg(f"Stop with error:{err}")
                break
        self.display_board()            

    def new_window(self):
        """ Create new independant window with current game state
        """
        self.display_board(desc="New Window", new_display=True)

    def set_move_no(self, move_no, moved="white"):
        """ Set current move number and moved color
        :move_no: move number (after) 1 - after white or black first move
        :moved: "-","white","black" last moved default: "white"
        """
        SlTrace.lg(f"chess_game_show: set_move_no({move_no =}, {moved=})")
        #self.cbd.set_move_no(move_no, moved=moved)
        if move_no < 1:
            move_index = 0
        else:
            move_index = (move_no-1)*2+1
            if moved == "black":
                move_index += 1
        self.stop_loop()
        # If move_index is out of range, do moves to get there,
        # bringing in moves from current game, if any
        if move_index < 0 or move_index > len(self.cbs.board_stack)-1:
            while self.do_move() is not None:
                pass
        stack_len = len(self.cbs.board_stack)        
        if move_index >= 0 and move_index < stack_len:
            self.cbs.set_cur_bd_index(move_index)
        else:
            ChessError(f"set_move_no: {move_no =}, {moved =} out of range: {stack_len =}")
        self.display_board() 

    def set_move_no_x(self, move_no, moved="white"):
        """ Set current move number and moved color
        :move_no: move number (after) 1 - after white or black first move
        :moved: "-","white","black" last moved default: "white"
        """
        SlTrace.lg(f"chess_game_show: set_move_no({move_no =}, {moved=})")
        if move_no < 1:
            move_index = 0
        else:
            move_index = (move_no-1)*2+1
            if moved == "black":
                move_index += 1
        self.stop_loop()
        if move_index < 0 or move_index > len(self.cbs.board_stack)-1:
            while self.do_move() is not None:
                pass

        if move_index < 0:
            move_index = len(self.cbs.board_stack)+move_index
        if move_index >= 0 and move_index < len(self.cbs.board_stack):
            self.cbs.set_cur_bd_index(move_index)
            self.display_board()
            
    """
    ChessGameDisplay origin commands
    """
    def cgd_game_file(self, *args, **kwargs):
        return self.get_file_games(*args, **kwargs)
    
    def cgd_chess_move(self):
        cm = self.do_move()
        if cm is None:
            return -1
        
        return self.cbs.get_bd_index()
    
    def cgd_chess_goto_move(self, move_no, moved="white"):
        """ goto move
        :returns: move_index
        """
        ret = self.cgd_goto_move(move_no, moved=moved)
        return ret
    
    def cgd_chess_unmove(self):
        cm = self.undo_move()
        if cm is None and self.cbs.get_bd_index() != 0:
            self.display_board()
            return -1
        
        if cm is not None:
            desc = cm.get_move_desc()      # Incase at beginning
        self.display_board()
        return self.cbs.get_bd_index()

    
    def cgd_restart(self):
        return self.restart_game()
    
    def cgd_loop_play(self):
        self.loop_game()
    
    def cgd_stop(self):
       return self.stop_loop()
    
    def cgd_get_fen(self, *args):
        return self.get_fen_cmd(args[0])
    '''
    def cgd_goto_move(self, move_no, moved="white"):
        return self.cmd_goto_move(move_no, moved=moved)
    '''
    def cgd_print_fen(self):
        self.cbd.print_fen()

    """
    Centralized commands
    """
    
    
    def update_board_state_for_move(self):
        """ Do chess move, modifying state
        :returns: updated move_index, negative if failed
        """
        return self.cgd_chess_move()

    def update_board_state_for_unmove(self):
        """ Do chess unmove
        :returns: new move_index, negative if failed
        """
        return self.cgd_chess_unmove()
    

    def update_board_state_for_goto_move(self, move_no, moved="white"):
        """ Do chess goto_move updating state and returning new move_index, 
            -1 if failed
        """
        new_move_index = self.cgd_chess_goto_move(move_no, moved=moved)
        return new_move_index

    def update_board_state_for_goto_move_index(self, move_index):
        """ Do chess goto_move updating state and returning new move_index, 
            -1 if failed
        """
        new_move_index = self.cgd_goto_move_index(move_index)
        return new_move_index
    


if __name__ == '__main__':
    SlTrace.clearFlags()
    #SlTrace.setFlags("no_ts=0")        # Timestamps for loging
    app = wx.App()

    game_commentary = """
    Game of the Century
    From https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
    """
    demo_game_text = """
    [Event "Third Rosenwald Trophy"]
    [Site "New York, NY USA"]
    [Date "1956.10.17"]
    [EventDate "1956.10.07"]
    [Round "8"]
    [Result "0-1"]
    [White "Donald Byrne"]
    [Black "Robert James Fischer"]
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
    pgn_games = pgn.loads(demo_game_text)
    demo_game = pgn_games[0]
    SlTrace.lg(f"{demo_game}")
    SlTrace.lg("\nmoves:")
    moves_str = ""
    line_str = ""
    for move in demo_game.moves:
        if len(line_str) >= 40:
            moves_str += "\n"
            line_str = ""
        moves_str += " " + move
        line_str += " " + move
    SlTrace.lg(moves_str)


    step_through = True        # wait till user commands
    quit_on_fail = True         # Quit on first fail    
    scan_max_loops = 1          # Limit scanning loops
    update_as_loaded = False
    width = int(80*8+80*1.3)
    height = int(80*8+80*2.5)
    frame = wx.Frame(None, size=wx.Size(width,height)) 


    parser = argparse.ArgumentParser()
    '''parser.add_argument('-m', '--moves', default=moves,
                        help=("Move string"
                                " (default:moves"))
    '''
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
    quit_on_fail = args.quit_on_fail



    ccs = ChessCentralShow()
    ccs.setup_display(demo_game)
    ccs.setup_board(demo_game)    
    SlTrace.set_start_time()                
    ccs.cbd.mainloop()     
