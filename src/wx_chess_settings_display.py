#wx_chess_settings_display.py
""" 
Chess settings display (SettingsDisplay)
Converted from wx_settings_display_demo.py
May compress SettingsDisplay->SettingsDisplayBase->ChessSettingsDisplay...
wxPython version of settings frame

TBD load/save settings from properties file
TBD implement do/undo settings
"""
import wx

from graphics_braille.select_trace import SlTrace
from graphics_braille.settings_display import SettingsDisplay

from graphics_braille.wx_settings_display_base import SettingsDisplayBase
from wx_chess_settings_data_panel import ChessSettingsDataPanel
from wx_chess_settings_control_panel import ChessSettingsControlPanel

        
class ChessSettingsDisplay(SettingsDisplayBase):
    def __init__(self, parent=None, title=None, size=None,
                control_prefix="CHESS_SETTINGS_DISPLAY",                 
                data_panel_type=ChessSettingsDataPanel,
                control_panel_type=ChessSettingsControlPanel,
                update_data_fun=None,
                update_control_fun=None,
                onclose=None):
        """
        :parent: containg frame
        :title: optional title
        :size: frame size (wx.Size)
        :control_prefix: properties prefix
        :data_panel_type: settings data panel class
                    default: ChessSettingsDataPanel,
        :control_panel_type: settings control(button) panel class
                    default: ChessSettingsControlPanel,
        :update_data_fun: data change function
                        update_data_fun(name, value)
        :update_control_fun: control(e.g. button) function
                        update_control_fun(name)
        :onclose: call on window closure
                default: no action
        """
        if size is None:
            size = wx.Size(400,400)
        if data_panel_type is None:
           data_panel_type = ChessSettingsDataPanel 
        if control_panel_type is None:
           control_panel_type = ChessSettingsControlPanel 
        SettingsDisplayBase.__init__(self,
                data_panel_type=data_panel_type,
                control_panel_type=control_panel_type,
                update_data_fun=update_data_fun,
                update_control_fun=update_control_fun,
                onclose=onclose)
        self.Bind(wx.EVT_CLOSE, self.onclose)   # For SettingsDisplay

        self.control_prefix = control_prefix
       
if __name__ == '__main__':
    import os
    import sys
    
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width, height)
    frame = wx.Frame(None, size=wx.Size(width,height),
                     title="base_frame")
    
    def update_data_fun(name, value):
        SlTrace.lg(f"{os.path.basename(__file__)}:"
                   f" update_data_fun(\"{name}\", {value})")
    
    def update_control_fun(name):
        SlTrace.lg(f"{os.path.basename(__file__)}"
                   f" update_control_fun(\"{name}\")")


    def onclose():
        """ Called when demo window closes
        """
        SlTrace.lg("settings_frame closed")
        sys.exit(0)
        
    settings_frame = ChessSettingsDisplay(frame,
                        title="Chess Settings",
                        size=size,
                        update_data_fun=update_data_fun,
                        update_control_fun=update_control_fun,
                        onclose=onclose
                        )

    app.MainLoop()  
