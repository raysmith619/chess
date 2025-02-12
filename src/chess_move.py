#chess_move.py
""" Decode move from specification
"""
import re

from select_trace import SlTrace

class ChessMove:
    def __init__(self, board, to_move=None):
        self.board = board
        self.to_move = to_move
        
    
    def decode_castle(self, spec,  to_move=None):
        """ Process castle
        :spec: castle specification oo or ooo
        :to_move:white or black
            default: ChessMove to_move, else current board.to_move            
        """    
    def decode(self, spec,  to_move=None):
        """ Decode notation into:
        in chess notation e.g. e4, e5, Nf3, Nc3, Ncf3, Qh4e1
        :to_move: side making move
                default: not previous move's
                        first: white
        :setups: self.err error text or None, also returned by decode
                self.piece to piece notation e.g. p or P
                self.orig_sq: beginning square e.g. e2
                self.dest_sq: destination square
                self.capt_sq: capture square or None if no capture
                self.new_piece: promotion piece or None if no promotion
                self.to_move: color of moved piece
        :returns: None if successful, else err_msg text 
        """
        if to_move is None:
            to_move = self.to_move
            if to_move is None:
                to_move = self.board.to_move
                
        if spec in ["oo", "ooo"]:
            return self.decode_castle(spec=spec, to_move=to_move)
        
        # check for d:e TBD
        # Pick off destination from tail end
        if not (match_dest_pos := re.match(r'^(.*)([a-z])(\d+)$', spec)):
            self.err = f"Unrecognized destination in move:{spec}"
            return self.err

        move_start,dest_pos_file, dest_pos_rank = match_dest_pos.groups()        
        if move_start == '':    # No piece == pawn
            piece = "p" if self.board.to_move == "black" else "P"
            piece_choice = ""
        else:
            # Allow for extended pieces not in kqrbnp,KQRBNP
            if not (match_move_start := re.match(r'([A-Z])(\S*)$', move_start)):
                self.err = f"Unrecognize move piece: {move_start}"
                return self.err
        
            piece,piece_choice = match_move_start.groups()
        SlTrace.lg(f"spec: {spec} to_move:{to_move} piece:{piece}"
                    f" piece_choice:{piece_choice}"
                    f" dest:{dest_pos_file}{dest_pos_rank}")
        self.piece = piece
        self.dest_pos_file = dest_pos_file
        self.dest_pos_rank = dest_pos_rank 
    
if __name__ == "__main__":
    
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    SlTrace.clearFlags()
    cb = Chessboard()
    cbp = Chessboard
    cm = ChessMove(cb)
    for move_spec in ["e4", "e5", "Nf3", "Nc6", "Ncf3", "Qh4e1"]:
        cm.decode(move_spec)