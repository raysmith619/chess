# chess_game_access.py  07Sep2026  crs, Author
"""
This module provides access to chess games
Initially it will be a simple in-memory store,
but later it may access internet 
"""
import pgn

class ChessGameAccess:
    def __init__(self, game_dir=None,
                 error_dir=None,
                 new_file_fun=None):
        """ Access  to chess games (PGN)"""
        self.game_dir = game_dir
        self.error_dir = error_dir

    def get_games(self, file, next_game_fun=None):
        """ Get next game
        :returns: (next game (PGN), None if end of file
        """        
    def get_game_iterator(self):
        """
        Returns an iterator over chess games
        """
        return pgn.get_game_iterator(self.game_dir, self.error_dir)
    