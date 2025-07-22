#chessboard_print.py 10Feb2025  crs
import re

from select_trace import SlTrace

class ChessboardPrint:
    def __init__(self,
                 board,
                 display_options=None,
                ):
        if board is None:
            raise Exception(f"ChessboardPrint board is None")
        
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
        if display_options is None:
            display_options = []
        elif isinstance(display_options,str):
            display_options = display_options.split()
            
        figure_pieces = {
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
            'fullSQ': chr(0x25A0),
            'emptySQ': chr(0x25A1),
            'sq_diag' : chr(0x25A7),
            'b_sm_sq' :chr(0x25AA),
            'vert_line' : chr(0xFF5C),
            'horz_line' : chr(0x23AF),
            'light_sq' : chr(0x23AF),
            'black_cx_hatch' : chr(0x25A9),
            '2_per_em' : chr(0x2002),
            '3_per_em' : chr(0x2004),
            '4_per_em' : chr(0x2005),
            '6_per_em' : chr(0x2006),
            'thin_sp' : chr(0x2009),
            'hair_sp' : chr(0x200A),
            'zero_sp' : chr(0x200B),
        }
        w_sq = figure_pieces['emptySQ']
        bk_cx = figure_pieces['black_cx_hatch']
        sq_diag = figure_pieces['sq_diag']
        emb2 = figure_pieces['2_per_em']
        emb3 = figure_pieces['3_per_em']
        emb4 = figure_pieces['4_per_em']
        emb6 = figure_pieces['6_per_em']
        emb3 = figure_pieces['3_per_em']
        emb3 = figure_pieces['3_per_em']
        th_sp = figure_pieces['thin_sp']
        hair_sp = figure_pieces['hair_sp']
        zero_sp = figure_pieces['zero_sp']

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
        sq_size = len(white_sq)
        vs = figure_pieces['vert_line']
        hs = figure_pieces['horz_line']
        if "visual" in display_options:
            black_sq = emb6+figure_pieces['b_sm_sq']+""
            horz_div_line_top = "   " + "" + board.nsqx*(hs+hs+hs)
            horz_div_line = "  " +vs + board.nsqx*(hs+vs)
            vert_div_sq = figure_pieces['vert_line']
            white_sq = ""+" "+""
        if "visual_s" in display_options:
            #black_sq = emb4+"bk_cx"+emb4
            black_sq = emb4+":"+emb4
            white_sq = emb4+w_sq+emb4
        
        if "visual" in display_options:
            board_str += horz_div_line_top+"\n"
        for ir in reversed(range(board.nsqy)):
            rank = str(ir+1)
            row_str = f"{rank}:"
            for ic in range(board.nsqx):
                piece = pb_squares[ic][ir]
                if "visual" in display_options:
                    row_str += vert_div_sq
                if piece is None:
                    sq = black_sq if (ir+ic)%2==0 else white_sq
                    sq_spec = chr(ord('a')+ic)+str(ir+1)    # e.g. a1
                    if "visual" in display_options:
                        sq = ""+sq                        
                    elif "square_notes" in display_options:
                        sq = " "+sq[0]+sq_spec+sq[-1]      # surrounding
                    elif "visual_s" in display_options:
                        sq = sq
                    else:
                        sq = " "+sq+""
                    row_str += f"{sq}"     # For visible blank
                else:
                    if "visual" in display_options:
                        row_str += f"{figure_pieces[piece]}"
                    elif "visual_s" in display_options:
                        row_str += emb6+figure_pieces[piece]+emb6
                    else:
                        if piece.isupper():
                            row_str += f" [.{piece.lower()}]"
                        else:
                            row_str += f" [ {piece}]"
            board_str += row_str + "\n"
            if "visual" in display_options:
                if ir == 0:
                    board_str += horz_div_line_top + "\n"
                else:
                    board_str += horz_div_line + "\n"
        if len(display_options) == 0 or "visual_s" in display_options:
            sep_str = "-"*len(row_str)
            board_str += sep_str + "\n"
            
        if "visual_s" in display_options:
            ranks_str = " "
        else:
            ranks_str = ", "
        for ic in range(board.nsqx):
            if "visual_s" in display_options:
                rank_str = "  "+chr(ord('a')+ic)
            else:
                rank_str = ", "+chr(ord('a')+ic)+" ,"
            ranks_str += rank_str    
        if "visual" in display_options:
            ranks_str = " "+ranks_str.replace(",","")
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
    for option in [None, "visual", "visual_s"]:
        SlTrace.lg(f"\nOption: {option}")   
        for cbp in [cbp1, cbp2]:
            cbp.display_board(display_options=option)
    
    