#chess_move.py
""" Decode move from specification
"""
import re

from select_trace import SlTrace

class ChessMove:
    def __init__(self, board, to_move=None):
        self.board = board
        self.to_move = to_move
        
    def __str__(self):
        """ String form for debugging/analysis
        """
        ret = "ChessMove: to_move:{self.to_move}"
        ret += f" {self.spec}"        # move specification
        if self.err:
            ret += f" {self.err}\n    "
        if self.castle_king:
            ret += f" castle_king"
        if self.castle_queen:
            ret += f" castle_queen"
        ret += f"\n    {self.piece}"       # piece e.g, K == white king
        if self.is_capture:
            ret += " is_capture:{self.is_capture}"
            ret += f" {self.capt_piece}"
            ret += f" on {self.capt_sq}"
        ret += f" orig_sq:{self.orig_sq}"  # move's original square
        ret += f" dest_sq:{self.dest_sq}" # move's destination square
        if self.dest_sq_mod:
            ret += f"dest_sq_mod:{self.dest_sq_mod}"
        if self.update_to_move:
            ret += f" self.update_to_move"  # update to_move after successful move

    def decode_castle(self, spec,  to_move=None):
        """ Process castle
        :spec: castle specification oo or ooo
        :to_move:white or black
            default: ChessMove to_move, else current board.to_move            
        """
        if spec == "O-O":
            self.castle_king = True
        elif spec == "O-O-O":
            self.castle_queen =True
        else:
            self.err = "Unrecognized castle {spec}"
            return self.err

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
        candidate_piece_sqs_d = self.get_pieces(piece)
        can_moves = []
        if len(candidate_piece_sqs_d) == 1:
            return list(candidate_piece_sqs_d)[0]
        
        return self.get_choice_sq(piece, candidate_piece_sqs_d, piece_choice)
    
    def get_dest_sq(self, dest_str, orig_piece=None):
        """ Get destination square
        :dest_str: destination part of specification
                e.g. a for file a ONLY for pawn
                    a1: file a, rank 2
        :returns: destination square
        """
        if (match_dest_sq := re.match(r'([a-z])([1-8]$)', dest_str)):
            file, rank = match_dest_sq.groups()
            return file+rank
        
        if (match_dest_sq := re.match(r'([a-z])', dest_str)):
            file = match_dest_sq.group(1)
            if not self.is_pawn(orig_piece):
                raise Exception(f"{dest_str} piece: {orig_piece}"
                                f" not a pawn")
            raise Exception(f"TBD support for dest_str: {dest_str}")
        
            
        
    def decode_if_capture(self, spec, to_move=None):
        """ Check for and process capture
        Examples exd,exd5, Bxe5, Rdxf8, R1xa3, Qh4xe1
        :spec: move specificaiont
        :to_move: whose move
                default: use to_move self or self.board.to_move
        :returns: True if a capture
                if capture, setup move settings
        """
        # with x or : explicit capture
        expl_capture = False
        impl_piece_capture = False
        impl_pawn_capture = False
        if match_expl_capture := re.match(r'^(.*)([x:])(.*))$', spec):
            expl_capture = True
        elif (match_impl_piece_capture :=
                    re.match(r'([KQRBN])(.*)([a-zA-Z][1-8])$', spec)):
            impl_piece_capture = True
        elif (match_impl_pawn_capture :=
                    re.match(r'(([a-z])(.*))$', spec)):
            impl_pawn_capture = True
        else:
            return False
        
        if expl_capture:     
            # Examples:
            # e4:d5, e:d, e:d5 q:a5, Qh4xe1
            # B:a1
            start_str,self.capture_ind,dest_str = match_expl_capture.groups()
            orig_piece,piece_choice = self.get_start_piece(start_str)
            self.dest_sq = self.get_dest_sq(dest_str,
                                            orig_piece=orig_piece)             
            self.orig_sq = self.get_orig_sq(piece=orig_piece,
                                       piece_choice=piece_choice,
                                       dest_sq=self.dest_sq)
                        
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
                self.dest_sq_mod: alternative to orig_sq contents
                                for say promotions
                            default: destination sq
                                gets piece from self.orig_sq
                self.update_to_move: update to_move after move
                self.to_move: Whose move white/black
                    default: use board.to_move
        :returns: None if successful, else err_msg text 
        """
        # Change if/when appropriate
        self.err = None         # Error msg, None == no error
        self.spec = spec        # move specification
        self.is_capture = False # True == capture made
        self.capt_piece = None  # captured piece (on dest_sq)
        self.to_move = None     # to move "white" / "black"
        self.piece = None       # piece e.g, K == white king
        self.orig_sq = None     # move's original square
        self.dest_sq = None     # move's destination square
        self.dest_sq_mod = None # modified dest_sq piece
        self.update_to_move = True  # update to_move after successful move
        is_castle_king = False  # castle kingside
        is_castle_queen = False # castle queenside
        # piece/square selection results
        self.dest_from_file = None  # dest abrv e.g., e:f
        self.orig_from_file = None  # orig abrv g:h
         
        
        if to_move is None:
            to_move = self.to_move
            if to_move is None:
                to_move = self.board.to_move
        self.spec = spec        
        if spec in ["O-O", "O-O-O"]:
            return self.decode_castle(spec=spec, to_move=to_move)
        
        # check for d:e TBD
        # Check if capture
        if self.decode_if_capture(spec, to_move=to_move):
           return self.err  # decoded - return result
        
        # Pick off destination <file><rank> from tail end
        #   with capture : or x
        if (match_dest_pos := re.match(r'^(.*)([x:])([a-z])(\d+)$', spec)):
            self.is_capture = True
            move_start,capture_str,dest_pos_file, dest_pos_rank = match_dest_pos.groups()        
            self.capt_piece = self.get_piece(dest_pos_file+dest_pos_rank)
        elif (match_dest_pos := re.match(r'^(.*)([a-z])(\d+)$', spec)):
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
        SlTrace.lg(f"spec: {spec} to_move:{to_move}"
                    f"piece:{piece}"
                    f" piece_choice:{piece_choice}"
                    f" dest:{dest_pos_file}{dest_pos_rank}",
                    "chess_moves")
        self.piece = piece
        self.piece_choice = piece_choice
        self.dest_sq = dest_pos_file+dest_pos_rank
        if not self.find_orig_sq():
            return self.err     # Return error msg string
            
        # Pick off destination <file> from tail end e.g. exf
        elif (match_dest_pos := re.match(r'^(.*)[x:]([a-z])$', spec)):
            move_start,dest_pos_file = match_dest_pos.groups()        
            if move_start == '':    # No piece == pawn
                piece = "p" if self.board.to_move == "black" else "P"
                piece_choice = ""
            else:
                # Allow for extended pieces not in kqrbnp,KQRBNP
                if not (match_move_start := re.match(r'([A-Z])(\S*)$', move_start)):
                    self.err = f"Unrecognize move piece: {move_start}"
                    return self.err
            
                piece,piece_choice = match_move_start.groups()
            SlTrace.lg(f"spec: {spec} to_move:{to_move}"
                        f"piece:{piece}"
                        f" piece_choice:{piece_choice}"
                        f" dest:{dest_pos_file}{dest_pos_rank}",
                        "chess_moves")
            self.piece = piece
            self.piece_choice = piece_choice
            self.dest_sq = dest_pos_file+dest_pos_rank
            if not self.find_orig_sq():
                return self.err     # Return error msg string


    def is_pawn(self, piece):
        """ Check if a pawn
        :piece: piece notation
        """
        return True if (piece == "P" or piece == "p") else False

    def is_some_piece_choice(self):
        """ Check if a non-empty piece disambiguation
        """
        if (self.piece_choice is not None
            and self.piece_choice != ""):
            return True
        
        return False
        
    def find_orig_sq(self):
        """ Determine original move square
            from info stored in self....
            Some thinking to do
            e.g. destination: e4 might come from e2 or e3
            or e5 (if black)
        """
        if self.is_pawn(self.piece):
            return self.find_orig_sq_pawn()
    
    def rel_sq(self, base_sq, at_rank=None, rel_rank=None):
        """ find square relative to given sq
        :sq: base square
        :at_rank: get sq with base_sq file with at_rank
        :rel_rank: get sq with base_sq file with rank of base_sq rank+rel_rank
        :returns: sq
        """
        if at_rank is not None:
            base_sq_file,base_sq_rank = self.sq_to_file_rank(base_sq)
            at_sq = self.file_rank_to_sq(file=base_sq_file,
                                         rank=at_rank)
        
        if rel_rank is not None:
            dest_file,dest_rank = self.sq_to_file_rank(self.dest_sq,
                                                       to_int=True)
            at_sq = self.file_rank_to_sq(file=dest_file,
                                         rank=dest_rank+rel_rank)
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
    Links to board functions
    """

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
        
    def get_piece(self, sq=None, file=None, rank=None):
        """ Get piece at sq, None if empty
        :sq: square notatin e.g., a1 if present
            else
        :file: file letter or int:1-
        :rank: rank str or int: 1- 
        """
        return self.board.get_piece(
            sq=sq, file=file, rank=rank)

    
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
        
    def make_move(self, orig_sq=None, dest_sq=None,
                  spec=None,
                  dest_sq_mod=None,
                  update_to_move=None):
        """ Make move after decode
        Update to_move iff successful
        :orig_sq: origin square for move
        :dest_sq: destination square for move
        :spec: move specification
        :dest_sq_mod: alternate piece for destination e.g. promotion 
        :update_to_move: change to_move default: True - change
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
        if update_to_move is None:
            update_to_move = self.update_to_move
            
        return self.board.make_move(orig_sq=orig_sq,
                                    dest_sq=dest_sq,
                                    dest_sq_mod=dest_sq_mod,
                                    update_to_move=update_to_move,
                                    spec=spec)

    def sq_to_file_rank(self, sq, to_int=False):
        """ split sq into file, rank pair
        :sq: square notation
        :to_int: True - return file,rank as ints 1-
        :returns: (file, rank) e.g. a1  or to_int 1,1
        """
        return self.board.sq_to_file_rank(self, sq, to_int=to_int)

            
if __name__ == "__main__":
    
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    SlTrace.clearFlags()

    cb = Chessboard()
    cb.standard_setup()
    cbp = ChessboardPrint(cb)
    cm = ChessMove(cb)
    for move_spec in ["e4", "e5", "Nf3", "Nc6", "Ncf3", "Qh4e1"]:
        if cm.decode(move_spec):
           SlTrace.lg(f"{move_spec}: {cm.err}")
        else:
            SlTrace.lg(f"move: {cm}")
                
        if cm.make_move():
            SlTrace.lg(cm.err)
            SlTrace.lg("Quitting")
            break
