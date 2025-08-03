# wx_selection_ok.py    18Apr2025  crs, from virtual listCtrl
import wx
import sys, glob, random

from select_trace import SlTrace
from wx_virtual_list_ctl import VirtualListCtrl


class SelectionOK(wx.Frame):

    def __init__(self, parent, dataSource=None, doOK=None, doCancel=None):
        """ Setup access to datasource
        :datasource: (ChessDataSource) data
        :doOK: function to call on OK with selection
        :doCancel: call if cancel
        """
        self.selected_data = None
        self.doOK = doOK
        self.doCancel = doCancel
        
        super().__init__(parent, title='SelectionOK')

        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        title = wx.StaticText(self.panel, wx.ID_ANY, 'SelectionOK')
        
        self.listCtrl = VirtualListCtrl(self.panel, dataSource=dataSource)

        
        okBtn = wx.Button(self.panel, wx.ID_ANY, 'OK')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.onOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        topSizer        = wx.BoxSizer(wx.VERTICAL)
        titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        listCtrlSizer  = wx.BoxSizer(wx.VERTICAL)
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer.Add(title, 0, wx.ALL, 5)

        listCtrlSizer.Add(self.listCtrl, 0, wx.ALL|wx.CENTER|wx.EXPAND, 5) 
        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(listCtrlSizer, 0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)
        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)


    def onOK(self, event):
        # Do something
        print('onOK handler')
        selection = self.getSelection()
        SlTrace.lg(f"selection: {selection}", "display")
        if self.doOK:
            self.closeProgram()
            self.doOK(selection)
            
    def onCancel(self, event):
        self.closeProgram()
        if self.doCancel:
            self.doCancel()
            
    def closeProgram(self):
        self.Close()

    def onItemSelected(self, e):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            # An item is selected
            # Access item data using selected_index
            data = self.listCtrl.GetData(selected_index)
            SlTrace.lg(f"{data = }", "display")
            self.selected_data = data

    def Wait(self):
        """ Wait till ok/cancel
        """
        

    def getSelection(self):
        """ Get selected data
        :returns: selection tuple (,..., game)
                None if none selected
        """
        data = self.selected_data
        self.closeProgram()
        return data
    
                 
# Run the program
if __name__ == '__main__':
    import os
    
    from select_trace import SlTrace
    from chess_game_data_source import ChessGameDataSource
    
    os.chdir(os.path.dirname(__file__))
    game_file = '../games/fischer.pgn'
    SlTrace.lg(f"game_file:{os.path.abspath(game_file)}")
    dataSource = ChessGameDataSource(game_file)
    
    app = wx.App()
    
    sel = SelectionOK(None, dataSource=dataSource)
    sel.Show()
    app.MainLoop()
