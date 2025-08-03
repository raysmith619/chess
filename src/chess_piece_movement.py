#chess_piece_movement.py
""" 
Handles peice movement rules
Determines available destination squares
based on piece, square, board conditions
"""
import re

from select_trace import SlTrace

from chess_error import ChessError

class CastleInfo:

    def __init__(self,
            can_castle = False,
            piece = None,          # our piece
            dest_sq = None,        # our piece destination sq
            king_sq = None,        # king's starting sq
            rook_sq = None,        # rook's starting sq
            ):
        self.can_castle = can_castle
        self.piece = piece
        self.dest_sq = dest_sq
        self.king_sq = king_sq      # Original sq
        self.rook_sq = rook_sq
        
class ChessPieceMovement:

    """
    Piece movement
    The following determines the possible piece movement.
    In general, a piece's possible movement is specified by:
        1. list of directions each of the form (x,y,special)
            x is change in file(column)
            y is change in rank(row) (as viewed by white)
            special: "move" - use only if a move
                    "capture" - use only if a capture
        2. repition, number of times which the direction change
           can be applied.
            The number of repititions depends on piece type.
                In the case of pawns: 2 for first move, else 1
                In case of knight: 1
                Others: number of rows or columns
    by piece or piece capture, if different than move
    arranged in clockwise, starting by up/to right
    NOTE: change is in the "forward" direction, negated for black
           As, except for pawns, the lists are symetric in y for
           content - For efficiency/clarity, we provide
           a black pawn list "p-black" which replicates the "p"
           entry with y negated
    As for dir "capture" entries, these entries take effect if
    and only if their use can effect a capture, i.e., the
    destination square is occupied by an opponent.
    EP capture is effect, if the previous opponent move is a
    2-square pawn move jumping the capture square. 
    """      
    piece_type_dir_d = {
        # lists of tuples
        #   PAIR: (X,Y) or TRIPLE: (x,y,"capture"/"move")
        #   "capture" only if move is a capture
        #   "move" only move is not capture
        #   default: move, if empty or capture if not empty
        # pawn:
        #       rep: first move 1, else 2
        "p" : [(0,1,"move"),
               (-1,1, "capture"), (1,1,"capture")],
        # black pawn MUST equal "p" with y entries negated
        "p-black" : [(0,-1,"move"),
            (-1,-1, "capture"), (1,-1,"capture")],
        
        "n" : [(1,2), (2,1), (2,-1), (1,-2),
               (-1,-2), (-2,-1), (-2,1), (-1,2)],
        "b" : [(1,1), (1,-1), (-1,-1), (-1,1)],
        "r" : [(0,1), (1,0), (0,-1), (-1,0)],
    }
    piece_type_dir_d["q"] =  piece_type_dir_d["r"] + piece_type_dir_d["b"]
    piece_type_dir_d["k"] = piece_type_dir_d["q"] # only one sq
       
    def __init__(self, board):
        self.board = board
        self.spec = None    # Set by move decode
                            # to facilitate debugging
                            
    def assert_sqs(self, sqs, sq_only=None,
                   sq_in=None, sq_out=None, desc=None):
        """ Assert squares are filled, not filled
        :sqs: dictionary of pieces by squares
        :sq_only: these and only these are filled
            == sq_in=these, sq_out=all not in sq_in
        :sq_in: filled squares
            str: str: space, comma, or comma space separated sq notation
            list: list of sq notation
        :sq_only: filled squares
            and all other squares are missing
        :sq_out: empty squares
            str: space, comma, or comma space separated sq notation
            list: list of sq notation
        :desc: descripion of test
            default: No description
        :reports: reports on fails
                keeps count self.assert_fail_count
                raises exception when assert_fail_count_max reached
            """
        return self.board.assert_sqs(sqs, sq_only=sq_only,
                   sq_in=sq_in, sq_out=sq_out, desc=desc)

    def leave_king_in_ckeck(self, dest_sq=None, orig_sq=None):
        """ Check if this piece move would leave our king in check
        Short-circuit implied move to avoid recursion
        :orig_sq: origin square for move
        :dest_sq: destination square
        :returns: True iff king of the side in orig_sq is in check after this move
        """
        dest_piece = self.get_piece(dest_sq)
        if self.piece_to_type(dest_piece) == 'k':
            return False    # Oponent's king is in check
        
        move_piece = self.get_piece(sq=orig_sq)
        if move_piece is None:
            SlTrace.lg(f"Original sq:{orig_sq} is empty"
                       f" - not an actual game move")
            return False
        ck_board = self.board.copy()   # compromise from playing with
                                        # original board
        ck_board.place_piece(move_piece, dest_sq)
        if ck_board.poss_en_passant == dest_sq:
            ck_board.clear_sq(
                    ck_board.poss_en_passant_rm_sq)        
        ck_board.clear_sq(orig_sq)
        kpiece = self.piece_to_king(move_piece)
        king_pss = self.get_pieces(piece=kpiece, board=ck_board)
        if len(king_pss) == 0:
            SlTrace.lg(f"No king for piece: {move_piece}", "trace_no_king")
            return False    # Our king is not on board
        
        if len(king_pss) > 1:
            SlTrace.lg(f"Too many kings for piece: {move_piece} : {king_pss}")
            return False
        
        king_ps = king_pss[0]
        king_sq = self.ps_to_sq(king_ps)

        
        if self.is_attacked(move_piece, king_sq, board=ck_board):
            return True         # King would be attacked
        
        return False


    def get_move_to_sqs(self, piece, orig_sq=None,
                        add_piece=False):
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
        :add_piece: True if add piece to board (Deprecated)
                    mostly for testing
                    default: False
        :returns: dictionary of candidate destination squares
                Empty if none
                None if error
        """
        if add_piece:
            self.place_piece(piece=piece, sq=orig_sq)
        piece_type = self.piece_to_type(piece)
        if piece_type not in ChessPieceMovement.piece_type_dir_d:
            self.err = f"get_move_to_sqs {piece}"
            return None
        if piece_type in ['k', 'n']:
            rep = 1
        else:
            rep = None  # Use default - max
        # Get possible destination squares
        move_to_sqs_base = self.get_move_sqs_base(
            piece, orig_sq=orig_sq,
            rep=rep)
        
        # Avoid leaving king in check
        # or king passing through check via castling
        move_to_sqs = {}
        for sq in move_to_sqs_base:
            if not self.leave_king_in_ckeck(dest_sq=sq,
                                   orig_sq=orig_sq):
                move_to_sqs[sq] = self.get_piece(sq)
        return move_to_sqs

    def square_discard_on_check(self,
                                orig_sq=None,
                                dest_sq=None,
                                move_to_sqs_castle=None):
        """ Check if candidate move-to square should be
        discarded because king would be placed in check
        :orig_sq: original square
        :dest_sq: destination square
        :move_to_sqs_castle: dictionary, by dest square
                            of castle info (CastleInfo)
        :returns: True iff square should be discarded
        """
        # First deal if a castle move
        # Note leave_king_in_ckeck assumes one piece movement
        if dest_sq in move_to_sqs_castle:
            castle_info = move_to_sqs_castle[dest_sq]
            return self.castle_discard(castle_info)
        
        # Just verify not leaving king in check                    
        return self.leave_king_in_ckeck(dest_sq=dest_sq,
                                   orig_sq=orig_sq)

    def castle_discard(self,castle_info):
        """ Check if candidate castle destination square
        is to be discarded
        :castle_info: of castle information (CastleInfo)

        """
        piece = castle_info.piece
        to_move = self.piece_to_move(piece)
        king_sq = castle_info.king_sq
        rook_sq = castle_info.rook_sq
        king_trav = self.get_intervening_sqs(king_sq, rook_sq,
                                             include_first=True,
                                             include_last=False)
        king = self.get_piece(king_sq)
        for sq in king_trav:
            ps = self.to_piece_sq(king, sq)
            attsqs = self.get_attacking_pieces(ps, to_move)
            if len(attsqs) > 0:
                return True     # An attacker
            
    def get_adj_sq(self, sq, dir):
        """ Get adjacent square in direction (x,y) 
        :sq: our square e.g, a1
        :dir: direction (x_inc,y_inc) or (x_inc,y_inc,special)
        :returns: adjacent square, None if off board
        """
        file_no, rank_no = self.sq_to_file_rank(sq, to_int=True)
        file_inc, rank_inc = dir[0],dir[1]
        file_no += file_inc   
        rank_no += rank_inc
        if (file_no < 1 or file_no > self.get_nsqx()
            or rank_no < 1 or rank_no > self.get_nsqy()):
            return None
            
        adj_sq = self.file_rank_to_sq(file=file_no, rank=rank_no)
        return adj_sq
    
    def get_move_sqs_base(self, piece,
                            orig_sq,
                            rep=None):
        """ Get squares to which we can move
        without leaving the board nor hitting a
        square of our own color
        No checking for ending with king in check.
        A dictionary, by destination square, of moves,
        of destination square created via castling is
        created and returned as the second tuple
        member.
        :piece: our piece
        :orig_sq: original(move starting)
        :rep: maximum repition default: maximum rank,file
        :returns: dictionary, by dest sq, of pre-move contents
                    
        """
        if piece == 'p' or piece == 'P':
            return self.get_move_pawn_dir_sqs(piece, orig_sq)
        
        if rep is None:
            rep = max(self.get_nsqx(), self.get_nsqy())
            
        sqs_d = {}              # Dictionary, by dest_sq, of contents
        move_sqs_castle = {}    # Dictionary, by dest_sq, of castle info
        
        piece_type = self.piece_to_type(piece)
        our_color = self.piece_color(piece)
        list_dirs = self.piece_type_dir_d[piece_type]
        for dir in list_dirs:
            sq = orig_sq
            for i in range(rep):
                sq = self.get_adj_sq(sq, dir)
                if sq is None:
                    break   # over board edge
                sq_piece = self.get_piece(sq)                    
                if sq_piece is None:
                    sqs_d[sq] = sq_piece    # save empty    
                    continue
                
                # Square is occupied                
                sq_piece_color = self.piece_color(sq_piece)
                if sq_piece_color == our_color:
                    break   # End, Not a capture situation
                
                sqs_d[sq] = sq_piece
                break       # End if capturing piece

        """
        Check for castling options
        Produce dictionary by dest_sq of
            castle info: (CastleInfo)
        Each info is enough to call castle_discard
        and determine if this dest_sq should
        be discarded.
        """
        if piece_type == 'k' or piece_type == 'r':
            kingside = True
            castle_info = self.castle_info(piece,
                            orig_sq, kingside=kingside,
                            ck_for_check=True)
            if castle_info.can_castle:
                dest_sq = castle_info.dest_sq
                sqs_d[dest_sq] = self.get_piece(dest_sq)
                
            kingside = False    # queenside
            castle_info = self.castle_info(piece,
                                orig_sq, kingside=kingside,
                                ck_for_check=True)
            if castle_info.can_castle:
                dest_sq = castle_info.dest_sq
                sqs_d[dest_sq] = self.get_piece(dest_sq)
                
        return sqs_d

    pawn_dirs = {
        #       rep: first move 1, else 2
        "P" : [(0,1,"move"),
               (-1,1, "capture"), (1,1,"capture")],
        # black pawn MUST equal "p" with y entries negated
        "p" : [(0,-1,"move"),
            (-1,-1, "capture"), (1,-1,"capture")],
        }

    def get_move_pawn_dir_sqs(self, piece,
                            orig_sq):
        """ For pawns, Get squares to which we can move
        without leaving the board nor hitting a
        square of our own color
        :piece: our piece   "P" - WHITE, "p" -black
        :orig_sq: our square
        :returns: dictionary, by sq, of moveable squares
        """
        sqs_d = {}
        piece_type = self.piece_to_type(piece)
        our_color = self.piece_color(piece)
        rep = 2 if self.pawn_is_at_origin(piece, orig_sq) else 1
        list_dirs = self.pawn_dirs[piece]    
        for dir in list_dirs:
            special_dir = dir[2]
            sq = orig_sq
            repadj = 1 if special_dir == "capture" else rep
            for i in range(repadj):
                sq = self.get_adj_sq(sq, dir)
                if sq is None:
                    break   # over board edge

                # Check on en passant
                if (self.board.poss_en_passant == sq
                    and special_dir == "capture"):
                        sqs_d[sq] = None    # Maybe we should "place" the pawn here?
                        break   # End  of this dir
                    
                sq_piece = self.get_piece(sq)                    
                if sq_piece is None:
                    if special_dir == "capture":
                        break  # quit if capture sq is empty
                    else:    
                        sqs_d[sq] = sq_piece    # save empty    
                        continue
                else:   # Square is occupied                
                    sq_piece_color = self.piece_color(sq_piece)
                    if special_dir == "capture":
                        if sq_piece_color == our_color:
                            break   # End, Not a capture situation
                        else:
                            sqs_d[sq] = sq_piece
                            break       # End if capturing piece
                    else:
                        break   # blocked by any piece
        return sqs_d

    def castle_orig_dest_sq(self, piece, kingside=True):
        """ Returns castle destination square
        Assumes valid checks already passed
        :piece: piece
        :kingside: king/queen side default: kingside(True)
        :returns: orig_sq, dest_sq
        """
        piece_type = self.piece_to_type(piece)
        to_move = self.piece_to_move(piece)
        if kingside:
            if to_move == 'white':
                king_orig_sq = 'e1'
                king_dest_sq = 'g1'
                rook_orig_sq = 'h1'
                rook_dest_sq = 'f1'
            else:
                king_orig_sq = 'e8'
                king_dest_sq = 'g8'
                rook_orig_sq = 'h8'
                rook_dest_sq = 'f8'
        else:
            if to_move == 'white':
                king_orig_sq = 'e1'
                king_dest_sq = 'c1'
                rook_orig_sq = 'a1'
                rook_dest_sq = 'd1'
            else:
                king_orig_sq = 'e8'
                king_dest_sq = 'c8'
                rook_orig_sq = 'a8'
                rook_dest_sq = 'd8'
                
        if piece_type == 'k':
            orig_sq = king_orig_sq
            dest_sq = king_dest_sq
            
        elif piece_type == 'r':
            orig_sq = rook_orig_sq
            dest_sq = rook_dest_sq
        return orig_sq, dest_sq
        
    def castle_info(self, piece, orig_sq, kingside=True,
                   ck_for_check=False):
        """ Check if this piece (type and color)
        can castle on side requested (kinside)
        :piece: kKrR, king(black,white), rook(black,white)
               at original kingside square
        :orig_sq: piece's original square 
        :kingside: True=kingside, else queenside
                default: True=kingside
        :ck_for_check: True - check for king:
                in,through,ending in check
                default: True  - check
        :returns: castling info (CastleInfo)
        """
        no_castle = CastleInfo(can_castle=False)    # not casle value
        piece_type = self.piece_to_type(piece)
        to_move = self.piece_to_move(piece)
        if not self.castle_opportunity(kingside=kingside,
                               to_move=to_move):
            return no_castle
        
        # Check for basic positional requirements
        if not self.castle_piece_req(piece, orig_sq, kingside=kingside):
            return no_castle
            
        king = self.piece_to_king(piece)
        king_orig_sq, king_dest_sq = self.castle_orig_dest_sq(
                            king,kingside=kingside)
        rook = self.piece_to_rook(piece)
        rook_orig_sq, rook_dest_sq = self.castle_orig_dest_sq(
                            rook, kingside=kingside)
        dest_sq = king_dest_sq if piece_type == 'k' else rook_dest_sq

        if ck_for_check:
            # Check king in/through check restriction
            # Find our king and rook
            king_trav_sqs = self.get_intervening_sqs(
                        king_orig_sq, king_dest_sq,
                        include_first=True,
                        include_last=True)
            for sq in king_trav_sqs:
                if self.is_attacked(king, sq):
                    return no_castle    # Can't start, land
                                    # or pass occupied
        
        castle_info = CastleInfo(True, piece, dest_sq, 
                       king_orig_sq, rook_orig_sq)
        return castle_info

    def castle_piece_req(self, piece, orig_sq, kingside=True):
        """ Check if pieces rook and king are in proper positions
        for such castle, destinations are vacant and no pieces
        are in the traversal squares
        :piece: piece to castle
        :orig_sq: square for piece
        :returns: True iff pieces are present in starting squares
                    and destination squares are vacant
        """
        piece_type = self.piece_to_type(piece)
        if piece_type != 'k' and piece_type != 'r':
            return False
        
        # Find our king and rook
        king = self.piece_to_king(piece)
        king_orig_sq, king_dest_sq = self.castle_orig_dest_sq(king,
                                                    kingside)
        
        rook = self.piece_to_rook(piece)
        rook_orig_sq, rook_dest_sq = self.castle_orig_dest_sq(rook,
                                                              kingside)
        # Check if our piece is in the proper starting square
        if piece_type == 'r' and orig_sq != rook_orig_sq:
            return False
        if piece_type == 'k' and orig_sq != king_orig_sq:
            return False
        
        # Check if both king and rook at proper position
        if self.get_piece(king_orig_sq) != king:
            return False
        
        if self.get_piece(rook_orig_sq) != rook:
            return False
        
        # Check if destination squares are vacant
        # Note this is redundant with vacant traversal
        # test below - should we do simple test first?
        if self.get_piece(king_dest_sq) != None:
            return False    # dest is occupied
        
        if self.get_piece(rook_dest_sq) != None:
            return False    # dest is occupied
     
        # Check traversal squares are vacant
        trav_sqs = self.get_intervening_sqs(king_orig_sq,
                                            rook_orig_sq)
        for sq in trav_sqs:
            if self.get_piece(sq) is not None:
                return False    # Can't land or pass occupied
       
        return True

    def is_at_origin(self, piece, sq):
        """ Check if pawn at origin sq
        :piece: piece
        :sq: occupying square
        :returns TTrue if pawn at origin
        """
        file_int, rank_int = self.sq_to_file_rank(sq, to_int=True)
        if piece == "p":
            return True if rank_int == 7 else False
    
        if piece == "P":
            return True if rank_int == 2 else False
        
        raise ChessError("{pice = } not a pawn")

    def piece_to_king(self, piece):
        """ Get this piece's king
        :piece: our   piece
        :returns: the king for this piece's color
        """
        return 'K' if piece.isupper()  else 'k'

    def piece_to_rook(self, piece):
        """ Get this piece's rook
        :piece: our   piece
        :returns: the rook for this piece's color
        """
        return 'R' if piece.isupper()  else 'r'
    
    """ 
    Links to board
    """    


    def castle_opportunity(self, to_move="white", kingside=True):
        """ Check if the opportunity for castle is present
        :to_move: whose move default: white
        :kingside: True if kingside, False: queenside
                default: kingside
        :returns: True if opportunity is present
        """
        return self.board.castle_opportunity(to_move=to_move,
                                             kingside=kingside)
        
    def get_opponent_pieces(self, to_move=None, board=None):
        """ Get all side to move pieces
        :to_move: black/white
            default: get from board
        :board: Chessboard default: self.board
        :returns:   list of piece_square settings
        """
        if board is None:
            board = self.board
        return board.get_opponent_pieces(to_move=to_move)
        
    def piece_to_move(self, piece):
        """ get to_move from piece
        capital pieces are white
        :piece: piece e.g. K white king, k black king
        :returns: black/white for whos move
        """
        return self.board.piece_to_move(piece)
            
    def file_rank_to_sq(self, file=None, rank=None):
        """ Convert rank, file to sq notation
        :file: int 1-8 or str: a-h
        :rank: int 1-8 or str 1-8
        :returns: sq notation
        """
        return self.board.file_rank_to_sq(file=file, rank=rank)

    def get_intervening_sqs(self, first_sq, last_sq,
                            include_first=False,
                            include_last=False,
                            board=None):
        """ Get squares between first and last
        :first_sq: beginning square
        :last_sq: last square
        :include_first: True - include first square, else omit
                    default: False - omit
        :include_last: True - include last square, else omit
        :board: Chessboard default: self.board
        :returns: dictionary, by sq, of contained pieces, None == empty
        """
        if board is None:
            board = self.board
        return board.get_intervening_sqs(first_sq,
                                        last_sq,
                                        include_first=include_first,
                                        include_last=include_last)

    def get_nsqx(self):
        """ Get board size, number of squares in x direction
        :returns: number squares x direction (wide, files)
        """
        return self.board.nsqx

    def get_nsqy(self):
        """ Get board size, number of squares in x direction
        :returns: number squares x direction (wide, ranks)
        """
        return self.board.nsqy

    def all_sqs(self):
        """ Create dictionary of all squares
        :returns: dictionary by sq of place holder
        """
        return self.board.all_sqs()
        
    def clear_board(self):
        """ Empty board of pieces
        """
        self.board.clear_board()

    def pawn_is_at_origin(self, piece, sq):
        """ Check if pawn at original square
        :piece: p/P - black/white pawn
        :s1: current square
        """
        file, rank = self.sq_to_file_rank(sq, to_int=True)
        if piece == 'p' and rank == 7:
            return True
        
        if piece == 'P' and rank == 2:
            return True
        
        return False
    
            
    def is_moved(self, sq):
        """ Tell if piece, originating at this square
        has ever been moved
        :sq: origin square
        """
        return self.board.is_moved(sq)
    
    def set_as_moved(self, sq):
        """ Set piece, originating at this sq
        as moved.  Note if another piece is moved from this
        square the original piece has to have moved
        """
        return self.board.set_as_moved(sq)

    def clear_assert_test_count(self):
        """ Clear assert fail count
        """
        self.board.clear_assert_test_count()

    def sq_to_file_rank(self, sq, to_int=False):
        """ split sq into file, rank pair
        :sq: square notation
        :to_int: True - return file,rank as ints 1-
        :returns: (file, rank) e.g. a1  or to_int 1,1
        """
        return self.board.sq_to_file_rank(sq, to_int=to_int)

    def get_attacking_pieces(self, ps, to_move=None):
        """ Get dictionary of piece-squares
        which can attack/capture given sq
        If the attacked piece is a king, the
        test for the opponent's move is short-circuited
        with no test for opponent left in check.
        :ps: piece-square or sq
            if sq use to_move 
        :to_move: side to move (our side)
                default: the board's
        :returns: dictionary by squares, of pieces which can attack our
                square sq
        """
        if len(ps) > 2:
            target_piece,target_sq = self.ps_to_p_sq(ps)
            to_move = self.piece_to_move(target_piece)
        else:
            target_piece = None
            target_sq = ps
            
        if to_move is None:
            to_move = self.get_to_move()
        
        target_piece_type = self.piece_to_type(target_piece)
        att_pcs = self.att_pieces_black if to_move == "white" else self.att_pieces_white
        att_piece_sqs = self.get_pieces(att_pcs)   
        attacking_psq = {}
        
        # If target is king, attackers need not worry about
        # going into check
        ck_for_check = False if target_piece_type=='k' else True
        for att_psq in att_piece_sqs:
            att_piece, att_sq = self.ps_to_p_sq(att_psq)
            att_move_to_sqs = self.get_move_to_sqs(att_piece,
                                        orig_sq=att_sq,
                                        ck_for_check=ck_for_check)
            if target_sq in att_move_to_sqs:
                attacking_psq[att_sq] = att_piece 
        return attacking_psq
    
    def is_attacked(self, piece, sq, board=None):
        """ Check if piece is attacked (by an opponent)
        :piece: our piece Upper case for white
        :sq: piece's square
        :board: current board default:self.board
        :returns: True if attacked
        """
        if board is None:
            board = self.board
        to_move = self.piece_to_move(piece)
        opp_pieces = self.get_opponent_pieces(to_move, board=board)
        for ps in opp_pieces:
            opp_piece, opp_sq = self.ps_to_p_sq(ps)
            if self.is_attacking(opp_piece, orig_sq=opp_sq, dest_sq=sq,
                                 board=board):
                return True
        
        return False    # No attackers

    def is_attacking(self, piece, orig_sq, dest_sq, board=None):
        """ Check if the piece(piece), if occuping the square(orig_sq)
        can capture an opponent's piece, if occupying dest_sq.
.
        :piece: attacking piece
        :orig_sq: attacking piece's square
        :dest_sq: destination square, need not be occupied
        :board: Chessboard default: self.board
        :returns: True iff an opponent's piece, if present
                    in dest_sq, could be immediately
                    captured by this piece from the orig_sq 
        """
        if board is None:
            board = self.board
        piece_type = self.piece_to_type(piece)
        if piece_type == 'p':
            return self.is_attacking_pawn(piece, orig_sq, dest_sq,
                                          board=board)
        
        if piece_type == 'k':
            return self.is_attacking_king(piece, orig_sq, dest_sq,
                                          board=board)
        
        if piece_type == 'q':
            return self.is_attacking_queen(piece, orig_sq, dest_sq,
                                          board=board)
        
        if piece_type == 'r':
            return self.is_attacking_rook(piece, orig_sq, dest_sq,
                                          board=board)
        
        if piece_type == 'b':
            return self.is_attacking_bishop(piece, orig_sq, dest_sq,
                                          board=board)
        
        if piece_type == 'n':
            return self.is_attacking_knight(piece, orig_sq, dest_sq,
                                          board=board)

    def is_attacking_knight(self, piece, orig_sq, dest_sq, board=None):
        """ Check if knight attacking
        :piece: attacking piece
        :orig_sq: attacking square
        :dest_sq: attacked square
        :board: Chessboard default: self.board NOT USED
        :returns: True if attacked
        """
    
        inc_x,inc_y = self.inc_xy(orig_sq, dest_sq)
        if (abs(inc_x) == 1 and abs(inc_y) == 2
            or abs(inc_x) == 2 and abs(inc_y) == 1):
            return True
        
        return False
    
    def is_attacking_pawn(self, piece, orig_sq, dest_sq, board=None):
        """ Check if knight attacking
        :piece: attacking piece
        :orig_sq: attacking square
        :dest_sq: attacked square
        :board: our board default: self.board
        :returns: True if attacked
        """
        if board is None:
            board = self.board    
        inc_x,inc_y = self.inc_xy(orig_sq, dest_sq)
        if self.piece_color(piece) == 'white':
            capt_incs = (-1,1), (1,1)
        else:
            capt_incs = (-1,-1), (1,-1)
        for capt_inc in capt_incs:
            if capt_inc[0] == inc_x and capt_inc[1] == inc_y:
                return True
    
    def is_attacking_king(self, piece, orig_sq, dest_sq, board=None):
        """ Check if king attacking
        :piece: attacking piece
        :orig_sq: attacking square
        :dest_sq: attacked square
        :returns: True if attacked
        """    
        if board is None:
            board = self.board    
        inc_x,inc_y = self.inc_xy(orig_sq, dest_sq)
        capt_incs = ChessPieceMovement.piece_type_dir_d['k']
        for capt_inc in capt_incs:
            if capt_inc[0] == inc_x and capt_inc[1] == inc_y:
                return True
         
        return False   
    
    def is_attacking_queen(self, piece, orig_sq, dest_sq, board=None):
        """ Check if queen attacking
        :piece: attacking piece
        :orig_sq: attacking square
        :dest_sq: attacked square
        :returns: True if attacked
        """    
        if board is None:
            board = self.board    
        if self.is_attacking_rook(piece,orig_sq,dest_sq, board=board):
            return True
        
        if self.is_attacking_bishop(piece,orig_sq,dest_sq, board=board):
            return True
        
        return False
    
    def is_attacking_rook(self, piece, orig_sq, dest_sq, board=None):
        """ Check if rook attacking
        :piece: attacking piece
        :orig_sq: attacking square
        :dest_sq: attacked square
        :returns: True if attacked
        """
        if board is None:
            board = self.board
        inc_x,inc_y = self.inc_xy(orig_sq, dest_sq)
        if inc_x == 0 or inc_y == 0:
            trav = self.get_intervening_sqs(orig_sq, dest_sq,
                                                include_first=False,
                                                include_last=False,
                                                board=board)
            for sq in trav:
                piece = board.get_piece(sq)
                if piece is not None:
                    return False    # Something in the way
            return True             # Nothing in the way
        
        return False
    
    def is_attacking_bishop(self, piece, orig_sq, dest_sq, board=None):
        """ Check if bishop attacking
        :piece: attacking piece
        :orig_sq: attacking square
        :dest_sq: attacked square
        :returns: True if attacked
        """
        if board is None:
            board = self.board
        inc_x,inc_y = self.inc_xy(orig_sq, dest_sq)
        if abs(inc_x) == abs(inc_y):
            trav = self.get_intervening_sqs(orig_sq, dest_sq,
                                                include_first=False,
                                                include_last=False,
                                                board=board)
            for sq in trav:
                piece = board.get_piece(sq)
                if piece is not None:
                    return False    # Something in the way
            return True             # Nothing in the way
        
        return False
                
        capt_incs = ChessPieceMovement.piece_type_dir_d['k']
        for capt_inc in capt_incs:
            if capt_inc[0] == inc_x and capt_inc[1] == inc_y:
                return True

    def inc_xy(self, orig_sq, dest_sq):
        """ Get relative change in file(x) and rank(y) between
        orig_sq moveing to dest_sq
        :orig_sq: starting square
        :dest_sq: ending square
        :returns: (change in file(x), rank(y))
        """
        orig_file_no, orig_rank_no = self.sq_to_file_rank(orig_sq, to_int=True)
        dest_file_no, dest_rank_no = self.sq_to_file_rank(dest_sq, to_int=True)
        inc_x = dest_file_no - orig_file_no
        inc_y = dest_rank_no - orig_rank_no 
        return inc_x, inc_y   
        
    def get_assert_test_count(self):
        """ Get test count
        """
        return self.board.get_assert_test_count()

    def get_castle_move_to_sqs(self, piece, orig_sq):
        """ Determine which, if any squares the king can move to 
        by castling (kingside, queenside), we assume it is the king's
        turn to move.
             Requirements
               * neither king nor rook have moved
               * no interveining pieces
               * king must not move from,through or to check
        :piece: k for black king, K for white king
        :orig_sq: orign square for king
        :returns: dictionary of destination squares, empty if none
        """
        move_to_sqs = {}
        to_move = self.piece_to_move(piece)
        if self.can_castle(kingside=True):
            kside = self.castle_from_to(to_move=to_move)
            king_sq, king_dest, rook_sq, rook_dest = kside
            move_to_sqs[king_dest] = None
        if self.can_castle(kingside=False):
            qside = self.castle_from_to(kingside=False, to_move=to_move)
            king_sq, king_dest, rook_sq, rook_dest = qside
            move_to_sqs[king_dest] = None
        return move_to_sqs

    def do_test(self, desc=None, desc2=None,trace=None):
        """ start test, test_group
        :desc: description
            default: continue with prev description
        :desc2: additional description
        :trace: possible trace flag
        """
        self.board.do_test(desc=desc, desc2=desc2, trace=trace)


    def clear_assert_fail(self):
        """ Clear assert fail count
        """
        self.board.clear_assert_fail()
        
    def set_assert_fail_max(self, max=10):
        """ Set maximum assert_fail_reports till
            exception raised
        :max: maximum till quit
        """
        self.board.set_assert_fail_max(max=max)
        
    def assert_fail_report(self, err):
        """ Report assert fail
        :err: report string
        """
        self.board.assert_fail_report(err)

    def get_assert_fail_count(self):
        """ Get test fail count - numbers of test errors
        """
        return self.board.get_assert_fail_count()

    def get_assert_first_fail(self):
        """ Get first failed test no + fail msg
        :return: fail test no
        """
        return self.board.get_assert_first_fail()
            
    def get_piece(self, sq=None, file=None, rank=None):
        """ Get piece at sq, None if empty
        :sq: square notatin e.g., a1 if present
            else
        :file: file letter or int:1-
        :rank: rank str or int: 1- 
        """
        return self.board.get_piece(sq=sq, file=file, rank=rank)
    
    def get_pieces(self, piece=None, piece_type=None, board=None):
        """ Get piece-square list for board setting
        :piece: get only matching pieces
            OR
        :piece_type get only matching piece types(case insensitive)
                e.g q - all both color queens
                "empty" - all empty squares
                "any" - any piece type
        :board: board to find pieces default: self.board
        :returns: list of piece_square settings
        """
        if board is None:
            board = self.board
        return board.get_pieces(piece=piece, piece_type=piece_type)

    def piece_color(self, piece):
        """ Get piece's color
        :piece: piece uppercase for white
        """
        return self.board.piece_color(piece)

    def piece_to_type(self, piece):
        """ Get piece's type (lowercase of piece)
        :piece: piece uppercase for white
        :returns: piece type (lowercase)
        """
        return self.board.piece_to_type(piece)
    
    def ps_to_sq(self, ps):
        """ Get square from piece_square
        :ps: piece-square spec
        :returns: square
        """
        return self.board.ps_to_sq(ps=ps)
        
    def place_pieces(self, piece_sqs):
        """ Place piece in square, first deleting destination contents
        :piece: piece, e.g. p black pawn, P white pawn
        :sq: destination square, e.g. e1
        :returns: previous contents of destination sq, None if empty
        """
        return self.board.place_pieces(piece_sqs=piece_sqs)
        
    def assert_pieces(self, piece_sqs):
        """ Verify piece(s) is(are) present
        :piece: piece, e.g. p black pawn, P white pawn
        :sq: destination square, e.g. e1
        :returns: previous contents of destination sq, None if empty
        """
        return self.board.assert_pieces(piece_sqs=piece_sqs)


    def clear_sq(self, sq):
        """ Empty square
        :sq: square notation, e.g., e1
        """
        self.board.clear_sq(sq)
        
        
    def place_piece(self, piece, sq=None):
        """ Place piece in square, first deleting destination contents
        :piece: piece, e.g. p black pawn, P white pawn
        :sq: destination square, e.g. e1
        :returns: previous contents of destination sq, None if empty
        """
        return self.board.place_piece(piece, sq=sq)
        
    def make_move(self, orig_sq=None, dest_sq=None,
                  spec=None,
                  dest_sq_mod=None,
                  update=None):
        """ Make move after decode
        Update to_move iff successful
        :orig_sq: origin square for move
        :dest_sq: destination square for move
        :spec: move specification
        :dest_sq_mod: alternate piece for destination e.g. promotion 
        :update: change to_move default: True - change
        :returns: None if successful, else err msg
        """
        return self.board_make_move(orig_sq=orig_sq, dest_sq=dest_sq,
                  spec=spec,
                  dest_sq_mod=dest_sq_mod,
                  update=update)
        
    def to_piece_sq(self, piece=None, sq=None):
        """Produce piece_square even if piece is None
        :piece: piece or None if empty
        :sq: square
        """
        return self.board.to_piece_sq(piece=piece, sq=sq)

    def get_prev_move(self):
        """ Get previous move, with no change
        Used to check for thigs suchas E.P
        :returns: previous move (ChessSaveUnit)
            None if no previous move saved
        """
        return self.board.get_prev_move()


    def remove_piece(self, sq):
        """ Remove piece from square
        :sq: sq to remove OK if sq is empty
        """
        self.board.remove_piece(sq=sq)
            
    def save_move(self, orig_sq=None, dest_sq=None,
                  spec=None, orig_sq_2=None, dest_sq_2=None):
        """ Save move info, to enable undo
        :orig_sq: original square location
        :dest_sq: destination square location
        :spec: specification
        :orig_sq_2: optional original square
        :dest_sq_2: optional second destination square
        """
        self.board.save_move(orig_sq=orig_sq, dest_sq=dest_sq,
                  spec=spec, orig_sq_2=orig_sq_2, dest_sq_2=dest_sq_2)

    
    def ps_to_sq(self, ps):
        """ Get square from piece_square
        :ps: piece-square spec
        :returns: square
        """
        return self.board.ps_to_sq(ps)
        
    def ps_to_p_sq(self, ps):
        """ Get piece,sq from piece-square
        :ps: piece-square spec
        :returns: piece,square
        """
        return self.board.ps_to_p_sq(ps)


    """ end of board links """
