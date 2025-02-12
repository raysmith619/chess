# chessbord_display_print.py    10Feb2025  crs
""" "Display" chess board via printing
especially for blind
"""
class ChessboardDisplayPrint:
    def __init__(self,
                 board,
                 sq_size = 80,
                 light_sq = "#fc9",        # tan
                 dark_sq = "#a65",         # brown
                 #light_sq = "#ffffff",      # white
                 #dark_sq = "#769656",       # green
                ):
        self.board = board

    def display_board(self, mw=None, include_pieces=True):
        """ Display board
        """    

    def display_pieces(self, piece_squares=None):
        """ Display pieces
        :piece_squares: list of piece_squares to display
            default: use board.setting
        """
        if piece_squares is None:
            piece_squares = self.board.get_board_pieces()
        for ps in piece_squares:
            self.display_piece_square(ps)
    