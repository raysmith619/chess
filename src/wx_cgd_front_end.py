#wx_cgd_front_end.py    06Aug2026  crs, remove cgd graphics_braille
#                       10Apr2025  crs, Adapted from cgd_front_end.py
# 
#
"""
ChessGameDisplay support using wxPython
Trying to use lessons learned with wxPython port of AudioDrawWindow
"""
import wx
import sys
from math import sqrt
from datetime import datetime
import time 

from graphics_braille.wx_stuff import *
from graphics_braille.select_trace import SlTrace
from graphics_braille.wx_audio_beep import AudioBeep
from chess_square import ChessSquare
from chessboard_stack import ChessboardStack
from graphics_braille.grid_fill_gobble import GridFillGobble
from graphics_braille.wx_trace_control_window import TraceControlWindow
from graphics_braille.wx_key_cmd_proc import KeyCmdProc

from wx_cgd_menus import CgdMenus


class CgdFrontEnd:

    """
    Front end functions
    """
    def __init__(self, cgd,
                 title=None, key_str=None, menu_str=None,
                 pos_check_interval= .1,
                 pos_rep_interval = .1,
                 pos_rep_queue_max = 1,
                 visible_figure = True,
                 enable_mouse = False,
                 silent=False,
                 pgmExit=None,
                 show_marked=False,
                 shift_to_edge=None,
                 color="blue",
                 ):
        """ front end support
        :cgd: (ChessGameDisplay) parent window
        :title: title for reporting
        :pos_rep_interval: minimum time between reports
                default: .5 seconds
        :pos_rep_queue_max: maximum position report queue maximum
                default: 4
        :silent: make noise dissapear
                default: cgd.silent - False
        :visible_figure: figure is visible
                default: True - visible
        :key_str: initial key command string default: none
        :menu_str: initial menu command string default: none
        """
        self.cgd = cgd
        self.menus = CgdMenus(self, frame=self.cgd)
        self.key_cmd_proc = KeyCmdProc(cgd, key_press=self.key_press)
        #self.speaker_control = self.get_speaker_control()
        #self.speaker_control = None
        if title is None:
            title = "Audio Menu"
        self.title = title
        self.win_print_entry = cgd.win_print_entry
        self._multi_key_progress = False    # No multi-key cmd in progress
        self.key_str = key_str
        self.menu_str = menu_str
        self.rept_at_loc = True         # Start with reporting at loc
        self._echo_input = True     # True -> speak input
        self._silent = silent           # So prev=self._silent  doesn't fail
        self.set_silent(silent) # Start with speaking
        ###self.set_using_audio_beep(False)
        ###self.set_enable_mouse(enable_mouse)
        ###self.setup_beep()

    def silence(self):
        """ Function to check for silent mode
        """
        return self.is_silent()

    def is_silent(self):
        return self._silent
    
        
    def set_silent(self, val=True):
        """ Set / Clear silent
        :val: value to set
        :returns: previous silent value
        """
        prev_val = self._silent
        self._silent = val
        return prev_val


    def do_complete(self, menu_str=None, key_str=None):
        """ Complete menu process
        """

    def wait_on_output(self):
        """ Wait till queued output speech/tones completed
        """
        while True:
            if self.cgd.speaker_control.is_busy():
                self.update()
                continue

            break
    """
    Setup menus
    """
    def pgm_exit(self, rc=None):
        SlTrace.lg("fte.pgm_exit")
        self.cgd.exit()

    def File_Open_tbd(self):
        print("File_Open_menu to be determined")

    def File_Save_tbd(self):
        print("File_Save_menu to be determined")

    """ Automate functions for menu access
    """
    def do_menu_str(self, menu_str=None):
        """ Execute initial navigate string, if any
            wait on output before each cmd action
        :menu_str: string default: use self.menu_str
        """
        if menu_str is None:
            menu_str = self.menu_str
        if menu_str is None or menu_str == "":
            return

        menu_cmds = menu_str.split(';')
        for cmd in menu_cmds:
            cmd = cmd.strip()
            cmd_type, cmd_letters = cmd.split(':')
            menu_scs = self.get_menu_item_scs(cmd_type)
            if menu_scs is None:
                raise Exception("No command short cut {cmd_type} in {cmd}")
            for c in cmd_letters:
                cmd_command = self.get_menu_cmd(cmd_type, c)
                if cmd_command is None:
                    raise Exception("No command {cmd_type}:{c}")
                self.wait_on_output()
                cmd_command()

    def do_key_str(self, key_str=None):
        """ Execute initial key string, if any
            wait on output before each cmd action
        :key_str: string default: use self.nav_str
        """
        slow_key_str = SlTrace.trace("slow_key_str")
        if key_str is None:
            key_str = self.key_str
        if key_str is None or key_str == "":
            return

        SlTrace.lg(f"do_key_str: {key_str}")
        syms = key_str.split(";")
        for sym in syms:
            SlTrace.lg(f"press: {sym}")
            self.wait_on_output()
            self.key_cmd_proc.put_key_cmd(sym)



    def pause(self, time_sec):
        """ Pause for time (sec) while allowing update events
        :time: pause time in seconds
        """
        end_time = time.time() + time_sec
        SlTrace.lg(f"pause: end_time:{end_time}")
        last_time = time.time()
        while True:
            now = time.time()
            if now > end_time:
                break

            if now > last_time + 30:
                print(f"pause time left:{end_time-now:.2f}")
                last_time = now
            self.update()


    """ key / mouse operation
    and those actions close to that
    """

    def motion(self, x, y):
        """ Mouse motion in  window
        """
        if not self.is_enable_mouse():
            return      # Ignore mouse motion 

        if self.motion_level > 1:
            SlTrace.lg("Motion Recursion: motion_level({self.motion_Level} > 1")
            self.motion_level = 0
            return

        self.set_xy((x, y))
        x,y = self.get_xy()
        x,y = x + self.x_min, y + self.y_min
        self.win_x,self.win_y = x,y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        quiet = self._drawing   # move quietly if drawing
        self.move_to(x,y, quiet=quiet)
        #self.pos_x = x 
        #self.pos_y = y
        #self.pos_check()
        self.motion_level -= 1
        return              # Processed via pos_check()

    def on_key_press(self, event):
        """ Key press event
        :event: Actual event
        """
        keysym = event.keysym
        ###self.key_press(keysym)
        self.cgd.on_key_down(event)

    def key_press(self, event):
        """ Actual or simulated key event
        :keysym: Symbolic key value/string
        """
        self.cgd.on_key_down(event)
        
    """
    keyboard commands
    """

    def key_unrecognized(self, keyslow):
        """ Process unrecognized key
        :keyslow: key symbol (lower case)
        """
        self.speak_text(f"Don't understand {keyslow}")

    def key_echo(self,keysym):
        """ Echo key, if appropriate
        :keysym; key symbol
        """
        if self._echo_input:
            self.cgd.speaker_control.speak_text(keysym, msg_type='ECHO')

    def key_flush(self, keysym):
        """ Do appropriate flushing
        :keysym: key symbol
        """
        self.escape_pressed = True  # Let folks in prog know
        self._multi_key_progress = False
        self._multi_key_cmd = False
        self.flush_rep_queue()
        self.stop_speak_text()
        self.escape_pressed = False

    def key_escape(self):
        SlTrace.lg("Escape pressed")
        #self._multi_key_progress = False    # Stop multi key processing   
        self.key_flush(keysym="Escape")


    def key_help(self):
        """ Help - list keyboard action
        """
        help_str = """
        h - say this help message
        Escape - flush pending report output
        """
        self.speak_text(help_str)

    def key_exit(self):
        self.speak_text("Quitting Program")
        self.update()     # Process any pending events
        self.cgd.Destroy()
        sys.exit(0)         # Quit  program

    def key_talk(self, val=True):
        """ Enable / Disable talking
        """
        self.do_talking = val
        SlTrace.lg(f"do_talking:{self.do_talking}")

    def win_print(self,*args, dup_stdout=False, **kwargs):
        """ print to listing area
        :*args: print-like args
        :**kwargs: print-flags
        :dup_stdout:  send duplicate to stdout
        """
        lstr = ""
        if "sep" in kwargs:
            sep = kwargs["sep"]
        else:
            sep = " "
        for ls in args:
            lstr += (str(ls)+sep)
        if dup_stdout:
            print(*args, **kwargs)
        ###wxport###self.win_print_entry.delete(0, tk.END)
        ###wxport###self.win_print_entry.insert(0, lstr)
        #time.sleep(.2)


    """
    ############################################################
                       Links to menus
    ############################################################
    """
    def get_menu_scs(self):
        """ Get menu (menubar) short cuts
        """
        return self.menus.get_menu_scs()

    def get_menu_item_scs(self, menu_sc):
        """ Get list of menu item short cuts
        :menu_sc: menu shortcut
        :returns: list of menu itme shortcuts
        """
        return self.menus.get_menu_item_scs(menu_sc)

    def get_menu_cmd(self, menu_sc, mi_sc):
        """ get menu cmd
        :menu_cs: menu shortcut case insensitive
        :mi_cs: menu item shortcut case insensitive
        :returns: menu cmd, if none - None
        """
        return self.menus.get_menu_cmd(menu_sc, mi_sc)
    
     
    def file_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.file_direct_call(short_cut)

    def draw_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.draw_direct_call(short_cut)


    def mag_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.mag_direct_call(short_cut)


    def nav_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.nav_direct_call(short_cut)

    def scan_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.scan_direct_call(short_cut)

    """ End of menus links """


    """
    ############################################################
                       Links to speaker control
    ############################################################
    """


    def get_vol_adj(self):
        """ Get current volume adjustment ??? Thread Safe ???
        :returns: current vol_adjustment in db
        """
        return self.speaker_control.get_vol_adj()

    def set_vol_adj(self, adj=0.0):
        """ Set volume adjustment
        :adj: db adjustment default:0.0
        """
        self.speaker_control.set_vol_adj(adj=adj)

    def raise_vol_adj(self, db_adj=None):
        """ Adjust scanning audio level
        """
        self.speaker_control.raise_vol_adj(db_adj=db_adj)

    def lower_vol_adj(self, db_adj=None):
        """ Adjust scanning audio level
        """
        self.speaker_control.lower_vol_adj(db_adj=db_adj)


    """
    ############################################################
                       Links to cgd
    ############################################################
    """

    def update(self, full=False):
        """ Update display
        """
        self.cgd.update(full=full)

    """ Menus """    
    def cmd_file_open(self, e=None):
        """Select chess game files and load the game
        game files are text files of Portable Game Notation (PGN).
        see: https://www.chess.com/terms/chess-pgn
        """
        self.cgd.cmd_file_open()
                    
    def cmd_file_save(self, e=None):
        self.cgd.cmd_file_save()
        
    def cmd_file_log_file(self, e=None):
        self.cgd.cmd_file_log_file()
    
    def cmd_file_properties_file(self, e=None):
        self.cmd_file_properties_file()
    
    def cmd_file_exit(self, e=None):
        self.cgd.cmd_file_exit()

    def exit(self, rc=None):
        """ Main exit
        """
        self.cgd.exit(rc)

    """ Scanning files """        

    def cmd_scan_help(self, _=None):
        """ Help for Alt-s commands
        """
        """ Help - list command (Alt-s) commands
        """
        self.menus.cmd_scan_help()  # *** Placed in menus

    def cmd_setting_game_start(self, _=None):
        self.cgd.cmd_setting_game_start()

    def cmd_setting_game_end(self, _=None):
        self.cgd.cmd_setting_game_end()

        
    """ Settings """
    def cmd_settings_window(self,_=None):
        self.cgd.cmd_settings_window()
        
    def cmd_setting_print_bd(self,_=None):
        self.cgd.cmd_setting_print_bd()
        
    def cmd_setting_print_bd_no(self,_=None):
        self.cgd.cmd_setting_print_bd_no()
        
    def setting_cmd_print_fend(self,_=None):
        self.cgd.cmd_setting__print_fend()
            
    def cmd_setting_print_fen_no(self,_=None):
        self.cgd.cmd_setting_print_fen_no()
            
    def cmd_setting_move_display(self,_=None):
        self.cgd.cmd_setting_move_display()
       
    def cmd_setting_move_display_no(self,_=None):
        self.cgd.cmd_setting_move_display_no()
            
    def cmd_setting_final_position_display(self,_=None):
        self.cgd.cmd_setting_final_position_display()
            
    def cmd_setting_final_position_display_no(self,_=None):
        self.cgd.cmd_setting_final_position_display_no()

            
    def cmd_setting_loop_interval(self,_=None):
        self.cgd.cmd_setting_loop_interval()
            
    def cmd_setting_stop_on_error(self,_=None):
        self.cgd.cmd_setting_stop_on_error()
            
    def cmd_setting_no_stop_on_error(self,_=None):
        self.cgd.cmd_setting_no_stop_on_error()


    def cmd_settings_help(self,_=None):
        self.cgd.cmd_settings_help()


    """
    Game
    """

    def cmd_game_help(self, _=None):
        """ Help for Alt-g commands
        """
        """ Help - list command (Alt-m) commands
        """
        self.menus.cmd_game_help()  # *** placed in menus
        
    def cmd_new_window(self,_=None):
        self.cgd.cmd_new_window()
        
    def cmd_enter_fen(self,_=None):
        self.cgd.cmd_enter_fen()
        
    def cmd_goto_move(self,_=None):
        self.cgd.cmd_goto_move()
        
    def cmd_print_fen(self,_=None):
        self.cgd.cmd_print_fen()
        
    def cmd_print_game(self,_=None):
        self.cgd.cmd_print_game()
        
    """ 
    Enter Moves
    """
    def cmd_enter_moves_help(self,_=None):
        self.cgd.cmd_enter_moves_help()
        
    def cmd_enter_moves(self,_=None):
        self.cgd.cmd_enter_moves()


    def cmd_scanning_files(self, e=None):
        """ Scan chess files in games directory
        """
        self.cgd.cmd_scanning_files()

    """
    Trace support
    """

    def trace_menu(self, _=None):
        self.tcw = TraceControlWindow()


    
    """ 
    End of menu commands
    """
    
    """ 
    Button commands
    """
    def cmd_btn_move(self, e=None):
        self.cgd.cmd_btn_move()
    
    def cmd_btn_unmove(self, e=None):
        self.cgd.cmd_btn_unmove()

    def cmd_btn_loop(self, e=None):
        self.cgd.cmd_btn_loop()

    def cmd_btn_stop(self, e=None):
        self.cgd.cmd_btn_stop()

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
        self.cgd.speak_text(msg=msg, msg_type=msg_type,
                            dup_stdout=dup_stdout,
                            rate=rate, volume=volume)

    def mainloop(self):
        self.cgd.mainloop()


if __name__ == '__main__':
    '''
    from unittest.mock import MagicMock
    
    class cgdFake(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def exit(self):
            SlTrace.lg("cgd.exit()")
            sys.exit()
        
        def get_ix_min(self):
            return 100
        
        def get_ix_max(self):
            return 0
        
        def bounding_box_ci(self, cells):
            return (100,100, 0, 0)                
    '''
    from wx_chess_game_display import ChessGameDisplay
    from wx_cgd_menus import CgdMenus
                  
    app = wx.App()
    frame = wx.Frame(None)
    ccs = None
    cbs = ChessboardStack()
    cgd = ChessGameDisplay(ccs, cbs, parent=frame)
   
    fte = CgdFrontEnd(cgd)
    menus = CgdMenus(fte, frame=frame)
    ###fte.do_key_str("c;g")
    
    app.MainLoop()
