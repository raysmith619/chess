#chessboard.py 10Feb2025  crs
"""
Experimentation of manipulation of a chess board
Goals:
    efficient display
    efficient access
"""
import re
import copy

from select_trace import SlTrace

from chess_piece_movement import ChessPieceMovement
from chess_save_unit import ChessSaveUnit
from chess_move import ChessMove
from chess_error import ChessError
from chess_fen import ChessFEN

class Chessboard:
    att_pieces_black = ["k", "q", "r", "b", "n", "p"]
    att_pieces_white = [x.upper() for x in att_pieces_black ]

    def __init__(self,
                 pieces = None,
                 nsqx = 8,
                 nsqy = 8,
                 to_move = "white",
                 standard_setup=True
                ):
        """ Setup board, optional display
        :pieces: pieces to add
                1. Short hand string :(<piece><square>)* <to move> 
                    where <piece> is [KQRBNPkqrbnp] as in FEN
                    where <square> is Algebraic notaion, e.g. e4
                    where <to move> is w for white, b for black
                    OR
                2. FEN:<FEN string>
                default: No additional pieces added
                    FEN is the abbreviation of Forsyth-Edwards Notation,
                    and it is the standard notation to describe positions
                    of a chess game.
                3. STANDARD: - setup basic original position
                    
        :nsqx: Number of squares horizontal
                default: 8
        :nsqy: Number of squares vertical
                default: 8
        """
        self.pieces = pieces
        self.piece_squares = []    # Initial list of pieces, if any
        
        self.nsqx = nsqx
        self.nsqy = nsqy
        self.to_move = to_move
        self.cm = None          # ChessMove
        self.move_stack = []    # Stack of ChessSaveUnit
        self.move_redo_stack = []   # Stack of ChessSaveUnit of undos
        self.update = True # Default - update after make_move
        self.moved_pieces_d = {}  #dictionary, by initial square
                                  #  of pieces who have moved
        self.just_notation = False  # rue if just testing notation
        self.clear_assert_fail()
        self.set_assert_fail_max(10)
        self.cpm = ChessPieceMovement(self)
        err = self.setup_board(pieces=pieces,
                         standard_setup=standard_setup)
        if err:
            raise ChessError(err)
        
    def copy(self):
        """ Copy information for independant opperation
        """
        cb_new = copy.deepcopy(self)        
        return cb_new
                              
    def setup_board(self, pieces=None, standard_setup=True):
        """ Set board internals
        especially board for efficient access to board contents
        :pieces: piece specification, if any
        :standard_setup: standard pieces/position, used if pieces is None
        :returns: error message iff failed else None
        """
        if pieces is None:
            if standard_setup:
                return self.standard_setup()
                
        piece_string = self.pieces
        self.clear_board()
               
        if piece_string is None or piece_string == "":
            return None      # No pieces
        
        if piece_string[0] == ":":  # Check for short form
            short_string = piece_string[1:]
            match_pieces = list(re.finditer(r'([KQRBNPkqrbnp]([a-h])([1-8]))', short_string))
            if not match_pieces:                
                SlTrace.lg(f"short_string: {short_string} is not proper syntax")
                raise Exception(f"short_string: '{short_string}' is not proper piece-square syntax")
            last_piece = match_pieces[-1]
            end_pieces = last_piece.end()
            piece_squares = []
            SlTrace.lg(f"match groups:{match_pieces}")
            to_move_str = short_string[end_pieces:]
            SlTrace.lg(f"pieces:{short_string[:end_pieces]} remainding:{to_move_str}")
            for m in match_pieces:
                self.piece_squares.append(m.group())
            SlTrace.lg(f"match groups:{self.piece_squares}")
            match_to_move = re.match(r'^\s*([wb])', to_move_str)
            if match_to_move:
                to_move = match_to_move.group(1)
            self.to_move = to_move
            SlTrace.lg(f"to_move:{to_move}")        
        elif piece_string.upper().startswith("FEN:"):
            return self.fen_setup(piece_string)
        elif piece_string.upper().startswith("STANDARD:"):
            return self.standard_setup()
        else:    
            return("We don't yet handle anything other than short form")

        
        if len(self.piece_squares) > 0:
            self.add_pieces(self.piece_squares)      # Populate board

    def standard_setup(self):
        """ Setup standard initial setup
        """
        self.clear_board()
        self.piece_squares = []
        return self.fen_setup('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
                                
    def fen_setup(self, fen_str):
        """ Setup board piece_squares from FEN string
        Setup board state piece placement, etc from FEN specification
        :fen_str:  FEN notation string
        :returns: error message text, else None for success
        """
        cf = ChessFEN()
        if cf.parse(fen_str):
            self.err = cf.err
            return cf.err       # Bad syntax
        
        cf.export_to_bd(self)    

    """ 
    Internal board access
    Probably to be  made more efficient in the future
    """
    def is_moved(self, sq):
        """ Tell if piece, originating at this square
        has ever been moved
        :sq: origin square
        :returns: privious value of is_moved
        """
        if sq in self.moved_pieces_d:
            return True
        
        return False
    
    def set_as_moved(self, sq, is_moved=True):
        """ Set originating at this square to is_moved state
        :sq: origin square
        :returns: privious value of is_moved
        """
        prev_moved = self.is_moved(sq=sq)
        if is_moved != prev_moved:
            if (is_moved):
                self.moved_pieces_d[sq] = True
            else:
                if sq in self.moved_pieces_d:
                    del self.moved_pieces_d[sq]         
        return prev_moved
    
    def set_as_moved(self, sq):
        """ Set piece, originating at this sq
        as moved.  Note if another piece is moved from this
        square the original piece has to have moved
        """
        self.moded_pieces_d = sq
        
    def get_assert_test_count(self):
        """ Get test count
        """
        return self.assert_test_count

    def do_test(self, desc=None, desc2=None, trace=None):
        """ start test, test_group
        :desc: description
            default: continue with prev description
        :desc2: additional description
        :trace: possible trace flag
        """
        self.assert_test_count += 1
        if desc is not None:
            self.assert_test_desc =  desc
        self.assert_desc2 = desc2
        self.assert_test_trace = trace
        msg = f"\nTest {self.assert_test_count}:"
        msg += f" {self.assert_test_desc}"
        if desc2 is not None:
            msg += f" {desc2}"
        SlTrace.lg(msg)


    """
    Error processing
    """
       
    def err_add(self, msg=None):
        """ Set and Count errors
        :msg: count as error if msg != ""
            default: self.err - current parsing error message
        :returns: msg
        """
        self.assert_fail_report(err=msg)
        
        return msg
        
    def clear_assert_test_count(self):
        """ Clear assert fail count
        """
        self.clear_asser_fail()

    def clear_assert_fail(self):
        """ Clear assert fail count
        """
        self.assert_test_desc = ""
        self.assert_test_count = 0
        self.assert_fail_count = 0
        self.assert_first_fail = None
        self.assert_first_fail_move_no = 0
        
    def get_assert_fail_count(self):
        """ Get test fail count - numbers of test errors
        """
        return self.assert_fail_count

    def get_assert_first_fail(self):
        """ Get first failed test no + fail msg
        :return: fail test no
        """
        return self.assert_first_fail
            
    def set_assert_fail_max(self, max=10):
        """ Set maximum assert_fail_reports till
            exception raised
        :max: maximum till quit
        """
        self.assert_fail_count_max = max
        
    def assert_fail_report(self, err):
        """ Report assert fail
        :err: report string
        """
        self.assert_fail_count += 1
        SlTrace.lg(f"{self.assert_fail_count}: {err}")
        if self.assert_first_fail is None:
            self.assert_first_fail = f"Test {self.get_assert_test_count()}"
            self.assert_first_fail += f" {self.assert_test_desc}"
            self.assert_first_fail += f" {err}"
            self.assert_first_fail_move_no = self.get_move_no()
            
        if self.assert_fail_count >= self.assert_fail_count_max:
            raise Exception(f"Assert fail maximum"
                            f"({self.assert_fail_count_max}) reached"
                            f" quitting")        

    def get_assert_first_fail_move_no(self):
        """ Get move no at first error
        """
        return self.assert_first_fail_move_no
    def get_err_count(self):
        """ Get error count, using assert -should change
        """
        return self.get_assert_fail_count()
    
    def get_err_first_move_no(self):
        return 
        return self.get_assert_first_fail_move_no()
    
    def get_err_first(self):
        return self.get_assert_first_fail()


    def add_pieces(self, piece_squares, clear_first=True):
        """ add to current setting
        :piece_squares: list of new piece_square setting to add
                        or single piece-square
        :clear_first: clear board board before adding
                default: clear board first
        """
        if clear_first:
            self.clear_board()
        if isinstance(piece_squares,str):
            piece_squares = [piece_squares]
        for ps in piece_squares:
            self.add_piece_square(ps)

    def all_sqs(self):
        """ Create dictionary of all squares
        :returns: dictionary by sq of place holder
        """
        sqs = {}
        for file_no in range(1, self.nsqx+1):
            for rank_no in range(1, self.nsqy+1):
                sq = self.file_rank_to_sq(file=file_no, rank=rank_no)
                sqs[sq] = 'y'
        return sqs
    
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
        if sq_only is not None:
            SlTrace.lg(f"sq_only: {sq_only}", "test_strings")
            SlTrace.lg(f"     in: {sqs}", "found_sqs")
            if isinstance(sq_only, str):
                sq_only = re.split(r'[,\s]\s*', sq_only)
            sqs_in = {}
            for sq in sq_only:
                if sq == '':
                    continue    # ignore empties
                sqs_in[sq] = 'x'
            sqs_all = self.all_sqs()
            sqs_out = {}
            for sq in sqs_all:
                if sq not in sqs_in:    # create set complement
                    sqs_out[sq] = 'z'
            sq_in = list(sqs_in)
            sq_out = list(sqs_out)
            
        if sq_in is not None:
            if sq_only is None:
                SlTrace.lg(f"     in: {sqs}", "found_sqs")
            if isinstance(sq_in, str):
                sq_in = re.split(r'[,\s]\s*', sq_in)
            for sq in sq_in:
                if not sq in sqs:
                    err = "" if desc is None else desc+ " "
                    err += f"sq: {sq} is unexpectely MISSING"
                    self.assert_fail_report(err)

        if sq_out is not None:
            if isinstance(sq_out, str):
                sq_in = re.split(r'[,\s]\s*', sq_out)
            for sq in sq_out:
                if sq in sqs:
                    err = "" if desc is None else desc+" "
                    err += f"sq: {sq} unexpectely is PRESENT"
                    self.assert_fail_report(err)


    def add_piece_square(self, piece_square):
        """ Add piece square
        :piece_square: chess specifier <piece><square>
        """
        piece = piece_square[0]
        sq = piece_square[1:]
        self.board_setting[sq] = piece
        
    def clear_board(self):
        """ Empty board of pieces
        """
        self.board_setting = {}     # Board is dictionary of piece(e.g. K) by <square> e.g., e1
        self.half_move_clock = 0
        self.full_move_clock = 0
        self.poss_en_passant = None
        self.poss_en_passant_rm_sq = None   # avoiding piece sq
        self.can_castle_white_kingside = True
        self.can_castle_white_queenside = True
        self.can_castle_black_kingside = True
        self.can_castle_black_queenside = True

    def clear_sq(self, sq):
        """ Empty square
        :sq: square notation, e.g., e1
        """
        self.board_setting[sq] = None   # Leave for easy access
        
    def get_piece(self, sq=None, file=None, rank=None, remove=False):
        """ Get piece at sq, None if empty
        :sq: square notation e.g., a1 if present
            else
        :file: file letter or int:1-
        :rank: rank str or int: 1-
        :remove: True - remove piece from board
            default: leave piece in square
        :returns: piece at sq, None if empty 
        """
        if sq is not None:
            if sq in self.board_setting:
                return self.board_setting[sq]            
            return None
        elif file is None and rank is None:
            return None
        
        sq = self.file_rank_to_sq(file=file, rank=rank)
        if sq is None:
            return None
        
        if sq in self.board_setting:
            piece = self.board_setting[sq]
            if remove:
                self.remove_piece(sq)
            return piece 
                    
        return None

    def remove_piece(self, sq):
        """ Remove piece from square
        :sq: sq to remove OK if sq is empty
        """
        if sq in self.board_setting:
            del self.board_setting[sq]

    def get_adj_sq(self, sq, dir):
        """ Get adjacent square in direction (x,y) 
        :sq: our square e.g, a1
        :dir: direction (x_inc,y_inc) or (x_inc,y_inc,special)
        :returns: adjacent square, None if off board
        """
        file_no, rank_no = self.sq_to_file_rank(sq, to_int=True)
        if len(dir) == 2:
            dir = dir[0],dir[1],None
            
        file_inc, rank_inc, special = dir
        file_no += file_inc   
        rank_no += rank_inc
        if (file_no < 1 or file_no > self.nsqx
            or rank_no < 1 or rank_no > self.nsqy):
            return None
            
        adj_sq = self.file_rank_to_sq(file=file_no, rank=rank_no)
        return adj_sq
    
    def get_move_dir_sqs(self, piece,
                            orig_sq,
                            list_dirs, rep=None):
        """ Get squares to which we can move
        without leaving the board nor hitting a
        square of our own color
        :piece: our piece
        :orig_sq: our square
        :list_dirs: list of directions one move hop
        :rep: maximum number of repeats in each direction
        :returns: dictionary, by sq, of moveable squares
        """
        sqs_d = {}
        our_color = self.piece_color(piece)
        piece_type = self.piece_to_type(piece)
        if rep is None:
            rep = max(self.nsqx-1, self.nsqy-1)
            
        for dir in list_dirs:
            if len(dir) < 3:
                dir = dir[0],dir[1],"capture"
            special_dir = dir[2]
            sq = orig_sq
            repadj = rep
            if piece_type == 'p' and dir[0] == dir[1]:
                repadj = 1  # pawn diagonals == 1
                
            for i in range(repadj):
                sq = self.get_adj_sq(sq, dir)
                if sq is None:
                    break   # over board edge

                sq_piece = self.get_piece(sq)                    
                if sq_piece is None:
                    if special_dir != "capture":    # only save capture
                        sqs_d[sq] = sq_piece    # save empty square
                    continue
                
                # Square is occupied
                sq_piece_color = self.piece_color(sq_piece)
                if special_dir == "capture":
                    if sq_piece_color == our_color:
                        break   # End, Not a capture situation
                    else:
                        sqs_d[sq] = sq_piece
                        break       # End, capturing piece
                    
        return sqs_d

    def sq_to_file_rank(self, sq, to_int=False):
        """ split sq into file, rank pair
        :sq: square notation
        :to_int: True - return file,rank as ints 1-
        :returns: (file, rank) e.g. a1  or to_int 1,1
        """
        if to_int:
            file,rank = ord(sq[0])-ord('a')+1,ord(sq[1])-ord('1')+1
        else:
            file,rank = sq[0],sq[1]
        return file,rank
            
    def file_rank_to_sq(self, file=None, rank=None):
        """ Convert rank, file to sq notation
        :file: int 1-8 or str: a-h
        :rank: int 1-8 or str 1-8
        :returns: sq notation, None if off board
        """
        if isinstance(file,int):
            if file < 1 or file > self.nsqx:
                return None
            
            file = chr(ord('a')+file-1)
        if isinstance(rank, int):
            if rank < 1 or rank > self.nsqx:
                return None
            
            rank = chr(ord('1')+rank-1)
        return file+rank

    def get_move(self):
        """ Get board's latest move
        :returns: ChessMove, None if no move here
        """
        return self.cm

    def get_move_no(self):
        """ Get chess game move number using FEN
        full_move_clock
        started with white
        """
        return self.full_move_clock

    def get_opponent_pieces(self, to_move=None):
        """ Get all side to move pieces
        :to_move: black/white
            default: get from board
        :returns   list of piece_square settings
        """
        if to_move is None:
            to_move = self.get_to_move()
        opponent = "white" if to_move=="black" else "black"
        return self.get_side_pieces(to_move=opponent)

    def get_side_pieces(self, to_move=None):
        """ Get all side to move pieces
        :to_move: black/white
            default: get from board
        :returns   list of piece_square settings
        """
        if to_move is None:
            to_move = self.get_to_move()
        
        if to_move == "white":
            pieces = ("P","R","N","B","Q","K")
        else:
            pieces = ("p","r","n","b", "q","k")
        return self.get_pieces(pieces)    
                    
    def get_pieces(self, piece=None, piece_type=None):
        """ Get piece-square list for board setting
        :piece: list of pieces or piece - get only matching pieces
            OR
        :piece_type: get only matching piece types(case insensitive)
                e.g q - all both color queens
                "empty" - all empty squares
                "any" - any piece type
        :returns: list of piece_square settings
        """
        if isinstance(piece, (tuple,list)):
            pss = []
            for pc in piece:
                pss.extend(self.get_pieces(piece=pc))
            return pss
            
        if piece_type is not None:
            piece_type = piece_type.lower()
        piece_squares = []  # list <piece><rank><file>
        piece_by_squares = {}
        for sq in self.board_setting:
            pce = self.board_setting[sq]
            if pce is None:
                continue        # Ignore empty
            ptype = pce.lower()
            ps = None if piece is None else pce+sq
            if ((piece is not None and pce == piece)
                or (piece_type is not None and 
                    ptype == piece_type)
                or piece is None and piece_type is None):
                    piece_squares.append(pce+sq)
                    piece_by_squares[sq] = pce  # for inversion
        return piece_squares
    

    """
    game playing
    """

    def get_to_move(self, opponent=False):
        """ Whose move is it?
        :opponent: True - opponent
        """
        to_move = self.to_move
        if opponent:
            to_move = "black" if to_move == "white" else "white"
        return to_move

    def set_to_move(self, to_move=None):
        """ set who to move
        :to_move: "black" or "white"
            default: "white"
        """
        if to_move is None:
            to_move = "white"
        self.to_move = to_move    
    
    def update_move(self):
        """ Update whose to move
        """
        self.to_move = "black" if self.to_move == "white" else "white"

    def castle_from_to(self, king_side= True, to_move=None):
        """ give source, destination sq - worker function
        :king_side: True - king side castle, else queen side
        :to_move: white/black
                default: get current
        :returns: (king origin sq, destination sq), rook orig, dest)
                    no check if legal possible
        """
        if to_move is None:
            to_move = self.get_to_move()
        if king_side:
            if to_move == "white":
                king_sq = "e1"
                king_dest = "g1"
                rook_sq = "h1"
                rook_dest = "f1"
            else:
                king_sq = "e8"
                king_dest = "g8"
                rook_sq = "h8"
                rook_dest = "f8"
        else:
            if self.to_move == "white":
                king_sq = "e1"
                king_dest = "c1"
                rook_sq = "a1"
                rook_dest = "d1"
            else:
                king_sq = "e8"
                king_dest = "c8"
                rook_sq = "a8"
                rook_dest = "d8"
        return king_sq, king_dest, rook_sq, rook_dest
            

    def can_castle(self, king_side=True, to_move=None):
        """ Determine if we can castle
        :king_side: True if king side, else queen side
                default: kingside                
        :returns: True if the requested castling is permited
        """
        if to_move is None:
            to_move = self.get_to_move()
        king_sq, king_dest, rook_sq, rook_dest = self.castle_from_to(
                king_side=king_side, to_move=to_move)

        # Check that pieces are in place
        k_piece = "K" if to_move == "white" else "k"
        if self.get_piece(king_sq) != k_piece:
            return {}   # Some body else here
        
        r_piece = "R" if to_move == "white" else "r"
        if self.get_piece(rook_sq) != r_piece:
            return {}   # Rook not in place

        # neither king nor rook can have moved
        if self.is_moved(king_sq) or self.is_moved(rook_sq):
                return False
                
        # No intervening square can be occupied
        passing_sqs = self.get_intervening_sqs(king_sq, rook_sq,
                        include_first=False, include_last=False)
        for isq in passing_sqs:
            if self.get_piece(isq) is not None:
                return False    # Some intervening piece

        # King may not go from, through, or into check
        passing_sqs = self.get_intervening_sqs(king_sq, king_dest,
                        include_first=True, include_last=True)
        opp_piece_sqs = self.get_opponent_pieces(to_move=to_move)
        for pass_sq in passing_sqs:
            for opp_piece_sq in opp_piece_sqs:
                opp_piece,opp_sq = self.ps_to_p_sq(opp_piece_sq)
                opp_sqs = self.get_move_to_sqs(opp_piece, opp_sq)
                if pass_sq in opp_sqs:
                    return False    # attacked passing square
        return True

    def get_intervening_sqs(self, first_sq, last_sq,
                            include_first=False,
                            include_last=False):
        """ Get squares between first and last
        in same rank (maybe some day other paths)
        :first_sq: beginning square
        :last_sq: last square
        :include_first: True - include first square, else omit
                    default: False - omit
        :include_last: True - include last square, else omit
        :returns: dictionary, by sq, of contained pieces, None == empty
        """
        f_file_no, f_rank_no = self.sq_to_file_rank(
            first_sq, to_int=True)
        l_file_no, l_rank_no = self.sq_to_file_rank(
            last_sq, to_int=True)
        assert f_rank_no == l_rank_no, "get_intervening_sqs separate ranks"
        file_change = l_file_no - f_file_no
        file_dir = int(file_change/abs(file_change))
        incl_sqs = {}
        file_no = f_file_no
        rank_no = f_rank_no
        while True:
            sq = self.file_rank_to_sq(file=file_no, rank=rank_no)
            incl_sqs[sq] = sq
            if sq == last_sq:
                break
            file_no += file_dir
            
        if not include_first:
            del incl_sqs[first_sq]
        if not include_last:
            del incl_sqs[last_sq]
        return incl_sqs

    def get_attacking_pieces(self, ps, to_move=None):
        """ Get dictionary of piece-squares
        which can attack/capture given sq
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
        
        
        att_pcs = self.att_pieces_black if to_move == "white" else self.att_pieces_white
        att_piece_sqs = self.get_pieces(att_pcs)   
        attacking_sqs = {}
        for att_psq in att_piece_sqs:
            att_piece, att_sq = self.ps_to_p_sq(att_psq)
            att_move_to_sqs = self.get_move_to_sqs(att_piece,
                                                   orig_sq=att_sq)
            if target_sq in att_move_to_sqs:
                attacking_sqs[att_sq] = att_piece
        return attacking_sqs

    def is_in_check(self, piece=None):
        """ Check if king is in check
        :piece: piece in question
                default: our King
        :returns: True if piece is in check
        """
        if piece is None:
            to_move = self.get_to_move()
            piece = "K" if to_move == "white" else "k"
        ps_sq = self.get_pieces(piece=piece)
        if len(ps_sq) == 0:
            return False    # No king to check
        
        psq = ps_sq[0]
        attacking_pieces = self.get_attacking_pieces(psq)
        if len(attacking_pieces) > 0:
            return True
        
        return False            
 

    def piece_color(self, piece):
        """ Get piece's color
        :piece: piece uppercase for white
        """
        return "white" if piece.isupper() else "black"

    def piece_type_to_piece(self, type, to_move=None):
        """ Get piece's color
        :piece_type_to_piece: piece uppercase for white
        :to_move: black/white
            default: from board
        :returns: piece    # uppercase if white lowercase if black
        """
        if to_move is None:
            to_move = self.get_to_move()
        if type is None:
            SlTrace.lg(f"type is None")
        piece = type.lower() if to_move == "black" else type.upper()
        return piece

    def piece_to_type(self, piece):
        """ Get piece's type (lowercase of piece)
        :piece: piece uppercase for white
        :returns: piece type (lowercase)
        """
        return piece.lower()
    
    def ps_to_sq(self, ps):
        """ Get square from piece_square
        :ps: piece-square spec
        :returns: square
        """
        return ps[1:]       # so far just one character pieces
        
    def ps_to_p_sq(self, ps):
        """ Get piece,sq from piece-square
        :ps: piece-square spec
        :returns: piece,square
        """
        return ps[0],ps[1:]       # so far just one character pieces
    
        
    def place_piece(self, piece, sq=None):
        """ Place piece in square, first deleting destination contents
        :piece: piece, e.g. p black pawn, P white pawn
        :sq: destination square, e.g. e1
        :returns: previous contents of destination sq, None if empty
        """
        if not self.just_notation:
            assert(sq is not None)
        prev_piece = self.get_piece(sq)
        self.board_setting[sq] = piece
        return prev_piece

        
    def assert_pieces(self, piece_sqs):
        """ Verify piece(s) is(are) present
        :piece_sqs: piece-square  or comma,space separated string, or list/tuple
        """
        if isinstance(piece_sqs, str):
            piece_sqs = re.split(r'[;,\s]+', piece_sqs)
        SlTrace.lg(f"piece_sqs: {piece_sqs}", "test_strings")
        look_sqs = {}
        for piece_sq in piece_sqs:
            if piece_sq == '':
                continue
            
            piece,sq = self.ps_to_p_sq(piece_sq)
            look_sqs[sq] = piece
            piece_found = self.get_piece(sq)
            if piece_found != piece:
                self.assert_fail_report(f"At {piece_sq} {piece_found = } not the Expected: {piece}")
        # Check squares not mentioned are empty
        for sq in self.all_sqs():
            if sq not in look_sqs:
                other_piece = self.get_piece(sq)
                if other_piece is not None:
                    self.assert_fail_report(f"UNEXPECTED piece {other_piece} at {sq}")
        
    def place_pieces(self, piece_sqs):
        """ Place piece in square, first deleting destination contents
        :piece_sqs: piece-square  or comma,space separated string, or list/tuple
        """
        if isinstance(piece_sqs, str):
            piece_sqs = re.split(r'[;,\s]+', piece_sqs)
        for piece_sq in piece_sqs:
            if piece_sq == '':
                continue
            
            piece,sq = self.ps_to_p_sq(piece_sq)
            self.place_piece(piece, sq)
    
    def board_to_fen_str(self):
        """ Generate FEN notation string from current board state
        :returns: string of FEN notation
        """
        fen_str = ""
        cf = ChessFEN()
        cf.import_from_bd(self)
        fen_str += cf.to_fen_str()
        return fen_str
    
    def print_board_to_fen(self):
        """ Print current board state as a FEN string
        """
        fen_str = self.board_to_fen_str()
        SlTrace.lg(fen_str)
        
        
    def make_move(self,
                  just_notation=False,
                  orig_sq=None,
                  prev_orig_sq_moved=None,
                  dest_sq=None,
                  dest_sq_mod=None,
                  spec=None,
                  has_movement=None,
                  game_result=None,
                  update=True,
                  orig2_sq=None,
                  prev_orig2_sq_moved=None,
                  dest2_sq=None,
                  dest2_sq_mod=None,
                  promoted_piece=None):
        """ Make move after decode
        Update to_move iff successful
        sets/records if orig_sq,orig2 pieces have previouly been moved
        :just_notation: just for notation - no checks
                default: False
        :orig_sq: origin square for move
        :prev_orig_sq_moved: True if orig_sq moved previously
                default: get state before move
        :dest_sq: destination square for move
        :spec: move specification
        :has_movement:  True - move does something
                default: True
        :game_result: game rusult = game over
                default: No game result
        :dest_sq_mod: alternate piece for destination e.g. promotion 
        :update: change board default: True - change
        :orig2_sq: optional second origin sq e.g. for castle
        :prev_orig2_sq_moved: True if orig_sq moved previously
                default: get state before move
        :dest2_sq: optional second destination sq
        :dest2_sq_mod: optional alternate piece for dest
        :returns: None if successful, else err msg
        """
        # Game result stops action
        if game_result is not None:
            return None
        
        self.just_notation = just_notation      # To notify sub callers
        if orig_sq is None and not just_notation:
            err = f"make_move: spec:{spec} orig_sq:{orig_sq}"
            SlTrace.lg(err)
            return err
        

        if dest_sq is None and not just_notation:
            err = f"make_move: spec{spec} dest_sq:{dest_sq}"
            SlTrace.lg(err)
            return err
        
        if update:
            if orig_sq is not None:
                prev_orig_sq_moved = self.set_as_moved(orig_sq)
            if orig2_sq is not None:
                prev_orig2_sq_moved = self.set_as_moved(orig2_sq)
            orig_piece = self.get_piece(sq=orig_sq)
            if orig_piece is None:
                return self.err_add(f"make_move: orig_sq({orig_sq} is empty)")
            
            orig_piece_type = self.piece_to_type(orig_piece)
            dest_piece = self.get_piece(sq=dest_sq)
            
            if orig_piece == "K":
                self.can_castle_white_kingside = False
                self.can_castle_white_queenside = False
            elif orig_piece == "R":
                if orig_sq == "h1":
                    self.can_castle_white_kingside = False
                elif orig_sq == "a1":
                    self.can_castle_white_queenside = False
            elif orig_piece == "k":
                self.can_castle_black_kingside = False
                self.can_castle_black_queenside = False
            elif orig_piece == "r":
                if orig_sq == "h8":
                    self.can_castle_black_kingside = False
                elif orig_sq == "a8":
                    self.can_castle_black_queenside = False
            elif dest_sq == "h1":
                self.can_castle_white_kingside = False  # rook captured
            elif dest_sq == "a1":
                self.can_castle_white_queenside = False
            elif dest_sq == "h8":
                self.can_castle_black_kingside = False
            elif dest_sq == "a8":
                self.can_castle_black_queenside = False
            
            if (self.poss_en_passant is not None
                    and orig_piece_type == 'p'
                    and dest_sq == self.poss_en_passant):
                self.remove_piece(self.poss_en_passant_rm_sq)        
            self.poss_en_passant = None         # Forgotten
            if orig_piece_type == 'p' or dest_piece is not None:    # pawn move or capture
                self.half_move_clock = 0
            if orig_piece_type == 'p':
                o_file,o_rank = self.sq_to_file_rank(orig_sq, to_int=True)
                d_file,d_rank = self.sq_to_file_rank(dest_sq, to_int=True)
                if o_rank == 2 and d_rank == 4:     # white 2 sq move
                    self.poss_en_passant = self.file_rank_to_sq(file=o_file, rank=o_rank+1)
                elif o_rank == 7 and d_rank == 5:   # black 2 sq move
                    self.poss_en_passant = self.file_rank_to_sq(file=o_file, rank=o_rank-1)
                self.poss_en_passant_rm_sq = dest_sq    # en passant capture will remove this
                        
            else:
                self.half_move_clock += 1
            if self.to_move == "black":
                self.full_move_clock += 1
                
            self.remove_piece(sq=orig_sq)
            dest_update = orig_piece if dest_sq_mod is None else dest_sq_mod
            self.place_piece(dest_update, dest_sq)
            self.has_movement=has_movement
            self.game_result = game_result
            # Optional second pair for such things as castling
            if orig2_sq is not None:
                orig2_piece = self.get_piece(sq=orig2_sq)
                self.remove_piece(sq=orig2_sq)
                if dest2_sq is not None:
                    dest2_update = orig2_piece if dest2_sq_mod is None else dest_sq_mod
                    self.place_piece(dest2_update, dest2_sq)
            
            
            if game_result is None:
                self.update_move()
            if orig_sq is not None:
                self.remove_piece(orig_sq)


    def csu_to_move(self, mv_csu):
        """ Convert save unit (ChessSaveUnit) to move (ChessMove)
        :mv_csu: Move save unit
        :returns: sutable move (ChessMove)
        """
        cm = ChessMove(self)
        cm.board = mv_csu.board
        cm.spec = mv_csu.spec
        cm.orig_piece = mv_csu.orig_piece
        cm.prev_orig_sq_moved = mv_csu.prev_orig_sq_moved
        cm.orig_sq = mv_csu.orig_sq
        cm.dest_piece = mv_csu.dest_piece
        cm.dest_sq = mv_csu.dest_sq
        
        cm.orig2_piece = mv_csu.orig2_piece
        cm.orig2_sq = mv_csu.orig2_sq
        cm.prev_orig2_sq_moved = mv_csu.prev_orig2_sq_moved
        cm.dest2_piece = mv_csu.dest2_piece
        cm.dest2_sq = mv_csu.dest2_sq
        return cm

    def get_move_undo(self):
        """ Get move undo stack entry, if one
        No change to state
        :returns: undo cm, if one
                else None
        """
        if len(self.move_undo_stack) == 0:
            return None

        mv_csu = self.move_undo_stack[-1]
        return self.csu_to_move(mv_csu)
        
                
    def move_redo(self):
        """ Undo previous undo:
        1. Leaving board state as it was before that undo
        2. Removing ChessStateUnit from undo_stack
        :returns: previous move if successful else None
        """
        if len(self.move_redo_stack) == 0:
            return None
        
        mv_csu = self.move_redo_stack.pop()
        
        
    def move_undo(self):
        """ Undo previous move:
        1. Leaving board state as it was before that move
        2. Adding ChessStateUnit in move_redo_stack to support redo
        :returns: previous move if successful else None
        """
        if len(self.move_stack) == 0:
            return None
        
        mv_csu = self.move_stack.pop()
        self.move_redo_stack.append(mv_csu)
        mv_csu.restore()
        move = self.csu_to_move(mv_csu)
        return move
    
    def piece_to_move(self, piece):
        """ get to_move from piece
        capital pieces are white
        :piece: piece e.g. K white king, k black king
        :returns: black/white for whos move
        """
        return "white" if piece.isupper() else "black"
   
                
    def to_piece_sq(self, piece=None, sq=None):
        """Produce piece_square even if piece is None
        :piece: piece or None if empty
        :sq: square
        """
        p = "" if piece is None else piece
        return p + sq

    def get_prev_move(self, back=-1):
        """ Get previous move, with no change,
            assuming we have not  saved the current
            move.  After save_move, previous move(back==-1)
            would be the current move, and -2 would get
            the previouse move
        Used to check for thigs suchas E.P
        :back: look back
            default: -1  # -2 is one before last
        :returns: previous move (ChessSaveUnit)
            None if no previous move saved
        
        """
        if len(self.move_stack) < -back:
            return None
        
        return self.move_stack[back]
            
    def save_move(self,
                orig_sq=None,
                orig_piece=None,
                prev_orig_sq_moved=None,
                dest_sq=None,
                dest_piece=None,
                spec=None,
                orig2_sq=None,
                orig2_piece=None,
                prev_orig2_sq_moved=None,
                dest2_sq=None,
                dest2_piece=None,
                dest2_sq_mod=None,
                half_move_clock=None,
                full_move_clock=None,
                poss_en_passant=None):

        """ Save move info, to enable undo
        :orig_sq: original square location
        :orig_piece: orig_sq occupant
                default: get from sq
        :dest_sq: destination square location
        :dest_piece: dest_sq occupant
                default: get from sq
        :dest_sq_mod: optional modified destination piece NOT USED
        :spec: specification
        :orig2_sq: optional original square
        :orig2_piece: optional original square occupant
            default: get from square
        :dest2_sq: optional second destination square
        :dest2_piece: optional square occupant
            default: get from square
        :dest2_sq_mod: optional modified destination piece NOT USED
        """
        
        if orig_piece is None:
            orig_piece = self.get_piece(orig_sq)
        if dest_piece is None:
            dest_piece = self.get_piece(dest_sq)

        if orig2_sq is not None:
            if orig2_piece is None:
                orig2_piece = self.get_piece(orig2_sq)
        if dest2_sq is not None:
            if dest2_piece is None:
                dest2_piece = self.get_piece(dest2_sq)

        save_unit = ChessSaveUnit(self,
                        spec=spec,
                        orig_sq=orig_sq,
                        orig_piece=orig_piece,
                        dest_sq=dest_sq,
                        dest_piece=dest_piece,
                        prev_orig_sq_moved=prev_orig_sq_moved,
                        prev_orig2_sq_moved=prev_orig2_sq_moved,
                        orig2_sq=orig2_sq,
                        orig2_piece=orig2_piece,
                        dest2_sq=dest2_sq,
                        dest2_piece=dest2_piece,
                        half_move_clock=half_move_clock,
                        full_move_clock=full_move_clock,
                        poss_en_passant=poss_en_passant)


    """
    Links to ChessPieceMovement via cpm
    """


    def is_at_origin(self, piece, sq):
        """ Check if pawn at origin sq
        :piece: piece
        :sq: occupying square
        :returns True if pawn at origin
        """
        return self.cpm.is_at_origin(piece=piece, sq=sq)

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
        return self.cpm.get_move_to_sqs(piece, orig_sq=orig_sq)            


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
        if self.can_castle(king_side=True):
            kside = self.castle_from_to(to_move=to_move)
            king_sq, king_dest, rook_sq, rook_dest = kside
            move_to_sqs[king_dest] = None
        if self.can_castle(king_side=False):
            qside = self.castle_from_to(king_side=False, to_move=to_move)
            king_sq, king_dest, rook_sq, rook_dest = qside
            move_to_sqs[king_dest] = None
        return move_to_sqs

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
        piece_type = piece.lower()
        if piece_type not in ChessPieceMovement.piece_type_dir_d:
            self.err = f"get_move_to_sqs {piece}"
            return None
        
        if piece == 'p':
            dir_type = 'p-black'    # reverse y direction
        else:
            dir_type = piece_type
        dirs = ChessPieceMovement.piece_type_dir_d[dir_type]
        if piece_type == 'p':
            if self.is_at_origin(piece, orig_sq):
                rep = 2
            else:
                rep = 1
        elif piece_type in ['k', 'n']:
            rep = 1
        else:
            rep = None  # Use default - max
        return self.get_move_dir_sqs(piece, orig_sq=orig_sq,
                                     list_dirs=dirs,
                                     rep=rep)

        
if __name__ == "__main__":
    from chessboard_print import ChessboardPrint
    
    SlTrace.clearFlags()
    #cb = Chessboard(pieces=':Kc1Qe1kh7 w')
    cb = Chessboard(pieces='STANDARD:')
    cbd = ChessboardPrint(cb)
    cbd.display_board()

    cb = Chessboard(pieces=':Kc1Qe1kh7 w')
    cbd = ChessboardPrint(cb)
    cbd.display_board()
    