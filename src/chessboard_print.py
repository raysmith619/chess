#chessboard_print.py 10Feb2025  crs
import re

class ChessboardPrint:
    def __init__(self,
                 board,
                 display_options="sqare_notes",
                ):
        self.board = board
        self.display_options = display_options
        
    def display_board(self, mw=None, include_pieces=True,
                      display_options=None):
        display_str = self.display_board_str(include_pieces=include_pieces,
                                             display_options=display_options)
        print(f"\n{display_str}\n")
        
    def display_board_str(self, mw=None, include_pieces=True,
                          display_options=None):
        """ Display board, always include pieces
        """
        if display_options is None:
            display_options = self.display_options
        board_str = ""    
        board = self.board
        """list of rows,
            each a list of cols,
            each list of squares
        """
        # Easy access to square contents
        # access piece = pbs[ic][ir], None == empty         
        pb_squares = []
        for ic in range(board.nsqx):     # index col left to right
            col = []
            for ir in range(board.nsqy): # index row bottom to top
                col.append(None)
            pb_squares.append(col)
        
        pss = self.board.get_board_pieces()
        for ps in pss:
            if not (match_ps := re.match(r'^(\w)(\w)(\w)$', ps)):   # Ke1
                raise Exception(f"ps:{ps} not p file rank")
            piece,file,rank = match_ps.groups()
            ic = ord(file) - ord('a')
            ir = ord(rank)-ord('1')
            pb_squares[ic][ir] = piece
        
        black_sq = "'"*4
        white_sq = "`"*len(black_sq)
        for ir in reversed(range(board.nsqy)):
            rank = str(ir+1)
            row_str = f"{rank}:"
            for ic in range(board.nsqx):
                piece = pb_squares[ic][ir]
                if piece is None:
                    sq = black_sq if (ir+ic)%2==0 else white_sq
                    sq_spec = chr(ord('a')+ic)+str(ir+1)    # e.g. a1
                    if "square_notes" in display_options:
                        sq = sq[0]+sq_spec+sq[-1]      # surrounding
                    row_str += f" {sq}"     # For visible blank
                else:
                    if piece.isupper():
                        row_str += f" [.{piece.lower()}]"
                    else:
                        row_str += f" [ {piece}]"
            board_str += row_str + "\n"
        sep_str = "-"*len(row_str)
        board_str += sep_str + "\n"
        ranks_str = " , "
        for ic in range(board.nsqx):
            rank_str = ", "+chr(ord('a')+ic)+" ,"
            ranks_str += rank_str    
        board_str += ranks_str
        return board_str
    
if __name__ == "__main__":
    from chessboard import Chessboard
    
    cb = Chessboard(pieces='FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
    cbp = ChessboardPrint(cb)
    cbp.display_board()
    cbp.display_board(display_options="square_notes")
    
    cb = Chessboard(pieces=':Kc1Qe1kh7 w')
    cbp = ChessboardPrint(cb)
    cbp.display_board()
    cbp.display_board(display_options="square_notes")
    
    