#wx_chess_settings_frame.py
""" 
Chess display settings window
TBD load/save settings from properties file
TBD implement do/undo settings
"""
import wx

from graphics_braille.select_trace import SlTrace
from chess_settings_control import ChessSettingsControl
from wx_chess_settings_display import ChessSettingsDisplay

from wx_chess_settings_data_panel import ChessSettingsDataPanel
from wx_chess_settings_control_panel import ChessSettingsControlPanel

        
class ChessSettingsFrame(ChessSettingsDisplay):
    def __init__(self, parent=None, title=None, size=None,
                 control_prefix="CHESS_SETTINGS_FRAME",
                 settings_server=None,
                 update_data_fun=None,
                 update_control_fun=None,
                 onclose=None):
        """
        :parent: containg frame
        :title: optional title
        :size: frame size (wx.Size)
        :control_prefix: properties prefix
        :settings_server:  settings access
                        default: parent
        :update_data_fun: data change function
                        update_data_fun(name, value)
        :update_control_fun: control(e.g. button) function
                        update_control_fun(name)
        :onclose: called, if present when window closes
            Derived class is respnsible for binding window event
            to self.onclose.  self.onclose will pass this call
            to saved onclose(self._onclose) if present
            default: no action 
        """
        if  title is None:
            title = "Game Settings"
        if size is None:
            size = wx.Size(400,400)
        if settings_server is None:
            settings_server = parent
        if control_prefix is None:
            control_prefix = "CHESS_SETTINGS_FRAME"
        self.caller_onclose = onclose     # caller's close out, if any
        
        super().__init__(self,
                    control_prefix=control_prefix,                 
                    update_data_fun=update_data_fun,
                    update_control_fun=update_control_fun,
                    onclose=self.onclose)   # Our win's close
        
        self.settings_control = ChessSettingsControl(settings_display=self,
                                            settings_server=settings_server)
        
    def set_val(self, name, value, update_display=True):
        """ Set settings value, updating display
        :name: settings name
        :value: settings value
        :update_display: update display
            default: True - update display
        """
        self.settings_control.set_val(name=name, value=value, update_display=update_display)        

    def save_vals(self):
        """ Save current settings.  Facilitates
        Undo after composite settings like Fastest_Run
        """
        self.settings_control.save_vals()        

    def onclose(self, event=None):
        """ Our window's close out
        """
        if hasattr(self, "settings_control"):
            self.settings_control.on_close()
        if self.caller_onclose is not None:
            self.caller_onclose()
        SlTrace.lg("self.Destroy()")
        self.Destroy()    
        
    def get_geo_whxy(self):
        """ Obtain geometry of chess settings window
        :returns: list of width,height,x-offset,y-offset ints in pixels
        """
        x,y = self.GetPosition()
        w,h = self.GetSize()
        return w,h,x,y


        
if __name__ == '__main__':
    import sys
    from chess_settings_server import ChessSettingsServer
    
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width, height)
    frame = wx.Frame(None, size=wx.Size(width,height),
                     title="base_frame")
    settings_server = ChessSettingsServer(frame)
    
    def update_data_fun(name, value):
        SlTrace.lg(f"""data_update_fun("{name}", {value})""")
    
    def update_control_fun(name):
        SlTrace.lg(f"""data_control_fun("{name}")""")

    def onclose():
        """ Called if onclose option is present
        """
        SlTrace.lg("onclose - window closed")
        sys.exit(0)
        
    settings_frame = ChessSettingsFrame(frame,
                        title="#wx_chess_settings_frame.py",
                        size=size,
                        settings_server=ChessSettingsServer(),
                        update_data_fun=update_data_fun,
                        update_control_fun=update_control_fun,
                        onclose=onclose
                        ) 
    settings_frame.Show()
    app.MainLoop()  
