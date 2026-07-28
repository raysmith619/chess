#wx_chess_settings_frame_test.py   09Aug2025  crs
""" Test of SettingFrame 
Demonstrating connection from display to settings storage
"""
import os
import wx

from select_trace import SlTrace, SelectError

from wx_chess_settings_frame import ChessSettingsFrame

from settings_control import SettingsControl
from display_control import DisplayControl

class ChessSettingsFrameTest:
    def __init__(self, chess_settings, title=None):
        # Mimic game data
        self.setting_game_start_no = 1
        self.setting_game_end_no = None # No limit
        self.setting_is_move_display = True
        self.setting_is_final_position_display = True
        self.setting_is_printing_board = True
        self.setting_is_printing_fen = True
        self.loop_interval = 250    # msec loop interval

        self.settings_frame = chess_settings
        self.settings_frame.Show()
        
        # combination settings
        self.settings_is_shortest_move = False
        self.settings_is_fastest_run = False
        
        self.setup_settings()


    """ More mimicing
    
    Settings with explicit get/set functions
    "Use Shortest Move Interval" :
    """
    
    def get_shortest_move(self):
        return self.settings_is_shortest_move
    
    def set_shortest_move(self, value=True):
        self.settings_is_shortest_move = value
        self.setting_move_interval = 2
        
    def get_fastest_run(self):
        return self.settings_use_fastest_run

    # settings before use_fastest_run
    old_setting_is_move_display = True
    old_setting_is_printing_board = False
    old_setting_is_printing_fen = False
    old_loop_interval = 250    # msec loop interval
    def set_fastest_run(self, value=True):
        self.settings_use_fastest_run = value
        if value:
            old_setting_is_move_display = self.setting_is_move_display
            old_setting_is_printing_board = self.setting_is_printing_board
            old_setting_is_printing_fen = self.setting_is_printing_fen
            old_loop_interval = self.loop_interval
            self.setting_is_move_display = False
            self.setting_is_printing_board = False
            self.setting_is_printing_fen = False
            self.loop_interval = 1    # msec loop interval
        else:
            self.setting_is_move_display = old_setting_is_move_display
            self.setting_is_printing_board = old_setting_is_printing_board
            self.setting_is_printing_fen = old_setting_is_printing_fen
            self.loop_interval = old_loop_interval
                
        return self.settings_use_fastest_run
    
    def setup_settings(self):
        """ Setup run settings
        """
            
        def update_data_fun(name, value):
            SlTrace.lg(f"""data_update_fun("{name}", {value})""")
        
        def update_control_fun(name):
            SlTrace.lg(f"""data_control_fun("{name}")""")

        settings_frame = ChessSettingsFrame(frame,
                            title="wx_settings_frame2",
                            size=size,
                            update_data_fun=update_data_fun,
                            update_control_fun=update_control_fun
                            ) 

        
        self.chess_settings_frame = ChessSettingsFrame(
            parent=None, title="Chess Settings",)
        self.display_control = DisplayControl()
        """ Setup a group of settings
        :main_obj: main running object
        :set_dict: dictionary by Name:
                fields:
                    value:
                        default: getattr(main_obj, attr)
                    value_type: (default: type(value))
                    attr:
                        or
                    get_fun:
                    set_fun
                    if  attr present generate get_fun...
                    else use get_fun,set_fun
        """
        dict_name_setting = {
            "Print Board" :
                {"attr" : "setting_is_printing_board"},
            "Print FEN" :
                {"attr" : "setting_is_printing_fen"},
            "Display Move" :
                {"attr" : "setting_is_move_display"},
            "Display Final Position" :
                {"attr" : "setting_is_final_position_display"},
            "Stop on Error" :
                {"attr" : "setting_is_stop_on_error"},
            "Use Shortest Move Interval" :
                {"get_fun" : self.get_shortest_move,
                "set_fun" : self.set_shortest_move},
            "Set FASTEST Run" :
                {"get_fun" : self.get_fastest_run,
                "set_fun" : self.set_fastest_run},
        }
        self.settings_control.make_setting_group(
            service_obj=self, setting_dict=
                    dict_name_setting)

        
if __name__ == '__main__':
    title = os.path.basename(__file__)
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width, height)
    frame = wx.Frame(None, size=wx.Size(width,height),
                     title=title)
    
    chess_settings_frame = ChessSettingsFrame(frame,
                                title=title, size=size)
    display_control = DisplayControl(settings_control=
                                     chess_settings_frame)
    chess_settings_frame.setup_display_control(display_control)
    test_win = ChessSettingsFrameTest(
                chess_settings=chess_settings_frame,
                title=title) 

    app.MainLoop()  
