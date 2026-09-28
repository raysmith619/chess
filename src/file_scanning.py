# file_scanning.py   10Sep2026  crs, Pulled from wx_chess_game_display.py
""" Furnish support to scan chess files
"""
import pgn

from graphics_braille.select_trace import SlTrace

class FileScanning:
    def __init__(self, files=None, errors_dir=None):
        """ Support file scanning for PGN chess files
        :cdata: central data control CentralData
        :file_dir: chess file directory
            default: ../games
        :errors_dir: error file destination 
            default: ../errors
        :
        """
        self.scan_nfile = 0
        self.scan_ngame = 0
        self.scan_nmove = 0
        self.scan_files_iter = iter(files)
        self.scan_games_iter = iter([])     # Start file
        self.scan_moves_iter = iter([])     # Start game
 
    def scan_get_file(self):
        """ Get next file, None if no more
        :returns: file_path, else None if nomore files
        """
        try:
            file = next(self.scan_files_iter)
        except StopIteration:
            return None
        
        
        self.scan_nfile += 1
        self.scan_ngame = 0
        self.scan_nmove = 0
        SlTrace.lg(f"\nFile {self.scan_nfile:2}: {file}")
        with open(file) as game_file:
            self.scan_file_name = file
            pgn_text = game_file.read()
            self.pgn_games = pgn.loads(pgn_text) # Returns a list of PGNGame
            self.scan_games_iter = iter(self.pgn_games)
        return file
        
        
    def scan_get_game(self):
        """ Get next game, None if no more
        :returns: PgnGame, else None if no more games
        """
        try:
            game = next(self.scan_games_iter)
            self.scan_ngame += 1
            self.scan_moves_iter = iter(game.moves)
            return game
        
        except StopIteration:
            return None
        
    def scan_get_move(self):
        """ Get next move from scanning
        :returns: move, None if end of game
        """
        try:
            move = next(self.scan_moves_iter)
            self.scan_nmove += 1                    
            return move
            
        except StopIteration:
            self.scan_moves_iter = None
            return None


if __name__ == '__main__':
    import os
    import sys
    import wx

    app = wx.App()
    SlTrace.lg("Test FileScanning")
    dlg = wx.FileDialog(None, "Scanning Directory",
                        wildcard="All files (*.pgn)|*.pgn",
                    style=wx.FD_MULTIPLE)
    ans = dlg.ShowModal()
    if ans != wx.ID_OK:
        SlTrace.lg("Directory not selected")
        sys.exit()
        
    files = dlg.GetPaths()
    fs = FileScanning(files=files)
    nfile = 0
    ngame = 0
    show = ["file", "game", "move"]
    show = ["file"]
    while True:
        file_name = fs.scan_get_file()
        if file_name is None:
            SlTrace.lg("End of files")
            break
        
        nfile += 1
        if "file" in show:
            SlTrace.lg(f"{os.path.basename(file_name)} {fs.scan_nfile: } {file_name}")
        while True:
            game = fs.scan_get_game()
            if game is None:
                SlTrace.lg(f"End of File {fs.scan_ngame} games")
                break
            
            ngame += 1
            if "game" in show:
                SlTrace.lg(f"{os.path.basename(file_name)} {fs.scan_nfile: }"
                        f" {fs.scan_ngame}: {game.white} vs {game.black}")

            nmove = 0
            while True:
                move_spec = fs.scan_get_move()
                if move_spec is None:
                    if "move" in show:
                        SlTrace.lg(f"End of game {nmove = }")
                    break
                
                nmove += 1

    SlTrace.lg(f"{nfile} files {ngame} games")                
            
                
    
        