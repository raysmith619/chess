# chess_settings_control.py
"""
Adapted from settings_control.py

Facilitates
    setting and retrieving settings
    persistent storage of values
"""
import re
import copy


from graphics_braille.select_error import SelectError
from graphics_braille.select_trace import SlTrace
from graphics_braille.setting import Setting
from graphics_braille.settings_control import SettingsControl
from chess_settings_server import ChessSettingsServer
from wx_chess_settings_display import ChessSettingsDisplay
    
class ChessSettingsControl(SettingsControl):
    CONTROL_NAME_PREFIX = "CHESS_SETTINGS_CONTROL"
    def __init__(self,
                settings_server=None,
                settings_display=None,
                settings_dict=None,
                control_prefix=None,
                update_report=None,
                 ):
        """ Setup data control and access
        :settings_server: holder of setting variables/access
        :settings_display: settings display and input
        :settings_dict: dictionary by setting name of setup,
                        access
        :control_prefix: properties storage name prefix
        :update_report: update trace function
                        default: no report
        """
        settings_def_dict = {
                "Display_Move_Direction" :
                    {"attr" : "setting_is_display_move_direction"},
                "Print_Board" :
                    {"attr" : "setting_is_printing_board"},
                "Print_FEN" :
                    {"attr" : "setting_is_printing_fen"},
                "Display_Move" :
                    {"attr" : "setting_is_move_display"},
                "Display_Final_Position" :
                    {"attr" : "setting_is_final_position_display"},
                "Stop_on_Error" :
                    {"attr" : "setting_is_stop_on_error"},
                "Use_Shortest_Move_Interval" :
                    {"get_fun" : settings_server.get_shortest_move,
                    "set_fun" : settings_server.set_shortest_move},
                "Set_FASTEST_Run" :
                {"__not_data__" : True, # Don't save/restore
                "get_fun" : settings_server.get_fastest_run,
                    "set_fun" : settings_server.set_fastest_run},
                "Move_Interval" :
                    {"attr" : "loop_interval"},
                }
        if settings_server is None:
            settings_server = ChessSettingsServer()
        if settings_display is None:
            settings_display = ChessSettingsDisplay()
            
        if settings_dict is None:
            settings_dict = settings_def_dict
            
        super().__init__(
                         settings_server=settings_server,
                         settings_display=settings_display,
                         settings_dict=settings_dict,
                         control_prefix=control_prefix,
                         update_report=update_report)
    
            
if __name__ == '__main__':
    import sys
    import argparse
    import wx
    
    app = wx.App()
    from wx_settings_display_base import SettingsDisplayBase
    
    SlTrace.setProps()
    SlTrace.clearFlags()
    class TestFrame(wx.Frame):
        def __init__(self,
            parent=None,
            width=400,
            height=400,
            size=None):
            if size is None:
                size = wx.Size(width, height)
            super().__init__(parent)
            self.Bind(wx.EVT_CLOSE, self.on_close)
            settings_server = ChessSettingsServer()
            settings_display = ChessSettingsDisplay(parent)
            self.settings_control = SettingsControl(
                settings_server=settings_server,
                settings_display=settings_display)
            
        def on_close(self, event=None):
            SlTrace.lg("SettingsControl closing")
            self.settings_control.on_close()
            SlTrace.onexit()
            sys.exit()    
                
                
            
    tF = TestFrame(None)
    
    app.MainLoop()
    SlTrace.lg("After app.MainLoop")
    tF.on_close()
    