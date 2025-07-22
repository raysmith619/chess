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
        dest2_sq=None,
        half_move_clock=None,
        full_move_clock=None,
        poss_en_passant=None,
        can_castle_white_kingside=None,
        can_castle_white_queenside=None,
        can_castle_black_kingside=None,
        can_castle_black_queenside=None):

        self.board = board   # As of current state, will chante
        self.move_no = board.get_move_no()
        if to_move is None:
            to_move = board.get_to_move()
        self.to_move = to_move      # As of change
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
        self.half_move_clock=half_move_clock
        self.full_move_clock = full_move_clock
        self.poss_en_passant=poss_en_passant
        
        if can_castle_white_kingside is None:
            can_castle_white_kingside = board.can_castle_white_kingside
        self.can_castle_white_kingside = can_castle_white_kingside
        
        if can_castle_white_queenside is None:
            can_castle_white_queenside = board.can_castle_white_queenside
        self.can_castle_white_queenside = can_castle_white_queenside
        
        if can_castle_black_kingside is None:
            can_castle_black_kingside = board.can_castle_black_kingside
        self.can_castle_black_kingside = can_castle_black_kingside
        
        if can_castle_black_queenside is None:
            can_castle_black_queenside = board.can_castle_black_queenside
        self.can_castle_black_queenside = can_castle_black_queenside

    def get_move_no(self):
        """ Get move no as of save
        """
        return self.move_no
    
    def get_to_move(self, opponent=False):
        """ Whose move is it?  As of save
        Not using opponent
        :opponent: True - opponent
        """
        return self.to_move
    
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
        board.half_move_clock = self.half_move_clock
        board.full_move_clock = self.full_move_clock
        board.poss_en_passant = self.poss_en_passant
        
        board.can_castle_white_kingside = self.can_castle_white_kingside
        board.can_castle_white_queenside = self.can_castle_white_queenside
        board.can_castle_black_kingside = self.can_castle_black_kingside
        board.can_castle_black_queenside = self.can_castle_black_queenside
    