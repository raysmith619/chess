#chessboard.py 10Feb2025  crs
import re

"""
Experimentation of manipulation of a chess board
Goals:
    efficient display
    efficient access
"""
from select_trace import SlTrace

from chess_piece_images import ChessPieceImages
from chess_move import ChessMove


class ChessSaveUnit:
    """ Save info to support restoring previous current
    board status
    """
    
    def __init__(self,
        board,
        orig_ps=None,
        dest_ps=None,
        spec=None,
        to_move=None,
        orig_ps_2=None,
        dest_ps_2=None):
        if to_move is None:
            to_move = board.to_move
        self.orig_ps = orig_ps
        self.dest_ps = dest_ps
        self.spec = spec
        self.orig_ps_2 = orig_ps_2
        self.dest_ps_2 = dest_ps_2


class Chessboard:
    """
    Piece type movement directions
    Number of repititions depends on piece
    and in the case of pawns, the conditions 1'st move, after
    (x,y)
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
        #   PAIR X,Y, TRIPLE x,y,"capture" - only if capture
        # pawn:
        #       rep: first move 1, else 2
        "p" : [(0,1),
               (-1,1, "capture"), (1,1,"capture")],
        # black pawn MUST equal "p" with y entries negated
        "p-black" : [(0,-1),
            (-1,-1, "capture"), (1,-1,"capture")],
        
        "n" : [(1,2), (2,1), (2,-1), (1,-2),
               (-1,-2), (-2,-1), (-2,1), (-1,2)],
        "b" : [(1,1), (1,-1), (-1,-1), (-1,1)],
        "r" : [(0,1), (1,0), (0,-1), (-1,0)],
    }
    piece_type_dir_d["q"] =  piece_type_dir_d["b"] + piece_type_dir_d["b"]
    piece_type_dir_d["k"] = piece_type_dir_d["q"] # only one sq

    
    def __init__(self,
                 pieces = None,
                 base_board = None,
                 nsqx = 8,
                 nsqy = 8,
                 to_move = "white"
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
                    
        :base_board: Chess board on which this is based
                default: None - no base
        :nsqx: Number of squares horizontal
                default: 8
        :nsqy: Number of squares vertical
                default: 8
        """
        self.pieces = pieces
        self.piece_squares = []    # Initial list of pieces, if any
        
        self.base_board = base_board
        self.nsqx = nsqx
        self.nsqy = nsqy
        self.to_move = to_move
        self.setup_board()
        self.move_stack = []    # Stack of ChessSaveUnit
        self.update_to_move = True # Default - update after make_move
        self.moved_pieces_d = {}  #dictionary, by initial square
                                  #  of pieces who have moved
        self.clear_assert_test_count()
        self.clear_assert_fail()
        self.set_assert_fail_max(10)
                                  
    def setup_board(self):
        """ Set board internals
        especially board for efficient access to board contents
        """        
        piece_string = self.pieces
        self.clear_board()               
        if piece_string is None or piece_string == "":
            return      # No pieces
        
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
            self.fen_setup(piece_string[4:])
        elif piece_string.upper().startswith("STANDARD:"):
            self.standard_setup()
        else:    
            raise Exception("We don't yet handle anything other than short form")

        
        if len(self.piece_squares) > 0:
            self.add_pieces(self.piece_squares)      # Populate board

    def standard_setup(self):
        """ Setup standard initial setup
        """
        self.clear_board()
        self.piece_squares = []
        self.fen_setup('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        self.add_pieces(self.piece_squares)      # Populate board
                                
    def fen_setup(self, fen_str):
        """ Setup board piece_squares from FEN string
        setup self.piece_squares list of <piece><location> strings
        Initially just first field
        :fen_str:  FEN notation string
        """
        self.piece_squares = []
        fs = fen_str
        rank_n = self.nsqy
        while rank_n > 0 and len(fs) > 0:
            match_row = re.match(r'([^/]+)([/\s]|$)', fs)
            if match_row:
                row_str = match_row.group(1)
                self.fen_setup_row(rank_n, row_str, self.piece_squares)
                match_str = match_row.group()
                fs = fs[len(match_str):]    
            rank_n -= 1      # from top to bottom

    def fen_setup_row(self, rank_n, row_str, piece_squares):
        """ Setup from fen row
        :board_rank_n: rank 1...self.nsqy
        :row_str: row str e.g. 3qkbnr
        :piece_squares: list to which add piece_square e.g., ra8
        :returns: number piece_square added
        """
        board_file_strs = "abcdefgh"
        board_rank_strs = "12345678"
        board_file_no = 1
        n_placed = 0
        for ch in row_str:
            if pmatch := re.match(r'[rnbqkpRNBQKP]', ch):
                piece_pl = (pmatch.group() + board_file_strs[board_file_no-1]
                            + board_rank_strs[rank_n-1])
                piece_squares.append(piece_pl)
                board_file_no += 1
                n_placed += 1
            elif pmatch := re.match(r'[1-8]', ch):
                board_file_no += int(pmatch.group())    # Skip squares
            else:
                err = f"FEN row character:{ch} not recognized in row_str:{row_str}"
                SlTrace.lg(err)
                raise Exception(err)
        return n_placed

    """ 
    Internal board access
    Probably to be  made more efficient in the future
    """
    def is_moved(self, sq):
        """ Tell if piece, originating at this square
        has ever been moved
        :sq: origin square
        """
        if sq in self.moved_pieces_d:
            return True
        
        return False
    
    def set_as_moved(self, sq):
        """ Set piece, originating at this sq
        as moved.  Note if another piece is moved from this
        square the original piece has to have moved
        """
        self.moded_pieces_d = sq

    def clear_assert_test_count(self):
        """ Clear assert fail count
        """
        self.assert_test_count = 0

    def start_assert_test(self, desc=None):
        """ start test
        """
        self.assert_test_count += 1


    def clear_assert_fail(self):
        """ Clear assert fail count
        """
        self.assert_fail_count = 0
        
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
        if self.assert_fail_count >= self.assert_fail_count_max:
            raise Exception(f"Assert fail maximum"
                            f"({self.assert_fail_count_max}) reached"
                            f" quitting")        

    def add_pieces(self, piece_squares, clear_first=True):
        """ add to current setting
        :piece_squares: new piece_square setting to add
        :clear_first: clear board board before adding
                default: clear board first
        """
        if clear_first:
            self.clear_board()
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
        self.start_assert_test()
        if sq_only is not None:
            SlTrace.lg(f"sq_only: {sq_only}", "test_strings")
            SlTrace.lg(f"     in: {sqs}", "found_sqs")
            if isinstance(sq_only, str):
                sq_only = re.split(r'[,\s]\s*', sq_only)
            sqs_in = {}
            for sq in sq_only:
                sqs_in[sq] = 'x'
            sqs_all = self.all_sqs()
            sqs_out = {}
            for sq in sqs_all:
                if sq not in sqs_in:    # create set complement
                    sqs_out[sq] = 'z'
            sq_in = sq_only
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
        self.board_setting[piece_square[1:]] = piece_square[0]
        
    def clear_board(self):
        """ Empty board of pieces
        """
        self.board_setting = {}     # Board is dictionary of piece(e.g. K) by <square> e.g., e1

    def clear_sq(self, sq):
        """ Empty square
        :sq: square notation, e.g., e1
        """
        self.board_setting[sq] = None   # Leave for easy access
        
    def get_piece(self, sq=None, file=None, rank=None):
        """ Get piece at sq, None if empty
        :sq: square notatin e.g., a1 if present
            else
        :file: file letter or int:1-
        :rank: rank str or int: 1- 
        """
        if sq is not None:
            if sq in self.board_setting:
                return self.board_setting[sq]            
            return None
        
        if isinstance(file, int):
            file = chr(ord('a')+file-1)
        if isinstance(rank, int):
            rank = chr(ord('1')+rank)   # limited 10= ";"
        sq = file+rank
        if sq in self.board_setting:
            return self.board_setting[sq]
                    
        return None
    
        return self.board_setting[file+rank]

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
        if piece_type not in Chessboard.piece_type_dir_d:
            self.err = f"get_move_to_sqs {piece}"
            return None
        
        if piece == 'p':
            dir_type = 'p-black'    # reverse y direction
        else:
            dir_type = piece_type
        dirs = Chessboard.piece_type_dir_d[dir_type]
        if piece_type == 'p':
            if not self.is_moved(orig_sq):
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
        if rep is None:
            rep = max(self.nsqx-1, self.nsqy-1)
            
        for dir in list_dirs:
            if len(dir) < 3:
                dir = dir[0],dir[1],None
            special_dir = dir[2]
            sq = orig_sq
            for i in range(rep):
                sq = self.get_adj_sq(sq, dir)
                if sq is None:
                    break   # over board edge

                sq_piece = self.get_piece(sq)                    
                if sq_piece is None:
                    if special_dir != "capture":    # only save capture
                        sqs_d[sq] = sq_piece    # save empty square
                    continue
                
                sq_piece_color = self.piece_color(sq_piece)
                if special_dir == "capture":
                    if sq_piece_color == our_color:
                        break   # Not a capture situation
                
                if sq_piece_color == our_color:
                    break       # bumping into our piece
            
                sqs_d[sq] = sq_piece
                break           # Stop after getting oponent
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
        :returns: sq notation
        """
        if isinstance(file,int):
            file = chr(ord('a')+file-1)
        if isinstance(rank, int):
            rank = chr(ord('1')+rank-1)
        return file+rank
    
    def get_pieces(self, piece=None, piece_type=None):
        """ Get piece-square list for board setting
        :piece: get only matching pieces
            OR
        :piece_type get only matching piece types(case insensitive)
                e.g q - all both color queens
                "empty" - all empty squares
                "any" - any piece type
        :returns: list of piece_square settings
        """
        if piece_type is not None:
            piece_type = piece_type.lower()
        piece_squares = []  # list <piece><rank><file>
        piece_by_squares = {}
        for sq in self.board_setting:
            pce = self.board_setting[sq]
            ptype = pce.lower()
            ps = None if piece is None else pce+sq
            if ((piece is not None and pce == piece)
                or (piece_type is not None and 
                    ptype == piece_type)
                or True):
                    piece_squares.append(pce+sq)
                    piece_by_squares[sq] = pce  # for inversion
        return piece_squares
    
        '''
        if piece_type == "EMPTY":
            pie_sqs = []
            for f_no in range(1, self.nsqx+1):
                for r_no in range(1, self.nsqy+1):
                    sq = self.file_rank_to_sq(file=f_no,
                                              rank=r_no)
                    if sq not in piece_by_squares:
                        pie_sqs.append(sq)
            return pie_sqs
            
        return piece_squares
        '''
        
    def make_move(self, move_spec, to_move=None):
        """ Make a chess move
        :move_spec: make move
                1. chess notation
                    in chess notation e.g. e4, e5, Nf3, Nc3, Ncf3, Qh4e1
        :to_move: side making move
                default: board.to_move
                        first: white
        :returns: None if successful, err_msg if not 
        """
        mv = ChessMove(self, move_spec)

    """
    game playing
    """
    def update_move(self):
        """ Update whose to move
        """
        self.to_move = "black" if self.to_move == "white" else "white"
    
    def make_castle(self, king_side=True):
        """ Do castle move
        :king_sq: king's square e.g. e1
        :rook_sq: rook's square e.g. h1 king's side, a1 queen's side
        :king_side: king/queen side default: King side
        :returns: None if OK, errmsg if problem
        """
        if err := self.can_castle(king_side):
            return err
        
        if king_side:
            if self.to_move == "white":
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
                king_dest = "g8"
                rook_sq = "h8"
                rook_dest = "f8"
        self.make_move(orig_sq=king_sq, dest_sq=king_dest,
                        move_update=False)
        self.make_move(orig_sq=rook_sq, dest_sq=rook_dest,
                        move_update=False)

    def piece_color(self, piece):
        """ Get piece's color
        :piece: piece uppercase for white
        """
        return "white" if piece.isupper() else "black"
        
        
    def place_piece(self, piece, sq=None):
        """ Place piece in square, first deleting destination contents
        :piece: piece, e.g. p black pawn, P white pawn
        :sq: destination square, e.g. e1
        :returns: previous contents of destination sq, None if empty
        """
        assert(sq is not None)
        prev_piece = self.get_piece(sq)
        self.board_setting[sq] = piece
        return prev_piece
    
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
        if update_to_move is None:
            update_to_move = self.update_to_move
        if orig_sq is None:
            err = f"make_move: spec:{spec} orig_sq:{orig_sq}"
            SlTrace.lg(err)
            return err
        
        if dest_sq is None:
            err = f"make_move: spec{spec} dest_sq:{dest_sq}"
            SlTrace.lg(err)
            return err
        
        self.save_move(orig_sq=orig_sq, dest_sq=dest_sq,
                  spec=spec)
        orig_piece = self.get_piece(sq=orig_sq, remove=True)
        dest_piece = self.get_piece(sq=dest_sq, remove=True)
        dest_update = dest_piece if dest_sq_mod is None else dest_sq_mod
        self.place_piece(dest_update, dest_sq)
        if update_to_move:
            self.update_move()
        
    def to_piece_sq(self, piece=None, sq=None):
        """Produce piece_square even if piece is None
        :piece: piece or None if empty
        :sq: square
        """
        p = "" if piece is None else piece
        return p + sq

    def get_prev_move(self):
        """ Get previous move, with no change
        Used to check for thigs suchas E.P
        :returns: previous move (ChessSaveUnit)
            None if no previous move saved
        """
        if len(self.move_stack) == 0:
            return None
        
        return self.move_stack[-1]
            
    def save_move(self, orig_sq=None, dest_sq=None,
                  spec=None, orig_sq_2=None, dest_sq_2=None):
        """ Save move info, to enable undo
        :orig_sq: original square location
        :dest_sq: destination square location
        :spec: specification
        :orig_sq_2: optional original square
        :dest_sq_2: optional second destination square
        """
        orig_piece = self.get_piece(orig_sq)
        orig_ps = self.to_piece_sq(orig_piece, orig_sq)
        dest_piece = self.get_piece(dest_sq)
        dest_ps = self.to_piece_sq(orig_piece, orig_sq)
        
        if orig_sq_2 is not None:
            orig_piece_2 = self.get_piece(orig_sq_2)
            orig_ps_2 = self.to_piece_sq(orig_piece_2, orig_sq_2)
        else:
            orig_ps_2 = None
        
        if dest_sq_2 is not None:
            dest_piece_2 = self.get_piece(dest_sq_2)
            dest_ps_2 = self.to_piece_sq(dest_piece_2, dest_sq_2)
        else:
            dest_ps_2 = None

        save_unit = ChessSaveUnit(self,
                        orig_ps=orig_ps,
                        dest_ps=dest_ps, spec=spec,
                        to_move=self.to_move,
                        orig_ps_2 = orig_ps_2,
                        dest_ps_2 = dest_ps_2)        
        self.move_stack.append(save_unit)
        
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
    