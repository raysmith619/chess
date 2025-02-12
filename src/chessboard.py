#chessboard.py 10Feb2025  crs
import re

"""
Experimentation of manipulation of a chess board
Goals:
    efficient display
    efficient access
"""
from chess_piece_images import ChessPieceImages
from select_trace import SlTrace

class Chessboard:
    def __init__(self,
                 pieces = None,
                 base_board = None,
                 nsqx = 8,
                 nsqy = 8,
                 to_move = "white"
                ):
        """ Setup board, optional display
        :pieces: pieces to add
                1. Short hand string :(<piece><square>)* <to move> 
                    where <piece> is [KQRBNPkqrbnp] as in FEN
                    where <square> is Algebraic notaion, e.g. e4
                    where <to move> is w for white, b for black
                    OR
                2. FEN:<FEN string>
                default: No additional pieces added
                    FEN is the abbreviation of Forsyth-Edwards Notation,
                    and it is the standard notation to describe positions
                    of a chess game.
                    
        :base_board: Chess board on which this is based
                default: None - no base
        :nsqx: Number of squares horizontal
                default: 8
        :nsqy: Number of squares vertical
                default: 8
        """
        self.pieces = pieces
        self.piece_squares = []    # Initial list of pieces, if any
        
        self.base_board = base_board
        self.nsqx = nsqx
        self.nsqy = nsqy
        self.to_move = to_move
        self.setup_board()

    def setup_board(self):
        """ Set board internals
        especially board for efficient access to board contents
        """        
        piece_string = self.pieces
        self.clear_board()               
        if piece_string is None or piece_string == "":
            return      # No pieces
        
        if piece_string[0] == ":":  # Check for short form
            short_string = piece_string[1:]
            match_pieces = list(re.finditer(r'([KQRBNPkqrbnp]([a-h])([1-8]))', short_string))
            if not match_pieces:                
                SlTrace.lg(f"short_string: {short_string} is not proper syntax")
                raise Exception(f"short_string: '{short_string}' is not proper piece-square syntax")
            last_piece = match_pieces[-1]
            end_pieces = last_piece.end()
            piece_squares = []
            SlTrace.lg(f"match groups:{match_pieces}")
            to_move_str = short_string[end_pieces:]
            SlTrace.lg(f"pieces:{short_string[:end_pieces]} remainding:{to_move_str}")
            for m in match_pieces:
                self.piece_squares.append(m.group())
            SlTrace.lg(f"match groups:{self.piece_squares}")
            match_to_move = re.match(r'^\s*([wb])', to_move_str)
            if match_to_move:
                to_move = match_to_move.group(1)
            self.to_move = to_move
            SlTrace.lg(f"to_move:{to_move}")        
        elif piece_string.upper().startswith("FEN:"):
            self.fen_setup(piece_string[4:])
        else:    
            raise Exception("We don't yet handle anything other than short form")
        
        if len(self.piece_squares) > 0:
            self.add_pieces(self.piece_squares)      # Populate board
                        
    def fen_setup(self, fen_str):
        """ Setup board piece_squares from FEN string
        setup self.piece_squares list of <piece><location> strings
        Initially just first field
        :fen_str:  FEN notation string
        """
        self.piece_squares = []
        fs = fen_str
        rank_n = self.nsqy
        while rank_n > 0 and len(fs) > 0:
            match_row = re.match(r'([^/]+)([/\s]|$)', fs)
            if match_row:
                row_str = match_row.group(1)
                self.fen_setup_row(rank_n, row_str, self.piece_squares)
                match_str = match_row.group()
                fs = fs[len(match_str):]    
            rank_n -= 1      # from top to bottom

    def fen_setup_row(self, rank_n, row_str, piece_squares):
        """ Setup from fen row
        :board_rank_n: rank 1...self.nsqy
        :row_str: row str e.g. 3qkbnr
        :piece_squares: list to which add piece_square e.g., ra8
        :returns: number piece_square added
        """
        board_file_strs = "abcdefgh"
        board_rank_strs = "12345678"
        board_file_no = 1
        n_placed = 0
        for ch in row_str:
            if pmatch := re.match(r'[rnbqkpRNBQKP]', ch):
                piece_pl = (pmatch.group() + board_file_strs[board_file_no-1]
                            + board_rank_strs[rank_n-1])
                piece_squares.append(piece_pl)
                board_file_no += 1
                n_placed += 1
            elif pmatch := re.match(r'[1-8]', ch):
                board_file_no += int(pmatch.group())    # Skip squares
            else:
                err = f"FEN row character:{ch} not recognized in row_str:{row_str}"
                SlTrace.lg(err)
                raise Exception(err)
        return n_placed

    """ 
    Internal board access
    Probably to be  made more efficient in the future
    """
    def add_pieces(self, piece_squares, clear_first=True):
        """ add to current setting
        :piece_squares: new piece_square setting to add
        :clear_first: clear board board before adding
                default: clear board first
        """
        if clear_first:
            self.clear_board()
        for ps in piece_squares:
            self.add_piece_square(ps)

    def add_piece_square(self, piece_square):
        """ Add piece square
        :piece_square: chess specifier <piece><square>
        """
        self.board_setting[piece_square[1:]] = piece_square[0]
        
    def clear_board(self):
        """ Empty board of pieces
        """
        self.board_setting = {}     # Board is dictionary of piece(e.g. K) by <square> e.g., e1

    def get_board_pieces(self):
        """ Get piece-square list for board setting
        :returns: list of current piece_square settings
        """
        piece_squares = []  # list <piece><rank><file>
        for sq in self.board_setting:
            piece = self.board_setting[sq]
            piece_squares.append(piece+sq)
        return piece_squares

    def make_move(self, move, to_move=None):
        """ Make a chess move
        :move: make move
                1. chess notation
                    in chess notation e.g. e4, e5, Nf3, Nc3, Ncf3, Qh4e1
        :to_move: side making move
                default: not previous move's
                        first: white
        :returns: None if successful, err_msg if not 
        """
        # check for d:e TBD
        if not (match_dest_pos := re.match(r'^(.*)([a-z])(\d+)$')):
            err = f"Unrecognized destination in move:{move}"
            SlTrace.lg(err)
            raise Exception(err)
        move_start,dest_pos_file, dest_pos_rank = match_dest_pos.groups()        
        if move_start == '':
            return self.make_move_pawn(dest_pos_file, dest_pos_rank)
        
        if not (match_move_start := re.match(r'([a-zA-Z])(\S*)$'), move_start):
            err = f"Unrecognize move piece: {move_start}"
            raise Exception(err)
        piece,piece_choice = match_move_start.groups()
        SlTrace.lg(f"piece:{piece} choice:{piece_choice}"
                   f" dest:{dest_pos_file}{dest_pos_rank}")
        
if __name__ == "__main__":
    from chessboard_print import ChessboardPrint
    
    SlTrace.clearFlags()
    #cb = Chessboard(pieces=':Kc1Qe1kh7 w')
    cb = Chessboard(pieces='FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
    cbd = ChessboardPrint(cb)
    cbd.display_board()

    cb = Chessboard(pieces=':Kc1Qe1kh7 w')
    cbd = ChessboardPrint(cb)
    cbd.display_board()
    