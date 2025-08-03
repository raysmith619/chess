import wx
import sys, glob, random
import data

class GamelListCtrl(wx.ListCtrl):
    """
    A Game list that fetches data from a GameDataSource.
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
        return data[col]

    def OnGetItemAttr(self, item):  return None
    def OnGetItemImage(self, item): return -1

        

class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          "Virtual wx.ListCtrl",
                          size=(600,400))

        self.list = VirtualListCtrl(self, DataSource())



app = wx.PySimpleApp()
frame = DemoFrame()
frame.Show()
app.MainLoop()
