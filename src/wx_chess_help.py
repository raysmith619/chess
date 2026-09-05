#wx_chess_help.py  02Aug2026  crs
""" Help for wx_chess 
"""
import wx
from graphics_braille.select_trace import SlTrace

class ChessHelp(wx.Frame):
    def __init__(self, on_key_down=None):
        """ Create a help window
        :on_key_down: optional key down handler
        """
        self.on_key_down = on_key_down
        
        super().__init__(None, title="Chess DisplayHelp",
                         size=(500, 300))

        
        # Create a panel to hold the widgets
        panel = wx.Panel(self)
        
        # Vertical sizer to stack text elements cleanly
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        help_text_ctrl = wx.TextCtrl(
            panel,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE)
        main_sizer.Add(help_text_ctrl, 1, wx.EXPAND|wx.ALL, 5)
        hlpf = help_text_ctrl.GetFont()
        hlpf.SetPointSize(16)
        help_text_ctrl.SetFont(hlpf)
        panel.SetSizer(main_sizer)
        self.Bind(wx.EVT_CHAR_HOOK,
                            self.on_key_down, id=wx.ID_ANY)
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        help_text = r"""Chess Display Help
    Keyboard Shortcuts:
        SPACE - goto to next move
        BACKSPACE - goto to previous move
        <number> [W or B] [G or Return]    goto to move number, white or black
        D - rotate move direction display
        L - loop moves
        S - stop looping moves
        F - Flip move back and forth
        P - print current move per ChessGotoMove
        Q - print current move per ChessGameDisplay
        X - quit chess display
        
        
        
    Mouse:
        left-click - on move to go to that move
"""
        help_text_ctrl.SetValue(help_text)
        self.Show()
        
    def on_key_down(self, event):
        # Get the code of the pressed key
        key_code = event.GetKeyCode()
        
        # Check for specific keys (e.g., Escape, Arrow keys, or standard characters)
        if key_code == wx.WXK_ESCAPE:
            print("Escape pressed - Closing Frame")
            self.Close()
        elif key_code == wx.WXK_DOWN:
            print("Down Arrow pressed")
        else:
            print(f"Key pressed. KeyCode: {key_code}")
            
        # Always allow the event to propagate so child widgets function normally
        event.Skip()

    def on_window_close(self,event=None):
        SlTrace.lg("wx_chess_help.on_window_close")
        self.Destroy()
    

        
if __name__ == "__main__":
    def on_key_down(event):
        key = event.GetKeyCode()
        print(f"on_key_down:{key=}"
              f" {chr(key)=}")
        
    app = wx.App(False)
    frame = ChessHelp()
    app.MainLoop()