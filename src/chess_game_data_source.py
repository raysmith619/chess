# chess_game_data_source.py 16Apr2025  crs, from wxPython in Action
import wx

import pgn

from select_trace import SlTrace

class ChessGameDataSource:
    """
    A simple data source class that just uses our sample data items.
    A real data source class would manage fetching items from a
    database or similar.
    """
    columns = ["Index", "white", "black", "date", "result"]
    
    def __init__(self, game_file_name, columns=None):
        """ Setup file game access
        :game_file_name: game file path
        :columns: data displayed
            default use given
            "Index" is game position in file, starting at 1
            rest are attributes in pgn
            
        """
        try:
            game_file = open(game_file_name, 'r')
            
        except IOError:
            wx.LogError("Cannot open file '%s'." % game_file_name)
            return
        
        pgn_text = game_file.read()

        pgn_games = pgn.loads(pgn_text) # Returns a list of PGNGame
        self.game_selections = []
        self.games_by_selection = {}     # Unique selections ???
        
        max_g = 10000
        
        for game_index, pgn_game in enumerate(pgn_games):
            n = game_index + 1
            self.game_selections.append((n, pgn_game))

        
    def GetColumnHeaders(self):
        return self.columns

    def GetCount(self):
        return len(self.game_selections)

    def GetItem(self, index):
        """ Get item - tuple of data for columns selection
        :index: raw index into full list
        """
        row = self.game_selections[index]
        row_index = row[0]
        row_game = row[1]
        item_l =  []
        for column in self.columns:
            if column == "Index":
                item_l.append(row_index)
            else:
                if hasattr(row_game, column):
                    item_l.append(getattr(row_game, column))
                else:
                    item_l.append("???")
        item_l.append(row_game)            
        return tuple(item_l)

    def UpdateCache(self, start, end):
        pass
    
if __name__ == '__main__':
    import os
    
    os.chdir(os.path.dirname(__file__))
    game_file = '../games/fischer.pgn'
    SlTrace.lg(f"game_file:{os.path.abspath(game_file)}")

    data_limit = 10
    game_data = ChessGameDataSource(game_file)
    ndata = game_data.GetCount()
    SlTrace.lg(f"Data Count: {ndata}")
    SlTrace.lg(f"headings: {game_data.GetColumnHeaders()}")
    for i in range(data_limit):
        data = game_data.GetItem(i)
        SlTrace.lg(f"{ data =}")
    