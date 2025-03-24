# file_scanning.py  21Oct2026  crs, Testing Git
#                   10Sep2026  crs, Pulled from wx_chess_game_display.py
""" Furnish support to scan chess files
"""
import os

import pgn

from graphics_braille.select_trace import SlTrace

class FileScanning:
    def __init__(self, files=None, errors_dir=None):
        """ Support file scanning for PGN chess files
        :files: list of files to scan
            default: no files, not scanning
        :errors_dir: error file destination 
            default: ../errors
        :
        """
        self.scan_nfile = 0
        self.scan_ngame = 0
        self.scan_nmove = 0
        self.scan_files(files)
        
    def scan_files(self, files=None):
        """ Scan list of files
        :files: list of files
            default: no files scanned
        """
        self.scan_files_iter = iter([])
        self.set_scanning(False)
        self.set_scanning_paused(False)
        if files is None:
            return
                   
        self.scan_files_iter = iter(files)        
        self.scan_games_iter = iter([])     # Start file
        self.scan_moves_iter = iter([])     # Start game
        self.set_scanning()                 # Set scanning
 
    def scan_desc(self):
        """ Return current scanning description
            e.g <fileno>: <basename> <gameno>:
            """
        st = f"{self.scan_nfile}: {os.path.basename(self.scan_file_name)}"
        st += f" {self.scan_ngame}"
        return st
        
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
        SlTrace.lg(f"\nFile {self.scan_nfile:2}: {file}", "verbose")
        self.scan_file_name = file
        with open(file) as game_file:
            pgn_text = game_file.read()
            self.pgn_games = pgn.loads(pgn_text) # Returns a list of PGNGame
            self.scan_games_iter = iter(self.pgn_games)
        return file

    def set_scanning(self, scanning=True):
        """ Set scanning
        :scanning: scanning level default: True
        """
        self._is_scanning = scanning
        
    def is_scanning(self):
        """ Check scanning level
        :return: True iff scanning
        """
        return self._is_scanning

    def set_scanning_paused(self, scanning=True):
        """ Set scanning
        :scanning: scanning level default: True
        """
        self._is_scanning_paused = scanning
        
    def is_scanning_paused(self):
        """ Check scanning level
        :return: True iff scanning
        """
        return self._is_scanning_paused
           
        
    def scan_get_game(self):
        """ Get next game, None if no more
        :returns: PgnGame, else None if no more games
        """
        try:
            game = next(self.scan_games_iter)
            self.scan_ngame += 1
            self.scan_moves_iter = iter(game.moves)
            self.scan_game = game
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
            return None

    
    def next_move(self, new_game_fun=None,
                  new_file_fun=None,
                  end_scan_fun=None):
        """ Get next chess move from scan files
        Processes all moves, calling appropriate functions at
        breaks.
        :new_game_fun(game): called before new game
        :new_file_fun: called before new  file
        :end_scan_fun called at end of scan
        :returns: move specification
                None if none
        """
        while True:
            self.move = self.scan_get_move()
            if self.move is not None:
                return self.move
            
            self.game = self.scan_get_game()
            if self.game is not None:
                new_game_fun(self.game)
                continue
            
            self.file_name = self.scan_get_file()
            if self.file_name is not None:
                new_file_fun(self.file_name)
                continue
            break
                    
                    

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
    #show = ["file"]

    def test_file_game_move():
        SlTrace.lg("Test get_file get_game get_move")
        nfile = 0
        ngame = 0
        nmove = 0
        while True:
            file_name = fs.scan_get_file()
            if file_name is None:
                SlTrace.lg("End of files")
                break
            
            nfile += 1
            if "file" in show:
                SlTrace.lg(f"{os.path.basename(file_name)}"
                           f" {fs.scan_nfile: } {file_name}", "fs")
            while True:
                game = fs.scan_get_game()
                if game is None:
                    SlTrace.lg(f"End of File {fs.scan_ngame} games", "fs")
                    break
                
                ngame += 1
                if "game" in show:
                    SlTrace.lg(f"{os.path.basename(file_name)} {fs.scan_nfile: }"
                            f" {fs.scan_ngame}: {game.white} vs {game.black}")

                while True:
                    move_spec = fs.scan_get_move()
                    if move_spec is None:
                        if "move" in show:
                            SlTrace.lg(f"End of game {nmove = }", "fs")
                        break
                    
                    nmove += 1

        SlTrace.lg(f"{nfile} files  {ngame}  games  {nmove} moves")                
            
    test_file_game_move()


    nfile = 0
    ngame = 0
    nmove = 0
    def test_next_move():
        SlTrace.lg("Test next_move", "fs")
        def end_scan():
            SlTrace.lg("End of Scan")
            
        def new_game(game):
            global ngame
            ngame += 1
            if "game" in show:
                SlTrace.lg(f"New game Scanning {fs.scan_desc()}", "fs")
        
        def new_file(file_name):
            global nfile
            nfile += 1
            if "file" in show:
                SlTrace.lg(f"New file {nfile}: {file_name}", "fs")
            
        fs = FileScanning()
        fs.scan_files(files)
        while (move := fs.next_move(new_game, new_file, end_scan)):
            global nmove
            nmove += 1


        SlTrace.lg(f"{nfile} files  {ngame}  games  {nmove} moves")                
            
    test_next_move()
                
    
        