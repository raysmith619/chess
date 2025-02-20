#chess_save_unit.py

class ChessSaveUnit:
    """ Save info to support restoring previous current
    board status
    """
    
    def __init__(self,
        board,
        spec=None,
        to_move=None,
        orig_piece=None,
        prev_orig_sq_moved=None,
        orig_sq=None,
        dest_piece=None,
        dest_sq=None,
        
        orig2_piece=None,
        orig2_sq=None,
        prev_orig2_sq_moved=None,
        dest2_piece=None,
        dest2_sq=None):
        
        if to_move is None:
            to_move = board.to_move
        self.to_move = to_move
        self.spec = spec
        
        if orig_piece is None:
            orig_piece = board.get_piece(orig_sq)
        self.orig_piece = orig_piece
        self.orig_sq = orig_sq
        self.prev_orig_sq_moved = prev_orig_sq_moved
        if dest_piece is None:
            dest_piece = board.get_piece(dest_sq)
        self.dest_piece = dest_piece
        self.dest_sq = dest_sq
        # default not used
        self.orig2_piece = orig2_piece
        self.orig2_sq = orig2_sq
        self.prev_orig2_sq_moved = prev_orig2_sq_moved
        self.dest2_piece = dest2_piece
        self.dest2_sq = dest2_sq
        if orig2_sq is not None:
            if orig2_piece is None:
                orig2_piece = board.get_piece(orig_sq)
            self.orig2_piece = orig2_piece
            if dest2_piece is None:
                dest2_piece = board.get_piece(dest2_sq)
            self.dest2_piece = dest2_piece
