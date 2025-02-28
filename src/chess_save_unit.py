#chess_save_unit.py

class ChessSaveUnit:
    """ Save info to support restoring previous current
    board status
    """
    
    def __init__(self,
        board,
        spec=None,
        to_move=None,
        move_no=None,
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
        self.board = board
        if to_move is None:
            to_move = board.get_to_move()
        self.to_move = to_move
        if move_no is None:
            move_no = board.get_move_no()
        self.move_no = move_no
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
                orig2_piece = board.get_piece(orig2_sq)
            self.orig2_piece = orig2_piece
            if dest2_piece is None:
                dest2_piece = board.get_piece(dest2_sq)
            self.dest2_piece = dest2_piece

    def restore(self):
        """ Restore board state from our state
        which was in effect before the move
        """
        board = self.board
        board.set_to_move(self.to_move)
        board.place_piece(self.orig_piece, sq=self.orig_sq)
        if self.prev_orig_sq_moved is not None:
            board.set_as_moved(sq=self.orig_sq, is_moved=self.prev_orig_sq_moved)
        if self.prev_orig2_sq_moved is not None:
            board.set_as_moved(sq=self.orig_sq, is_moved=self.prev_orig2_sq_moved)
        board.place_piece(self.dest_piece, sq=self.dest_sq)
        if self.orig2_sq:
            board.place_piece(self.orig2_piece, self.orig2_sq)
        if self.dest2_sq:
            board.place_piece(self.dest2_piece, self.dest2_sq)
            