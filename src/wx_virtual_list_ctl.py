# wx_virtual_list_ctl.py    18Apr2025  crs, from wxPython in Action
import wx
import sys, glob, random


class VirtualListCtrl(wx.ListCtrl):
    """
    A generic virtual listctrl that fetches data from a DataSource.
    """
    def __init__(self, parent, dataSource):
        wx.ListCtrl.__init__(self, parent,
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VIRTUAL)
        self.dataSource = dataSource
        self.Bind(wx.EVT_LIST_CACHE_HINT, self.DoCacheItems)
        self.SetItemCount(dataSource.GetCount())

        columns = dataSource.GetColumnHeaders()
        for col, text in enumerate(columns):
            self.InsertColumn(col, text)
        

    def DoCacheItems(self, evt):
        self.dataSource.UpdateCache(
            evt.GetCacheFrom(), evt.GetCacheTo())

    def OnGetItemText(self, item, col):
        data = self.dataSource.GetItem(item)
        return str(data[col])

    def OnGetItem(self, item, col):
        data = self.dataSource.GetItem(item)
        return str(data[col])

    def GetData(self, item):
        data = self.dataSource.GetItem(item)
        return data
    
    def OnGetItemAttr(self, item):  return None
    def OnGetItemImage(self, item): return -1

if __name__ == '__main__':
    import os
    
    from select_trace import SlTrace
    
    from chess_game_data_source import ChessGameDataSource
    
        
    os.chdir(os.path.dirname(__file__))
    game_file = '../games/fischer.pgn'
    SlTrace.lg(f"game_file:{os.path.abspath(game_file)}")
        
    class DemoFrame(wx.Frame):
        def __init__(self, ):
            wx.Frame.__init__(self, None, -1,
                            "Virtual wx.ListCtrl",
                            size=(600,400))

            self.list = VirtualListCtrl(self, ChessGameDataSource(game_file))



    app = wx.App()
    frame = DemoFrame()
    frame.Show()
    app.MainLoop()
