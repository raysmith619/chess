# file_scanning.py   10Sep2026  crs, Pulled from wx_chess_game_display.py
""" Furnish support to scan chess files
"""
from graphics_braille.select_trace import SlTrace
from central_data import CentralData

class FileScanning:
    def __init__(self, cdata, file_dir=None, errors_dir=None):
        """ Support file scanning for PGN chess files
        :cdata: central data control CentralData
        :file_dir: chess file directory
            default: ../games
        :errors_dir: error file destination 
            default: ../errors
        :
        """
        self.cdata = cdata
    
    def scan_files(self, files,
                   display_interval=.250,
                   next_move_fun=None,
                   start_scan_fun=None,
                   end_scan_fun=None,
                   start_file_fun=None,
                   end_file_fun=None,
                   start_game_fun=None,
                   end_game_fun=None):
        """ Scan chess (Portable Game Notation (PGN))
        files, providing move, game, and file information
        as accessed.  The goal is to facilitate the
        display of games as files are processed.

        Support pausing,stopping restart game display
        
        which advances one chess move(one-ply)
        call next_move (default: get next move)
        If at end of game, call end_game (default: get next game)
        If at end of file, call end_file (default: get next file)
        If at end of file list stop scanning
        
        :files: list of files/directories
        :display_interval: call next_move_fun every
            display_interval seconds default:.250 seconds
        :next_move_fun: function called with move spec
            fn(move_spec) e.g., central_data.py chess_move()
        
        :start_scan_fun:  function called at start of scan
            default: call self.start_scan
                    which starts scanning
        
        :end_scan_fun:  function called at end of scan
            default: call self.end_scan
                    which stops scanning
        
        :start_file_fun; function called at file start
            default: self.start_file(file_name)
                
        :end_file_fun: function called at file end
            default: call self.end_file()

        :start_game_fun: function called at game begin
            default: self.start_game(game PGN)
            
        :end_game_fun: function called at game end
            fn() e.g., 
            default: start next game else call end_file_fun
                    self.end_game() which calls new_game_fun()
                
        """
        if next_move_fun is None:
            next_move_fun = self.next_move
        self.next_move_fun = self.next_move_fun
        
        if next_move_fun is None:
            next_move_fun = self.next_move
        self.next_move_fun = self.next_move_fun
        
        
        if end_game_fun is None:
            end_game_fun = self.end_game
        self.end_file_fun = end_game_fun
        if end_file_fun is None:
            end_file_fun = self.end_file
        self.end_file_fun = end_file_fun
        self.is_scanning = True
        self.end_file_fun() # Start with first file

    def next_move(self):
        self.cdata.chess_move()
                
    def end_game(self):
        """ Default end-game processing
        """

if __name__ == '__main__':
    import wx
    
    class TestFileScanning:
        def __init__(self, file_scanning):
            self.file_scanning = file_scanning
        
        def scan(self):
            self.cmd_scanning_files()
            

        def cmd_scanning_files(self, e=None):
            """ Scan chess files in games directory
            """
            dlg = wx.FileDialog(None, "Scanning Directory",
                                wildcard="All files (*.pgn)|*.pgn",
                            style=wx.FD_MULTIPLE)
            ans = dlg.ShowModal()
            if ans != wx.ID_OK:
                SlTrace.lg("Directory not selected")
                return
            
            files = dlg.GetPaths()
            self.is_scanning = True     # Scanning files in progress
            self.scan_loops = 0         # Keep count
            SlTrace.lg(f"cmd_scanning_files:\n {'\n'.join(files)=}")
            self.file_scanning.scan_files(files=files)

    app = wx.App()
    
    cd  = CentralData()
    fs = FileScanning(cd)
    tfs = TestFileScanning(fs)
    tfs.scan()
    
        