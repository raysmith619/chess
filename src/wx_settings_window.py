#wx_settings_window.py
""" 
Chess display settings in popup window
TBD load/save settings from properties file
TBD implement do/undo settings
"""
import wx

from graphics_braille.select_trace import SlTrace

class SettingsWindow(wx.PopupWindow):
    def __init__(self, parent=None, title=None,
                 position=None, size=None):
        """ :parent: containg frame
            :title: Descriptive title
            :position: on screen wx.Point
                    default: x:200, y:200
            :size: width,height wx.Size
        """
        if position is None:
            position = wx.Point(200,200)
        if size is None:
            size = wx.Size(100, 150)
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour("red"))
        self.Position(position, size)
        panel_color = wx.Colour("blue")
        settings_panel = wx.Panel(self, size=size)
        settings_panel.SetBackgroundColour(panel_color)
        settings_panel.Show()
        cb_color = wx.Colour("violet")
        settings_panel.Show()
        panel_sizer = wx.BoxSizer()
        panel_sizer.Add(settings_panel,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(panel_sizer)
        
        settings_sizer = wx.BoxSizer(wx.VERTICAL)

        self.cb_display_move_direction = wx.CheckBox(settings_panel, -1,
                                           "Display Move Direction")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_display_move_direction,
                  self.cb_display_move_direction)
        self.cb_display_move_direction.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_display_move_direction,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)

        self.cb_print_board = wx.CheckBox(settings_panel, -1,
                                          "Print Board")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_print_board,
                  self.cb_print_board)
        self.cb_print_board.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_print_board,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)

        self.cb_print_fen = wx.CheckBox(settings_panel, -1,
                    "Print FEN")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_print_fen,
                  self.cb_print_fen)
        self.cb_print_fen.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_print_fen,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)

        self.cb_display_move = wx.CheckBox(settings_panel, -1,
                                           "Display Move")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_display_move,
                  self.cb_display_move)
        self.cb_display_move.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_display_move,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)

        self.cb_display_final_pos = wx.CheckBox(settings_panel, -1,
                                           "Display Final Position")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_display_final_pos,
                  self.cb_display_final_pos)
        self.cb_display_final_pos.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_display_final_pos,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)

        self.cb_stop_on_error = wx.CheckBox(settings_panel, -1,
                    "Stop on Error")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_stop_on_error,
                  self.cb_stop_on_error)
        self.cb_stop_on_error.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_stop_on_error,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)

        self.cb_shortest_move_interval = wx.CheckBox(settings_panel, -1,
                    "Use Shortest Move Interval")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_shortest_move_interval,
                  self.cb_shortest_move_interval)
        self.cb_shortest_move_interval.SetForegroundColour(cb_color)
        settings_sizer.Add(self.cb_shortest_move_interval,proportion=0,
                           flag=wx.EXPAND | wx.ALL, border=5)
        
        settings_panel.SetSizer(settings_sizer)
        x0 = y0 = 200
        w = h = 200
        self.Position(wx.Point(x0,y0),wx.Size(w,h))
        self.Show()

    """ Settings panel event functions
    """
    
    def cmd_print_board(self, event=None):
        val = self.cb_print_board.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Print_board")
    
    def cmd_display_move_direction(self, event=None):
        val = self.cb_display_move_direction.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Display Move Direction")
    
    def cmd_display_move(self, event=None):
        val = self.cb_display_move.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Display Move")
    
    def cmd_display_final_pos(self, event=None):
        val = self.cb_display_final_pos.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Display Final Position")
    
    def cmd_stop_on_error(self, event=None):
        val = self.cb_stop_on_error.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Stop on Error")
    
    def cmd_print_fen(self, event=None):
        val = self.cb_print_fen.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Print FEN")
    
    def cmd_shortest_move_interval(self, event=None):
        val = self.cb_shortest_move_interval.GetValue()
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + "Use Shortest Move Interval")

if __name__ == '__main__':
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width, height)
    frame = wx.Frame(None, size=size)
    #frame.SetBackgroundColour(wx.Colour("green"))
    frame.Show()
    settings_win = SettingsWindow(frame, "SettingsFrame",
                                  size=size) 
    app.MainLoop()  
