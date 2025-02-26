#chess_move.py

import re

from select_trace import SlTrace

from chess_move_notation import ChessMoveNotation
from chess_piece_movement import  ChessPieceMovement

class ChessMove:
    def __init__(self, board, to_move=None):
        self.board = board
        if to_move is not None:
            self.set_to_move(to_move)
        self.setup()        # Initialize state    
        self.cmn = ChessMoveNotation(self)
        self.cpm = ChessPieceMovement(board)

    def __str__(self):
        """ String form for debugging/analysis
        """
        ret = f"ChessMove: {self.spec}"
        ret += f"  {self.get_to_move()}"
        ret += f" {self.piece}"       # piece e.g, K == white king
        if self.err:
            ret += f" {self.err}\n    "
        if self.is_castle_king_side:
            ret += f" castle_king"
        if self.is_castle_queen_side:
            ret += f" castle_queen"
        if self.is_capture:
            ret += " is_capture:{self.is_capture}"
            ret += f" {self.capt_piece}"
            ret += f" on {self.capt_sq}"
        ret += f" orig_sq:{self.orig_sq}"  # move's original square
        ret += f" dest_sq:{self.dest_sq}" # move's destination square
        if self.dest_sq_mod:
            ret += f"dest_sq_mod:{self.dest_sq_mod}"
        if not self.update:
            ret += " NO to_move update"  # update to_move after successful move
        return ret

    def setup(self):
        """ Setup initial state
        which can be updated via decode...
        """
        self.err = None         # Error msg, None == no error
        self.spec = None        # move specification
        self.game_result = None # set with game result
        self.is_check = False   # True if check
        self.is_check_mate = False  # True if mate
        
        self.is_capture = False # True == capture made
        self.piece = None       # set later
        self.piece_type = None  # piece type k - king
        self.orig_sq = None     # set up later
        self.orig_sq_file = None    # to be disambugated
        self.dest_sq = None     # move's destination square
        self.dest_sq_mod = None # set later
        self.dest_sq_file = None  # dest abrv e.g., e:f
        self.orig2_sq = None    # optional origin square
        self.dest2_sq = None    # optional destination square
        self.dest2_sq_mod = None
        self.is_castle = False  # True - is castle
        self.is_castle_king_side = False  # castle kingside
        self.is_castle_queen_side = False # castle queenside
        
    def decode(self, spec):
        """ Decode move spec, in preparation for verification,
        execution.  Results are updated for successful parse
        :spec: move specification
        """
        
        self.setup()    # Setup default settings
        # In the future we may access some of these to
        # self.cmn the chess notational entry
        #
        
        # Parse basic notation
        if self.cmn.decode_spec_parts(spec=spec):
            return self.cmn.err
        
        # Complete parsing
        if self.cmn.decode_complete():        
            return self.cmn.err         # return completed
        
        self.cmn.make_move_update()     # Update parse results
        
    def get_start_piece(self, start_str, to_move=None):
        """ Determine starting piece, given spec string
        :start_str: beginning of specification less destination
        :to_move: whose move
            default: self.to_move
        :returns: (piece, remainder of start_str)
                pawn if no piece is included
        """

        if start_str[0].lower() in "kqrbnp":
            start_piece = start_str[0]
            remainder = start_str[1:]
        else:
            start_piece = "P" if self.to_move == "white" else "p"
            remainder = start_str   
        return (start_piece, remainder)

    def get_orig_sq(self, piece, piece_choice=None,
                    dest_sq=None):
        """ Find move's original square
        :piece: piece to move e.g. K,Q...P
        :piece_choice: disambiguation if choice
        :dest_sq:  destination square
        :returns: sq, None if none apply
        """
        ps_d = self.get_pieces(piece)   # our pieces on bd
        orig_sqs = []       # Filled with origin squares
        for ps in ps_d:
            sq = self.ps_to_sq(ps)
            sq_dest_d = self.get_move_to_sqs(piece=piece,
                                orig_sq=sq)
            if dest_sq in sq_dest_d:
                orig_sqs.append(sq)
                
        if len(orig_sqs) == 1:
            return orig_sqs[0]  # One and only one
        
        if len(orig_sqs) < 1:
            return None         # No takers
        if len(piece_choice) == 1:
            orig_sqs_2 = []
            for sq in orig_sqs:
                if sq.startswith(piece_choice):
                    orig_sqs_2.append(sq)
            if len(orig_sqs_2) == 1:
                return orig_sqs_2[0]
            
            if len(orig_sqs_2) > 1:
                SlTrace.lg(f"Ambiguous orig_sq: {orig_sqs_2}"
                           f" for {self.spec}")
                return None
            
        # TBD - Handle rank and double piece_choice
        return None
            
        
    def find_orig_sq(self):
        """ Determine original move square
            from info stored in self....
            Some thinking to do
            e.g. destination: e4 might come from e2 or e3
            or e5 (if black)
        """
        if self.is_pawn(self.piece):
            return self.find_orig_sq_pawn()

        candidate_ps = self.get_pieces(self.piece)
        capt_sqs = []       # to fill with squares that can move to
                            # our capture our destination 
        if len(candidate_sqs) == 1:
            return self.ps_to_sq(candidate_sqs[0])
    
    def rel_sq(self, base_sq, at_rank=None, rel_rank=None):
        """ find square relative to given sq
        :sq: base square
        :at_rank: get sq with base_sq file with at_rank
        :rel_rank: get sq with base_sq file with rank
                increasing for white, decreasing for black
                of base_sq rank+rel_rank
        :returns: sq
        """
        to_move = self.get_to_move()
        
        if at_rank is not None:
            base_sq_file,base_sq_rank = self.sq_to_file_rank(base_sq)
            at_sq = self.file_rank_to_sq(file=base_sq_file,
                                         rank=at_rank)
        
        if rel_rank is not None:
            rank_dir = 1 if to_move == "white" else -1
            rank_change = rank_dir*rel_rank
            dest_file,dest_rank = self.sq_to_file_rank(self.dest_sq,
                                                       to_int=True)
            at_sq = self.file_rank_to_sq(file=dest_file,
                                         rank=dest_rank+rank_change)
        return at_sq
    
    def is_in_sq(self, piece, at_rank=None, rel_rank=None):
        """ Check if piece is in a square
        :piece: piece, eg P, p, K
        :at_rank: check dest file and this rank
        :rel_rank: check dest file and dest rank+rel_rank
        """
        if at_rank is not None:
            dest_file,dest_rank = self.sq_to_file_rank(self.dest_sq)
            at_sq = self.file_rank_to_sq(file=dest_file, rank=at_rank)
            at_piece = self.get_piece(at_sq)
            if piece == at_piece:
                return True
        
        if rel_rank is not None:
            dest_file,dest_rank = self.sq_to_file_rank(self.dest_sq,
                                                       to_int=True)
            at_sq = self.file_rank_to_sq(file=dest_file,
                                         rank=dest_rank+rel_rank)
            at_piece = self.get_piece(at_sq)
            if piece == at_piece:
                return True
                
        return False

    def occupied_path(self, orig_sq, dest_sq,
                      exclude_orig=False, exclude_dest=False):
        """ Collect occupied squares in strait line from
        orig_sq to dest_sq, including end squares
        :orig_sq: beginning square
        :dest_sq: ending square
        :exclude_orig: True=Omit origin
                default: False
        :exclude_dest: True=Omit destination
                default: False
        """
        ps_list = []
        of_no,or_no = self.sq_to_file_rank(orig_sq, to_int=True)
        df_no,dr_no = self.sq_to_file_rank(dest_sq, to_int=True)
        file_change = df_no - of_no
        rank_change = dr_no - or_no
        
        file_dir = 0
        if file_change != 0:
            file_dir = int(file_change/abs(file_change))
        rank_dir = 0
        if rank_change != 0:
            rank_dir = int(rank_change/abs(rank_change))
            
        up_down = True if rank_change == 0 else False
        right_left = True if file_change == 0 else False
        diagonal = True if abs(file_change) == abs(rank_change) else False
        if not up_down and not right_left and not diagonal:
            return []
        
        occupied_sqs = []   # piece_square
        file_no = of_no
        rank_no = or_no
        while True:
            piece = self.get_piece(file=file_no, rank=rank_no)
            if piece is not None:
                if exclude_orig and file_no == of_no and rank_no == or_no:
                    pass    # Excluding origin
                elif exclude_dest and file_no == df_no and rank_no == dr_no:
                    pass    # Excluding dest
                else:
                    ps = piece + self.file_rank_to_sq(
                        file=file_no, rank=rank_no)
            if file_no == df_no and rank_no == dr_no:
                break
            
            file_no += file_dir
            rank_no += rank_dir
        return occupied_sqs         
    
    def find_orig_sq_pawn(self):
            if not self.is_some_piece_choice():
                if self.piece == "P":
                    if self.is_in_sq(self.piece, rel_rank=-1):
                        self.orig_sq = self.rel_sq(self.dest_sq, rel_rank=-1)
                    elif self.is_in_sq(self.piece, at_rank=2):  #origial pos
                        self.orig_sq = self.rel_sq(self.dest_sq, rel_rank=-2)
                    else:
                        self.err = f"Can't find origin pawn spec:{self.spec}"
                        return self.err
                    
                    blocking_sqs = self.occupied_path(self.orig_sq,
                                        self.dest_sq, exclude_orig=True)
                    if len(blocking_sqs) > 0:
                        self.err = f"Interposed pieces:{blocking_sqs}"
                        return self.err
                            
                elif self.piece == "p":
                    if self.is_in_sq(self.piece, rel_rank=1):
                        self.orig_sq = self.rel_sq(self.dest_sq, rel_rank=1)
                    else:
                        self.orig_sq = self.rel_sq(self.dest_sq, rel_rank=2)        
                occupied_sq = self.occupied_path(self.orig_sq, self.dest_sq,
                                                 exclude_orig=True)
                if len(occupied_sq) > 0:
                    err = f"move: {self.spec} {self.piece}:"
                    err += f" Unexpected occupied squares: {occupied_sq}"
                    self.err
                    return err

    """
    Links to cpm (ChessPieceMove) functions
    """
    def get_move_to_sqs(self, piece, orig_sq=None):
        """ Get list of squares this piece can legaly move to
        including capture and promotion, based on board contents
        One can use various functions to setup position:
            self.clear_board() - clears board to empty
            self.place_piece() - to setup additional pieces
                    Note orig_sq implies piece, sq without actually
                    populating the square
            self.save_move(ChessSaveUnit) sets previous move 
                e.g. self.save_move(ChessSaveUnit(self,
                            orig_ps="pe7", dest_ps="pe5"))
                        is a 2-square black pawn move which could
                        be taken enpasant by a white pawn on d4
        :piece: piece
        :orig_sq: origin square
        :prev_move: previous move (ChessSaveUnit)
            default: get from board 
        :returns: dictionary of candidate destination squares
                Empty if none
                None if error
        """
        return self.cpm.get_move_to_sqs(piece=piece,
                                orig_sq=orig_sq)



    """
    Links to cmn (ChessMoveNotation) functions
    """
                            
    def decode_spec_parts(self, spec):
        """ Decode standard specification, creating parts
        for possible disambuation, verification, and execution:
        Verification, disambugation, execution is done later
        :setups: self.err error text or None, also returned by decode
                self.piece_type: lowercase KQRBNP
                self.dest_sq: destination square, if known
                    or self.dest_sq_file, if to be determined
                self.is_capture: True if capture
        :returns: None if successful, else err_msg text 
        """
        return self.cmn.decode_spec_parts(spec=spec)                        

    """
    Links to board functions
    """

    def can_castle(self, king_side=True, to_move=None):
        """ Determine if we can castle
        :king_side: True if king side, else queen side
                default: kingside                
        :returns: True if the requested castling is permited
        """
        return self.board.can_castle(king_side=True, to_move=None)

    def file_rank_to_sq(self, file=None, rank=None):
        """ Convert rank, file to sq notation
        :file: int 1-8 or str: a-h
        :rank: int 1-8 or str 1-8
        :returns: sq notation
        """
        return self.board.file_rank_to_sq(file=file, rank=rank)
        if isinstance(file,int):
            file = chr(ord('a')+file-1)
        if isinstance(rank, int):
            rank = chr(ord('1')+rank-1)
        return file+rank

    def get_move_no(self):
        """ Get chess game move number, assuming
        started with white
        """
        return self.board.get_move_no()
        
    def get_piece(self, sq=None, file=None, rank=None, remove=False):
        """ Get piece at sq, None if empty
        :sq: square notation e.g., a1 if present
            else
        :file: file letter or int:1-
        :rank: rank str or int: 1-
        :remove: True - remove piece from board
            default: leave piece in square 
        """
        return self.board.get_piece(
            sq=sq, file=file, rank=rank, remove=remove)

    
    def get_pieces(self, piece=None, piece_type=None):
        """ Get piece-square list for board setting
        :piece: get only pieces
            OR
        :piece_type get only types(case insensitive)
                e.g q - all both color queens
                "empty" - all empty squares
                "any" - any piece type
        :returns: list of piece_square settings
        """
        return self.board.get_pieces(piece=piece,
                                     piece_type=piece_type)

    def get_to_move(self):
        """ Whose move is it?
        """
        return self.board.get_to_move()

    def set_to_move(self, to_move=None):
        """ set who to move
        :to_move: "black" or "white"
            default: "white"
        """
        self.board.set_to_move(to_move)

    def piece_to_type(self, piece):
        """ Get piece's type (lowercase of piece)
        :piece: piece uppercase for white
        :returns: piece type (lowercase)
        """
        return self.board.piece_to_type(piece)
    
    def piece_type_to_piece(self, type, to_move=None):
        """ Get piece's color
        :piece_type_to_piece: piece uppercase for white
        :to_move: black/white
            default: from board
        :returns: piece    # uppercase if white lowercase if black
        """
        return self.board.piece_type_to_piece(type=type, to_move=to_move)

    def ps_to_sq(self, ps):
        """ Get square from piece_square
        :ps: piece-square spec
        :returns: square
        """
        return self.board.ps_to_sq(ps=ps)
    
    def make_move(self,
                  just_notation=None,
                  orig_sq=None, dest_sq=None,
                  dest_sq_mod=None,
                  spec=None,
                  update=True,
                  orig2_sq=None, dest2_sq=None,
                  dest2_sq_mod=None):
        """ Make move after decode
        Update to_move iff successful
        :just_notation: just for notation - no checks
                default: False
        :orig_sq: origin square for move
        :dest_sq: destination square for move
        :spec: move specification
        :dest_sq_mod: alternate piece for destination e.g. promotion 
        :update: change board default: True - change
        :orig2_sq: optional second origin sq e.g. for castle
        :dest2_sq: optional second destination sq
        :dest2_sq_mod: optional alternate piece for dest
        :returns: None if successful, else err msg
        """
        if orig_sq is None:
            orig_sq = self.orig_sq
        if dest_sq is None:
            dest_sq = self.dest_sq
        if spec is None:
            spec = self.spec
        if dest_sq_mod is None:
            dest_sq_mod = self.dest_sq_mod
        if update is None:
            update = self.update
        if orig2_sq is None:
            orig2_sq = self.orig2_sq
        if dest2_sq is None:
            dest2_sq = self.dest2_sq
        if dest2_sq_mod is None:
            dest2_sq_mod = self.dest2_sq_mod
                
        return self.board.make_move(just_notation=just_notation,
                                    orig_sq=orig_sq,
                                    dest_sq=dest_sq,
                                    dest_sq_mod=dest_sq_mod,
                                    orig2_sq=orig2_sq,
                                    dest2_sq=dest2_sq,
                                    dest2_sq_mod=dest2_sq_mod,
                                    update=update,
                                    spec=spec)

    def sq_to_file_rank(self, sq, to_int=False):
        """ split sq into file, rank pair
        :sq: square notation
        :to_int: True - return file,rank as ints 1-
        :returns: (file, rank) e.g. a1  or to_int 1,1
        """
        return self.board.sq_to_file_rank(sq=sq, to_int=to_int)
           
if __name__ == "__main__":
    
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    import chess_move_notation as CMN 
    
    SlTrace.clearFlags()

    cb = Chessboard()
    cb.standard_setup()
    cbp = ChessboardPrint(cb)
    moves = """
    1.Nf3 Nf6 2.c4 g6 3.Nc3 Bg7 4.d4 O-O
    5.Bf4 d5 6.Qb3 dxc4 7.Qxc4 c6 8.e4 Nbd7
    9.Rd1 Nb6 10.Qc5 Bg4 11.Bg5 Na4 12.Qa3 Nxc3
    13.bxc3 Nxe4 14.Bxe7 Qb6 15.Bc4 Nxc3 16.Bc5 Rfe8+
    17.Kf1 Be6 18.Bxb6 Bxc4+ 19.Kg1 Ne2+ 20.Kf1 Nxd4+
    21.Kg1 Ne2+ 22.Kf1 Nc3+ 23.Kg1 axb6 24.Qb4 Ra4
    25.Qxb6 Nxd1 26.h3 Rxa2 27.Kh2 Nxf2 28.Re1 Rxe1
    29.Qd8+ Bf8 30.Nxe1 Bd5 31.Nf3 Ne4 32.Qb8 b5
    33.h4 h5 34.Ne5 Kg7 35.Kg1 Bc5+ 36.Kf1 Ng3+
    37.Ke1 Bb4+ 38.Kd1 Bb3+ 39.Kc1 Ne2+ 40.Kb1
    Nc3+ 41.Kc1 Rc2# 0-1
    """
    move_specs = CMN.game_to_specs(moves) 
    for move_spec in move_specs:
        cm = ChessMove(cb)
        move_no = cm.get_move_no()
        move_no_str = f"move {move_no:2}: "
        if cm.get_to_move() == "black":
            move_no_str = " " * len(move_no_str)
        if cm.decode(move_spec):
           SlTrace.lg(f"{move_no_str}Error: {move_spec}: {cm.err}")
        else:
            SlTrace.lg(f"{move_no_str}{cm}")
                
        if cm.make_move():
            SlTrace.lg(cm.err)
            SlTrace.lg("Quitting")
            break
