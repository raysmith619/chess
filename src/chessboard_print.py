#chessboard_print.py 10Feb2025  crs
import re

from select_trace import SlTrace

class ChessboardPrint:
    def __init__(self,
                 board,
                 display_options=None,
                ):
        self.board = board
        self.display_options = display_options
        
    def display_board(self, mw=None, include_pieces=True,
                      display_options=None):
        display_str = self.display_board_str(include_pieces=include_pieces,
                                             display_options=display_options)
        SlTrace.lg(f"\n{display_str}\n", replace_non_ascii=None)
        
    def display_board_str(self, mw=None, include_pieces=True,
                          display_options=None):
        """ Display board, always include pieces
        :include_pieces: include current pieces / position in display
                default: True - show the pieces
        :display_options: "visual" - for sighted
                default: Provide display targeted for blind / Braille processing
        """
        figure_pieces = {
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
            'fullSQ': chr(0x25A0),
            'emptySQ': chr(0x25A1),
            'b_sm_sq' :chr(0x25AA),
        }
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
        
        pss = self.board.get_pieces()
        for ps in pss:
            if not (match_ps := re.match(r'^(\w)(\w)(\w)$', ps)):   # Ke1
                raise Exception(f"ps:{ps} not p file rank")
            piece,file,rank = match_ps.groups()
            ic = ord(file) - ord('a')
            ir = ord(rank)-ord('1')
            pb_squares[ic][ir] = piece
        
        black_sq = "'"*4
        white_sq = "`"*len(black_sq)
        if display_options is not None and "visual" in display_options:
            black_sq = " "+figure_pieces['b_sm_sq']+"  "
            white_sq = " "+figure_pieces['emptySQ']+"  "
        if display_options is not None and "visual_s" in display_options:
            black_sq = figure_pieces['fullSQ']
            white_sq = figure_pieces['emptySQ']
        for ir in reversed(range(board.nsqy)):
            rank = str(ir+1)
            row_str = f"{rank}:"
            for ic in range(board.nsqx):
                piece = pb_squares[ic][ir]
                if piece is None:
                    sq = black_sq if (ir+ic)%2==0 else white_sq
                    sq_spec = chr(ord('a')+ic)+str(ir+1)    # e.g. a1
                    if display_options is not None and "visual" in display_options:
                        sq = " "+sq                        
                    elif display_options is not None and "square_notes" in display_options:
                        sq = " "+sq[0]+sq_spec+sq[-1]      # surrounding
                    elif display_options is not None and "visual_s" in display_options:
                        sq = sq
                    else:
                        sq = " "+sq+""
                    row_str += f"{sq}"     # For visible blank
                else:
                    if display_options is not None and "visual" in display_options:
                        row_str += f"  {figure_pieces[piece]}  "
                    elif display_options is not None and "visual_s" in display_options:
                        row_str += f"{figure_pieces[piece]}"
                    else:
                        if piece.isupper():
                            row_str += f" [.{piece.lower()}]"
                        else:
                            row_str += f" [ {piece}]"
            board_str += row_str + "\n"
        sep_str = "-"*len(row_str)
        board_str += sep_str + "\n"
        ranks_str = ", "
        for ic in range(board.nsqx):
            if display_options is not None and "visual_s" in display_options:
                rank_str = chr(ord('a')+ic)+" "
            else:
                rank_str = ", "+chr(ord('a')+ic)+" ,"
            ranks_str += rank_str    
        if display_options is not  None and "visual" in display_options:
            ranks_str = ranks_str.replace(","," ")
        board_str += ranks_str
        return board_str
    
if __name__ == "__main__":
    from chessboard import Chessboard
    display_options="visual"
    #display_options="visual_s"

    cb1 = Chessboard(pieces='FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
    cbp1 = ChessboardPrint(cb1)
    
    cb2 = Chessboard(pieces=':Kc1Qe1kh7 w')
    cbp2 = ChessboardPrint(cb2)
    for option in [None, "visual"]:
        SlTrace.lg(f"\nOption: {option}")   
        for cbp in [cbp1, cbp2]:
            cbp.display_board(display_options=option)
    
    