# wx_chess_game_display.py 10Apr2025  crs from chessboard_display.py
""" Display/Presentation level for display/manipulation of chess games
First used with chess_show_game.py, now a transition to using wxPython
for display.  This was done to have better interaction with screen readers,
such as JAWS and NVDA to aid use by the blind.
We use wx_chess_canvas_panel.py(ChessCanvasPanel) for board/pieces display
We use CgdMenus(wx_cgd_menus.py) to consolidate menu functions.
We use CgdFte (wx_cgd_fte.py) to provide a front end which, almost
any menu/GUI command can be done via the keyboard with audio feed back.
"""
import re
import sys
import os
import copy

import wx

import pgn

from gr_input import gr_input        
from graphics_braille.wx_speaker_control import SpeakerControlLocal

from chessboard import Chessboard
from wx_chessboard_panel import ChessboardPanel
from graphics_braille.wx_grid_path import GridPath

from wx_cgd_menus import CgdMenus
from chess_square import ChessSquare
from graphics_braille.select_trace import SlTrace
from graphics_braille.select_trace import TraceError

from wx_cgd_front_end import CgdFrontEnd
from wx_chess_piece_images import ChessPieceImages
from wx_chess_canvas_panel import ChessCanvasPanel
from input_gather import InputGather
from chessboard_stack import ChessboardStack
from chess_error import ChessError
from chess_game_data_source import ChessGameDataSource
from wx_selection_ok import SelectionOK
from wx_chess_settings_frame import ChessSettingsFrame
from chess_settings_server import ChessSettingsServer
from wx_chess_goto_move import ChessGotoMove

class ChessGameDisplay(wx.Frame):
    base_display_id = 0         # Unique display id: 1...
    display_d = {}              # dictionary of ChessboardDisplay by id
    END_GAME = "END_GAME"
    NEW_GAME = "NEW_GAME"
    END_SCAN = "END_SCAN"
    
    @classmethod
    def reset(cls):
        """ Reset display stack
        """
        cls.base_display_id = 0
        cls.display_d = {}
        
    @classmethod
    def get_display(cls, did):
        """Get display
        :display_id: display id (int)
        :returns: instance of ChessboardDisplay, None if none with this id
        """
        if isinstance(did, str):
            did = int(did)
        if did in cls.display_d:
            return cls.display_d[did]
        
        return None


    def __init__(self,
        cbs,
        parent=None,            
        app=None,
        display_list=None,
        title=None, speaker_control=None,
        games_dir="../games",       # chess games directory
        errors_dir="../errors",
        win_width=800, win_height=800,
        grid_width=8, grid_height=8,
        win_fract=True,
        x_min=None, y_min=None,
        x_max=None, y_max=None,
        line_width=1, color="black",
        enable_mouse = False,
        pgm_exit=None,
        show_marked=False,
        drawing=False,
        silent=False,
        visible=True,
        menu_str="",
        key_str="",
        setup_wx_win = True,
                 ):
        self.chess_goto_move = None     # Goto/game display
        
        #frame = CanvasFrame(title=mytitle, size=wx.Size(width,height))
        """ Setup game window
        :cbs: chessboard stack
        :app: wx application object
            default: create object
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :title: window title
        """
        self.going_to_move_no = None    # Check if move
                                        # pause loop if at move
        ChessGameDisplay.base_display_id += 1
        self.display_id = self.base_display_id
        self.call_later = None  # instance for stopping
        self.on_cmd = None
        self.err_count = 0
        self.prev_fen = None    # last entered
        self._is_end_game = False   # Set when end of game condition arrises
        self.is_display_fen = True  # True - display FEN
        self.is_looping = False
        self.is_scanning = False
        self.is_scanning_paused = False
        self.scan_file_name = None
        self.scan_is_force_next_game = False
        self.setting_is_stop_on_error = True  # stop on error
        self.scan_max_loops = 1
        self.scan_nfile = 0
        self.scan_ngame = 0     # games scanned in file
        self.scan_ngame_total = 0   # total games scanned
        self.sel_short_desc = None
        self.sel_game = None
        self.setting_game_start_no = 1
        self.setting_game_end_no = None # No limit
        self.setting_is_move_display = True
        self.setting_is_final_position_display = True
        self.setting_is_printing_board = True
        self.setting_is_printing_fen = True
        self.settings_is_fastest_run = False
        self.settings_is_shortest_move = False
        self.old_setting_is_move_display = False
        self.old_setting_is_printing_board = False
        self.old_setting_is_printing_fen = False
        self.old_loop_interval = 250
        self.loop_interval = 250    # msec loop interval
        self.end_game_interval = 250    # msec end game interval
        self.cbs = cbs
        if app is None:
            app = wx.App()
        self.app = app
        if title is None:
            title = "ChessGameDisplay"
        if speaker_control is None:
            pass
        if speaker_control is None and setup_wx_win:
            SlTrace.lg("Creating own SpeakerControl")
            speaker_control = SpeakerControlLocal()
        self.speaker_control = speaker_control
        self.display_list = display_list
        if win_width is None:
            win_width = 800
        if win_height is None:
            win_height = 800
        if title is None:
            title = "ChessGameDisplay"
        self.title = title
        super().__init__(parent, title=title,
                         size=wx.Size(win_width, win_height))
        self.win_print_entry = None
        self.is_legal_move_ck = True    # True - check for legal move as early as possible
        self.is_printing_fen = True

        self.games_dir = games_dir
        self.setup_errors(errors_dir)
        self.errors_dir = errors_dir
        self.win_width = win_width
        self.win_height = win_height
        self._pgm_exit = pgm_exit
        self.grid_width = grid_width
        win_fract = False
        if x_min is None:
            x_min = 0. if win_fract else 0.
        if y_min is None:
            y_min = 0. if win_fract else 0.
        if x_max is None:
            x_max = 1. if win_fract else self.draw_width()
        if y_max is None:
            y_max = 1. if win_fract else self.draw_height()
        # create the audio feedback window
        self.title = title

        
        #self.Show()
        #mw.withdraw()
        


        self._visible = visible
        self.grid_width = grid_width
        self.grid_height = grid_height
        green = "#008000"
        btn_panel = wx.Panel(self)
        btn_panel.SetBackgroundColour(wx.Colour(246,246,246))
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_move = wx.Button(btn_panel,label="Move")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_move, btn_move)
        btn_move.SetForegroundColour(wx.Colour(green))
        btn_sizer.Add(btn_move)
        
        btn_unmove = wx.Button(btn_panel,label="UnMove")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_unmove, btn_unmove)
        btn_unmove.SetForegroundColour(wx.RED)
        btn_sizer.Add(btn_unmove)
        
        btn_sizer.AddStretchSpacer(1)
        txt_game_move = wx.StaticText(btn_panel,
                        label="Game Move",
                        style=wx.ALIGN_CENTRE_HORIZONTAL)
        btn_sizer.Add(txt_game_move, wx.ALIGN_CENTER_HORIZONTAL)
        gm_font = txt_game_move.GetFont()
        gm_font.SetPointSize(16)
        txt_game_move.SetFont(gm_font)
        self.txt_game_move = txt_game_move
        
        btn_sizer.AddStretchSpacer(1)
        btn_panel_right = wx.Panel(btn_panel)
        btn_sizer.Add(btn_panel_right)
        btn_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_restart = wx.Button(btn_panel_right,label="Restart")
        btn_restart.SetForegroundColour(wx.BLACK)
        btn_right_sizer.Add(btn_restart, wx.ALIGN_RIGHT)
        
        btn_loop = wx.Button(btn_panel_right,label="Loop play")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_loop, btn_loop)
        btn_loop.SetForegroundColour(green)
        btn_right_sizer.Add(btn_loop, wx.ALIGN_RIGHT)

        btn_stop = wx.Button(btn_panel_right,label="Stop")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_stop, btn_stop)
        btn_stop.SetForegroundColour(wx.RED)
        btn_right_sizer.Add(btn_stop, wx.ALIGN_RIGHT)
        btn_panel_right.SetSizer(btn_right_sizer)
        
        btn_panel.SetSizer(btn_sizer)
        
        board = cbs.get_bd()
        chess_pan = ChessCanvasPanel(self, board=board)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn_panel, wx.SizerFlags().Expand())
        sizer.Add(chess_pan)
        self.SetSizer(sizer)
        self.chess_pan = chess_pan
        
        self.fte = CgdFrontEnd(self, title=title, silent=silent, color=color)
        self.menus = self.fte.menus # Menus setup by fte
        self.chess_pan.set_key_press_proc(self.fte.key_press)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down, id=wx.ID_ANY)
        

        self.escape_pressed = False # True -> interrupt/flush
        #self.set_cell_lims()
        self.do_talking = True      # Enable talking
        self.logging_speech = True  # Output speech to log/screen
        self.from_initial_canvas = False    # True iff from initial drawing
        self.running = True         # Set False to stop
        ###wxport###self.mw.focus_force()
        #self.pos_check()            # Startup possition check loop
        self.fte.do_complete(menu_str=menu_str, key_str=key_str)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        self.Raise()                # put on top

    def cgm_on_move_change(self, move_no=None, moved=None):
        """ Called on move changes from ChessGameMove
        :move_no: move number 0-beginning,
        :moved: color moved "white"/"black"
        """
        if move_no == 0:
            SlTrace.lg("Beginning")
        SlTrace.lg(f"{move_no=} {moved=}")
        SlTrace.lg(f"ChessGameDisplay.on_move_change("
                   f"{move_no=}, {moved=}")
        self.display_dispatch("set_move_no", move_no, moved=moved)
        
    def restart(self):
        """ Restart board
        """
        cb = Chessboard()
        self.cbs = ChessboardStack()
        self.cbs.push_bd(cb)


    """ 
    Menu top level functions
    Named cmd_<menu>_<item>
    """
    def doOK(self, selection=None):
        """ process selection
        :selection: (index,...,game)
        """
        self.display_dispatch("game file", selection=selection)
        
    def cmd_file_open(self, e=None):
        """Select chess game files and load the game
        game files are text files of Portable Game Notation (PGN).
        see: https://www.chess.com/terms/chess-pgn
        """
        with wx.FileDialog(self, "Open PGN file", wildcard="*.pgn",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            game_file_name = fileDialog.GetPath()
            game_data_source = ChessGameDataSource(game_file_name)
            game_select = SelectionOK(self, game_data_source, doOK=self.doOK)
            game_select.Show()
            
    def cmd_file_save(self, e=None):
        pass
        
    def cmd_file_log_file(self, e=None):
        pass
    
    def cmd_file_properties_file(self, e=None):
        pass
    
    def cmd_file_exit(self, e=None):
        self.exit()

    def exit(self, rc=None):
        """ Main exit
        """
        if rc is None:
            rc = 0
        if self._pgm_exit is not None:
            self._pgm_exit()      # Use supplied pgm_exit
            
        SlTrace.lg("AudoDrawWindow.exit", "adw")
        SlTrace.onexit()    # Force logging quit
        os._exit(0)


    def cmd_scanning_files(self, e=None):
        """ Scan chess files in games directory
        """
        dlg = wx.DirDialog(None, "Scanning Directory", defaultPath=self.games_dir)
        ans = dlg.ShowModal()
        if ans != wx.ID_OK:
            SlTrace.lg("Directory not selected")
            return
        
        self.games_dir = dlg.GetPath()
        self.is_scanning = True     # Scanning files in progress
        self.scan_loops = 0         # Keep count
        self.scan_files_start()

    def settings_window_cmd(self,_=None):
        SlTrace.lg("adw.settings_window_cmd")
        self.settings_win = ChessSettingsFrame(self)
        self.settings_win.Show()


    """    
    Settings with explicit get/set functions
    "Use Shortest Move Interval" :
    """
    
    def get_shortest_move(self):
        return self.settings_is_shortest_move
    
    def set_shortest_move(self, value=True):
        self.settings_is_shortest_move = value
        self.setting_move_interval = 2
        
    def get_fastest_run(self):
        return self.settings_is_fastest_run

    def set_fastest_run(self, value=True):
        self.settings_use_fastest_run = value
        if not hasattr(self, "settings_win"):
            return value
        
        sw = self.settings_win
        sw.save_vals()
        if value:
            self.old_setting_is_move_display = self.setting_is_move_display
            self.old_setting_is_printing_board = self.setting_is_printing_board
            self.old_setting_is_printing_fen = self.setting_is_printing_fen
            self.old_loop_interval = self.loop_interval
            sw.set_val(name="Display_Move", value=False)        
            sw.set_val(name="Print_Board", value=False)        
            sw.set_val(name="Print_FEN", value=False)        
            sw.set_val(name="Move_Interval", value=1)        

        else:
            sw.set_val(name="Display_Move", value=self.old_setting_is_move_display)
            sw.set_val(name="Print_Board", value=self.old_setting_is_printing_board)
            sw.set_val(name="Print_FEN", value=self.old_setting_is_printing_fen)
            sw.set_val(name="Move_Interval", value=self.old_loop_interval)
                
        return self.settings_use_fastest_run
        

    def setting_game_start_cmd(self):
        from gr_input import gr_input        
        new_val_str = gr_input("Starting game no",
                               default=str(self.setting_game_start_no))
        self.setting_game_start_no = int(new_val_str)

    def setting_game_end_cmd(self):
        """ default: None - No limit
        """
        from gr_input import gr_input        
        new_val_str = gr_input("Starting game no",
                               default=str(self.setting_game_start_no+1))
        self.setting_game_end_no = int(new_val_str)

            
    def setting_move_display_cmd(self,_=None):
        self.setting_is_move_display = True
       
    def setting_move_display_no_cmd(self,_=None):
        self.setting_is_move_display = False

    def setting_final_position_display_cmd(self):
        self.setting_is_final_position_display = True

    def setting_final_position_display_no_cmd(self):
        self.setting_is_final_position_display = False
        
        
    def setting_loop_interval_cmd(self):
        """ Set/change loop interval
        """
        from gr_input import gr_input
        
        interval = self.loop_interval
        new_val_str = gr_input("Loop interval(msec)", default=str(interval))
        print(f"{new_val_str = }")
        if new_val_str == "":
            return
        interval = int(new_val_str)
        self.loop_interval = interval

    def setting_print_bd_cmd(self):
        self.setting_is_printing_board = True

    def setting_print_bd_no_cmd(self):
        self.setting_is_printing_board = False

    def setting_print_fen_cmd(self):
        self.setting_is_printing_fen = True

    def setting_print_fen_no_cmd(self):
        self.setting_is_printing_fen = False
        
            
    def setting_stop_on_error_cmd(self,_=None):
        self.setting_is_stop_on_error = True
            
    def setting_no_stop_on_error_cmd(self,_=None):
        self.setting_is_stop_on_error = False

        
    """ 
    End of menu commands
    """
    
    """ 
    Button commands
    """
    def send_chess_goto_move_ch_cmd(self, ch):
        """ Send cmd as key via ChessGotoMove
        self.GetEventHandler().ProcessEvent(event)
        :ch: character to simulate key_down
        """
        if self.chess_goto_move is not None:
            self.chess_goto_move.simulate_key_down(ch)


    def on_chess_goto_move_cmd(self, ch):
        """ Called on ChessGotoMove key press
        :ch: character pressed
        """
        if ch == "L":
            self.display_dispatch("loop_play") 
        elif ch == "S":
            self.display_dispatch("stop")
        else:
            ChessError(f"on_chess_goto_cmd: unknown {ch = }") 

    def cmd_btn_move(self, e=None):
        ###self.display_dispatch("chess_move")
        self.send_chess_goto_move_ch_cmd(" ")
    
    def cmd_btn_unmove(self, e=None):
        ###self.display_dispatch("chess_unmove")
        self.send_chess_goto_move_ch_cmd("\b")

    def cmd_btn_loop(self, e=None):
        ###self.display_dispatch("loop_play")
        self.send_chess_goto_move_ch_cmd("l")

    def cmd_btn_stop(self, e=None):
        self.display_dispatch("stop")
        self.send_chess_goto_move_ch_cmd("s")
    
    """ 
    End of button commands
    """
    def setup_errors(self, errors_dir):
        """ Setup errors directory
        :errors_dir:
        """
        self.err_count = 0          # Count of errors      
        self.err_first = None       # first error, if any   
        self.err_first_move_no = 0  # first error move no
        directory = errors_dir
        self.errors_dir = errors_dir
        
        if not os.path.exists(directory):
            try:
                os.mkdir(directory)
            except:
                raise TraceError("Can't create errors directory %s"
                                     % directory)
                sys.exit(1)
        
            print("Error games Directory %s  created\n"
                  % os.path.abspath(directory))


    def draw_height(self):
        """ drawing area height reduced from window height
        """
        return self.win_height*(21/25)  # Hack for now

    def draw_width(self):
        """ drawing area width reduced from window width
        """
        return self.win_width*(38/40)  # Hack for now


    """ Process window events
    """
    def window_entry_cmd(self, ev=None):
        """ Announce when our dispplay is active
        with a command including our id
        Only send if on_cmd is set.
        """
        return      # DROPPED in favor of adding id to each command
    
        if self.on_cmd is not None:
            self.display_dispatch(input=f"we {self.display_id}")
    
    """ Setup keyboard/button commands
    """
    
    def print_fen_cmd(self):
        """ print FEN for current game state
        """
        self.display_dispatch("print_fen")
    
    def print_fen(self):
        """ Print current board FEN
        """
        bd = self.get_bd()
        if bd is None:
            return
        bd.print_board_to_fen()
            
    def move_cmd(self):
        """ Make move
        """
        self.display_dispatch(input="n")
        
    def unmove_cmd(self):
        """ Unmakeake move
        """
        self.display_dispatch(input="u")

    def stop_cmd(self):
        """ Restart game
        """
        self.display_dispatch(input="p")

    def loop_cmd(self):
        """ Restart game
        """
        self.display_dispatch(input="l")

    def start_looping(self, loop_fun=None, interval=None):
        """ Start looping
        :loop_fun: loop function to call at interval
        :interval: interval (msec) to call loop_fun
            default: leave interval unchanged
        """
        if loop_fun is None:
            loop_fun = self.loop_call
        self.loop_fun = loop_fun
        if interval is not None:
            self.loop_interval = interval
        self.is_looping = True  # Cleared to stop loop
        self.loop_call()    # use after?

    def stop_looping(self):
        """ Stop looping
        Note we do not stop the current execution.
        If the function is exceptionally long, the
        user can check the status of self.is_looping
        within the function, to effect an early exit.
        """
        self.call_later_stop()
        self.is_looping = False
        self.is_scanning = False
    
    def call_later_stop(self):    
        if self.call_later is not None:
            self.call_later.Stop()
            self.call_later = None
            
    def loop_call(self):
        """ Function to call users looping function
        """
        if self.is_looping:
            self.loop_fun()
        if self.is_looping:
            self.after_no_arg(self.loop_interval, self.loop_call)
        else:
            self.call_later_stop()
            
    def restart_cmd(self):
        """ Restart game
        """
        self.display_dispatch(input="t")

    def set_game(self, game):
        """ Set current game, scanned or played
        :game: game in png format
        """
        self.sel_game = game
                        
    def set_cmd(self, on_cmd):
        """ Setup cmd link
        :on_cmd: cmd(input) cmd
        :returns: previous on_cmd
        """
        old_cmd = self.on_cmd
        self.on_cmd = on_cmd
        return old_cmd  

    def set_move_no(self, move_no, moved="white"):
        """ Set current move number and moved color
        No display is done, just set the current board index
        :move_no: move number (after) 1 - after white or black first move
        :moved: "-","white","black" last moved default: "white"
        """
        SlTrace.lg(f"chess_game_display: set_move_no({move_no =}, {moved=})")
        if move_no < 1:
            move_idx = 0
        else:
            move_idx = (move_no-1)*2+1
            if moved == "black":
                move_idx += 1
        stack_len = len(self.cbs.board_stack)        
        #if move_idx >= 0 and move_idx < stack_len:
        self.cbs.set_cur_bd_index(move_idx)

    def set_title(self, title):
        """ Set game frame title
        :title: title text
        """
        self.SetTitle(title)
        self.txt_game_move.SetLabel(" "*20 + title)
        self.txt_game_move.Refresh()

    """
    Capture std keyboard key presses
    and pass to ChessGotoMove for processing
    """
    def on_key_down(self, event):
        key = event.GetKeyCode()
        SlTrace.lg(f"\n\nChessGameDisplayon_key_down:{key=}"
                   f" {chr(key)=}")
        if self.chess_goto_move is not None:
            self.chess_goto_move.on_key_down

        


    # Display Command Dispatch
    def display_dispatch(self, cmd, *args, **kwargs):
        """ Dispatch action requests
        :self: ChessGameDisplay instance, must have 
        :cmd: command identifying string
        :args: positional args,
        :kwargs: keyword args
        """
        if self.on_cmd is not None:
            SlTrace.lg(f"on_cmd({cmd=}, {args=}, {kwargs=})")
            self.on_cmd(self, cmd, *args, **kwargs)


    def mainloop(self):
        """ Do mainloop
        """
        self.app.MainLoop()
            
    def after(self, int_ms=0, cmd=None, arg=None):
        """ Call cmd after interval
        :int_ms: after this interval in msec
                default: as soon as possible
        :cmd: function to call
        :arg: argument to cmd
        """
        ###TBD   self.mw.after(int_ms, cmd, arg)    
            
    def after_no_arg(self, int_ms=0, cmd=None):
        """ Call cmd after interval with no arg
        :int_ms: after this interval in msec
                default: as soon as possible
        :cmd: function to call
        :arg: argument to cmd
        """
        self.call_later = wx.CallLater(int_ms, cmd)    

    def is_end_game(self):
        """ Check if end of game, clear after call
        """
        if self._is_end_game:
            self._is_end_game = False
            return True
        
        return False

    def set_end_game(self):
        """ Set end of game flag
        """
        self._is_end_game = True

    def get_cur_half_moves(self):
        """Number of half moves in game
        0 at beginning of game
        """
        bd = self.get_bd()
        if bd is None:
            return 0
        cm = bd.get_move()
        if cm is None:
            return 0
        move_no = cm.get_move_no()
        to_move = cm.get_to_move()
        moved = "white" if to_move == "black" else "black"
        nhalf = 2*(move_no-1)
        if moved == "white":
            nhalf += 1  # white has moved
        return nhalf
    
    def setup_chess_goto_move(self, game=None):
        """ Setup goto_move for game change
        :game: PGN notation
        """
        if self.chess_goto_move is None:
            self.chess_goto_move = ChessGotoMove(
                self,
                game=game,
                on_move_change=self.cgm_on_move_change)
        gt_total_hmove = self.chess_goto_move.get_total_half_moves()
        bd_cur_hmove = self.get_cur_half_moves()
        if bd_cur_hmove > gt_total_hmove:
            if self.chess_goto_move is not None:
                self.chess_goto_move.Destroy()
                self.chess_goto_move = None
            self.chess_goto_move = ChessGotoMove(
                self,
                game=self.sel_game,
                on_move_change=self.on_move_change)
           
    def update(self):
        """ Do update, allowing graphics to update
        """
        ### TBD    self.mw.update()
            
    def display_board(self, title=None,
                      include_pieces=True):
        """ Display board
        :title: board title - placed on window
        :include_pieces: include board pieces in display
            default: True - show pieces
        """
        self.Freeze()
        if 0 and self.chess_goto_move is not None:
            self.update_chess_goto_move()
        if title is None:
            title = self.title
        self.title = title
        self.include_pieces = include_pieces    
        if title is None:
            title = self.title
        if self.err_count > 0:
            title = f"ERRORS: {self.err_count} {title}"
        self.set_title(title)
        bd = self.get_bd()
        self.chess_pan.set_board(bd)
        self.chess_pan.Refresh()
        self.Thaw()

    def get_moved(self):
        """ color just moved
        """
        
    def update_chess_goto_move(self):
        """ Update goto display
        """
        SlTrace.lg("update_chess_goto_move")
        if self.chess_goto_move is None:
            self.setup_chess_goto_move()
        self.setup_chess_goto_move()
        bd_cur_half_move = self.get_cur_half_moves()
        self.chess_goto_move.set_half_move(
            half_move=bd_cur_half_move,
            ignore_select=True)

    def get_geo_whxy(self):
        """ Obtain geometry of display window
        :returns: list of width,height,x-offset,y-offset ints in pixels
        """
        x,y = self.GetPosition()
        w,h = self.GetSize()
        return w,h,x,y
        
    def err_add(self, msg=None):
        """ Set and Count errors
        :msg: count as error if msg != ""
            default: self.err - current parsing error message
        :returns: msg
        """
        if msg is None:
            msg = self.err
            
        if msg is not None and msg != "":
            self.err = msg
            self.err_count += 1
            if self.err_first is None:
                self.err_first_file_name = self.scan_file_name
                self.err_first_desc = self.sel_short_desc
                self.err_first_game = self.sel_game
                self.err_first = msg
        return msg    

    def error_show(self, desc=None):
        """ Show error
        if scanning, then go to next file
        """
        SlTrace.lg(f"Error {desc}")
        self.print_fen()
        
        self.err_add(msg=desc)
        
        self.save_error_game(desc)
        if self.is_scanning:
            if self.setting_is_stop_on_error:
                self.scan_pause()
                SlTrace.lg("Looping paused because of error")
                return

            self.scan_force_next_game()
        SlTrace.lg("Continuing")    

    def change_menu_label(self, menu, index, new_label):
        menu.entryconfigure(index, label=new_label)

    def get_bd(self):
        """ Get current board
        """
        return self.cbs.get_bd()
    
    def get_fen_str(self, ignored=None):
        """ Get and send FEN str
        """
        fen_str = self.fen_entry.get()
        self.display_dispatch(f"get_fen {fen_str}")
        self.fen_frame.destroy()

    def new_window_cmd(self):
        """ Create new independant window with current game state
        """
        self.display_dispatch("w")
        
    def enter_fen_cmd(self):
        """ Setup board, using FEN string,
        with optional following move sequence
        """
        from gr_input import gr_input
        
        new_fen = gr_input("Enter FEN", default=self.prev_fen)
        if new_fen == "":
            return
        bd = self.get_bd()
        if (err := bd.fen_check(new_fen)) is not None:
            SlTrace.lg(f"{err =} in {new_fen}")
            return
        
        self.restart()  # New game
        bd = self.get_bd()
        bd.fen_setup(new_fen)
        self.prev_fen = new_fen
        self.display_board()
            
        
    
    def move_validate(self, spec):
        """ Move validate, returns adjusted move specification
        :spec: entered specification
        :returns: "enter moves <updated value>"
        """
        ''' Can't convert from lowercase b may be a pawn
        specs = spec.split()
        specs_new = []
        for spec in specs:
            if (mv_match:=re.match(r'([rnbqkp])([:x])?([a-h])(.*)$', spec)):
                piece,capture,dest,rest = mv_match.groups()
                spec_new = piece.upper()
                if capture:
                    spec_new += capture
                spec_new += dest
                if rest:
                    spec_new += rest
                spec = spec_new
            specs_new.append(spec)
        spec_new = " ".join(specs_new)
        '''
        spec_new = spec
        return f"enter_moves {spec_new}"
    
    def enter_moves_cmd(self):
        """ Provide move entering,
        """
        if self.on_cmd is None:
            SlTrace.lg("Need to call set_moves_cmd before doing do_moves")
            return
        w,h,x,y = self.get_geo_whxy()
        x0 = int(x + w/2)
        y0 = y + 10
        ig = InputGather(mw=self.mw, call_with_input=self.display_dispatch,
                        validate=self.move_validate,
                        title=f"{self.display_id}: Enter Moves",
                        entry_label="Move(s)",
                        xoff=x0,  yoff=y0)
        

    move_index = 0        # move index from selection
    def goto_move_cmd(self):
        """ Select game move and set to pause there during 
        next looping/scanning run
        """
        SlTrace.lg("wx_chess_game_display.py:goto_move_cmd")
        pause_no = self.going_to_move_no
        at = "" if pause_no is None else f"[{pause_no}]"
        new_val_str = gr_input()
        SlTrace.lg(f"{new_val_str =}")
        if (m_move := re.match("^\s*(\d+)\s*(\w*)\s*$", new_val_str)):
            move_no = int(m_move.group(1))
            moved_g = m_move.group(2)
            moved_l = moved_g.lower()[0] if moved_g != "" else "w"
            moved = "white" if moved_l == "w" else "black"
            self.display_dispatch("goto_move", move_no, moved=moved)
        else:
            SlTrace.lg(f"Unexpected goto_move str:{new_val_str}")
            
    def print_game_cmd(self):
        """ list game info
        """
        self.print_game(self.sel_game, desc=self.sel_short_desc)

    def print_game(self, game=None, desc=None):
        """ List selected game
        :game: game to list default: current game 
        :desc: optional description
        """
        if game is None:
            game = self.sel_game        
        if desc is None:
            desc = ""
        if game is None:
            SlTrace.lg("No current game")
            return
        
        game_str = pgn.dumps(game)
        SlTrace.lg(f"{desc}\n{game_str}")
    
    def print_move_no(self, move_no=None):
        """ Print current move number and moved color
        :move_no: move number (after) 1 - after white or black first move
        """
        if move_no is None:
            hm = self.get_cur_half_moves()
            moved = "white" if (hm % 2) == 1 else "black"
            move_no = (hm+1)//2            
            bd = self.get_bd()
            if bd is None:
                return 0
            cm = bd.get_move()
            SlTrace.lg(f"HM: {hm} Move: {move_no} {moved} {cm=}")
        
    def win_size_event(self, e):  
        pass
    
    def pgm_exit(self):
        code = 0
        self.exit(code) 

    def save_error_game(self, desc=None, game=None):
        """ Report error, saving file png text
        :desc: description
        :game: game
                default: from cbd
        """
        if game is None:
            game = self.sel_game
        if game is None:
            SlTrace.lg("No sel_game stored")
            return
                        
        file_base = (f"error_{SlTrace.getTs()}"
                     +f"_{self.scan_nfile}_{self.scan_ngame}.pgn")
        file_name = os.path.join(self.errors_dir, file_base)
        with open(file_name,"w") as f:
            file_text = pgn.dumps(game)
            print(file_text, file=f)
            if desc is not None:
                print("\n{\n" + desc + "\n}\n", file=f)

    def scan_force_next_game(self):
        """ Force next move to go to next game
        """
        self.scan_is_force_next_game = True
        
    def scan_files_start(self):
        """ Start files scan
        :games_dir: directory of games pgn files
        """
        SlTrace.set_start_time()
        self.scan_loops += 1
        if self.scan_max_loops is not None:
            if self.scan_loops > self.scan_max_loops:
                SlTrace.lg(f"Stopping at {self.scan_loops = }")
                return
        
        self.scan_moves_iter = None # Iterate through game moves
        self.scan_games_iter = None # Iterate through file games
        # Iterate through dir files
        self.scan_files_iter = self.scan_dir_iter(self.games_dir)
        self.is_scanning = True
        self.after_no_arg(0, self.scan_do_move)       # Start/continue move scan

    def scan_is_wanted_game(self, pnggame):
        """ Check if we want to scan this game
        :pgngame: our game
        :returns: True if this game is our list
        """
        return True     # everything

    def scan_continue(self, move_interval=None):
        """ Continue scanning
        :move_interval: if present, update move interval
        """
        self.is_scanning = True
        self.is_scanning_paused = False
        if move_interval is not None:
            self.loop_interval = move_interval
        self.after_no_arg(0, self.scan_do_move)
            
    def scan_do_move(self):
        """ Continue game moves scan
        """
        if not self.is_scanning:
            return      # Scanning is over
    
        move = self.scan_get_move()            
        if move is None:
            self.after_no_arg(0, self.scan_files_start)  # start over
            return
        
        self.scan_call(move)
            
    def scan_call(self, move):
        """ Function to call users scan looping function
        We use the looping function
        :move: move specification "END_GAME" for end of game
        """
        self.display_dispatch("scan_move", (move))
        if self.is_scanning:
            self.after_no_arg(self.loop_interval, self.scan_do_move)

    def scan_moves_iterator(self, pgngame):
        """ Iterate moves through pgngame
        :pgngame: game returned via pgn.GameIterator()
        :returns: move if one, None if none left
        """
        move_index = 0
        while move_index < len(pgngame.moves):
            move = pgngame.moves[move_index]
            move_index += 1
            if move.startswith('{'):
                continue    # ignore comments
            yield move
        
        return None

        
    def scan_get_move(self):
        """ Get next move from scanning
        :returns: move, END_GAME if end of game
                None if at end of scanning list
        """
        # Loop to handle empty games
        while True:
            try:
                if self.scan_moves_iter is not None:
                    move = next(self.scan_moves_iter)
                    if self.scan_is_force_next_game:
                        raise StopIteration()   # force end of game
                    
                    return move
                
            except StopIteration:
                pass        # End of this game's moves
                self.scan_is_force_next_game = False
                self.scan_moves_iter = None     # Force next game
                return self.END_GAME    # Returned at end of game
            
            # Get next game.
            if (game := self.scan_get_game()) is None:
                return self.END_SCAN            # No more games
            
            # Check if a desired game.
            if not self.scan_is_wanted_game(game):
                continue
            
            self.scan_ngame += 1
            self.scan_ngame_total += 1
            # Update with new game info
            self.scan_moves_iter = self.scan_moves_iterator(game)
            short_desc = (f"{game.white} vs. {game.black}"
                        f" {game.event} {game.date}")
            self.set_game(game)
            self.sel_short_desc = short_desc
            return self.NEW_GAME
        return move
 
    def scan_get_game(self):
        """ Get next game, None if no more
        :returns: PgnGame, else None if nomore games
        """
        # Loop to handle empty files
        game = None
        while  True:
            if self.scan_games_iter is None:
                game = None
            else:
                try:
                    game = next(self.scan_games_iter)
                except StopIteration:
                    game = None
            if game is None:    
                if (file := self.scan_get_file()) is None:
                    return None
        
                self.scan_nfile += 1
                SlTrace.lg(f"\nFile {self.scan_nfile:2}: {file}")
                self.scan_file_name = file
                with open(file) as game_file:
                    pgn_text = game_file.read()
                    pgn_games = pgn.loads(pgn_text) # Returns a list of PGNGame
                    start_i = 0
                    end_i = len(pgn_games)-1
                    if (self.setting_game_start_no > 1
                        and self.setting_game_start_no < len(pgn_games)):
                        start_i = self.setting_game_start_no-1
                    if (self.setting_game_end_no is not None and
                        self.setting_game_end_no != ""):     
                       if (self.setting_game_end_no >= 0
                           and self.setting_game_end_no < len(pgn_games)):
                           end_i = self.setting_game_end_no-1
                           pgn_games = pgn_games[self.setting_game_start_no-1:] 
                    self.scan_ngame = start_i   # Bump before descr
                    self.scan_games_iter = iter(pgn_games[start_i:end_i+1])
            else:
                return game
 
    def scan_get_file(self):
        """ Get next file, None if no more
        :returns: file_path, else None if nomore files
        """

        try:
            file = next(self.scan_files_iter)
        except StopIteration:
            return None
        
        return file
        
    def scan_next_game(self):
        """ Do next game
        """
        game = self.game_iter.next()
        

    def scan_pause(self):
        """ Pause scanning
        """
        self.is_scanning = False
        self.is_scanning_paused = True
                
    def scan_dir_iter(self, games_dir):
        """ Iterate over directory, yielding next file path
        each time
        :games_dir: directory to scan
        :returns: next file path, None if end
        """
        for file in os.listdir(games_dir):
            # check the games files
            if file.endswith(".pgn"):
                # print path name of selected files
                file_path = os.path.join(games_dir, file)
                yield file_path
            
        return None
    

    def file_save(self):
        raise Exception("Not yet implemented")

    def LogFile(self):
        raise Exception("Not yet implemented")

    def move_control(self):
        raise Exception("Not yet implemented")

    def get_speaker_control(self):
        return self.speaker_control

    """ Links to speaker control
    """

    def is_silent(self):
        return self.fte.is_silent()

    def speak_text(self, msg, dup_stdout=True,
                   msg_type=None,
                   rate=None, volume=None):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :msg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9            
        """
        self.win_print(msg)
        if self.is_silent():
            if dup_stdout:
                SlTrace.lg(msg)
            return
        
        self.speaker_control.speak_text(msg=msg, msg_type=msg_type,
                             dup_stdout=dup_stdout,
                             rate=rate, volume=volume)

    def stop_speak_text(self):
        """ Stop ongoing speach, flushing queue
        """
        self.speaker_control.stop_speak_text()

    """ Links to fte """
            
    def win_print(self,*args, dup_stdout=False, **kwargs):
        """ print to listing area
        :*args: print-like args
        :**kwargs: print-flags
        :dup_stdout:  send duplicate to stdout
        """
        self.fte.win_print(args=args, dup_stdout=dup_stdout, kwargs=kwargs)
        
    def on_close_window(self, event):
        SlTrace.lg("wx_chess_game_display"
                   " on_close_window")
        if self.chess_goto_move is not None:
            self.chess_goto_move.Destroy()
        self.Destroy()

    #############################################################
    ###   Speaker Contontrol Stub out
    ############################################################
    def get_speaker_control(self):
        """ void stub for speaker control
        """
        return None
            
if __name__ == '__main__':
    from graphics_braille.select_trace import SlTrace
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    from chessboard_stack import ChessboardStack
    from wx_cgd_front_end import CgdFrontEnd
    from wx_cgd_menus import CgdMenus
        
    SlTrace.clearFlags()
    pieces_list = [
        'FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        ':Kc1Qe1kh7 w',
    ]
    #pieces_list = pieces_list[0:1]  # TFD - In tkinter version,second board loses images
    #pieces_list *= 2
    cbds = []
    cBd = None
    cbds.append(cBd)
    
    def test_on_cmd(cbd, cmd, *args, **kwargs):
        SlTrace.lg(f"{cmd = } {args = } {kwargs = }")

    app = wx.App()        
    cbs = ChessboardStack()    
    #root.title("Main Window")    
    for pieces in pieces_list: 
        width = int(80*8+80*1.3)
        height = int(80*8+80*2.5)
        frame = wx.Frame(None, size=wx.Size(width,height)) 
        cb = Chessboard(pieces=pieces)
        cbs.push_bd(cb)
        cbp = ChessboardPrint(cb)
        cbp.display_board()
        cbd = ChessGameDisplay(cbs, parent=frame, app=app,
                               win_width=width, win_height=height,
                               title=f"pieces={pieces}")
        cBd = cbd
        cbd.set_cmd(test_on_cmd)    # Set in each window
        if cBd is None:
            cBd = cbd
        new_piece = 'Ne4'
        cb.add_pieces(new_piece)
        cbd.display_board(title=new_piece)
        ###cbd.display_board()
        ###TBD   geos = cbd.get_geo_whxy()
        ###TBD   SlTrace.lg(f"{cbd.display_id}: {geos}")
        SlTrace.lg(f"After pieces={pieces}")
    #root.withdraw()
    cBd.mainloop()
