#chess_piece_movement.py
""" 
Handles peice movement rules
Determines available destination squares
based on piece, square, board conditions
"""
import re

from select_trace import SlTrace

class ChessPieceMovement:

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
        #   PAIR: (X,Y), TRIPLE: (x,y,"capture"/"move")
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
        piece_type = self.piece_to_type(piece)
        if piece_type not in ChessPieceMovement.piece_type_dir_d:
            self.err = f"get_move_to_sqs {piece}"
            return None
        
        if piece == 'p':
            dir_type = 'p-black'    # reverse y direction
        else:
            dir_type = piece_type
        dirs = ChessPieceMovement.piece_type_dir_d[dir_type]
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
        if (file_no < 1 or file_no > self.get_nsqx()
            or rank_no < 1 or rank_no > self.get_nsqy()):
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
        piece_type = self.piece_to_type(piece)
        our_color = self.piece_color(piece)
        if rep is None:
            rep = max(self.get_nsqx()-1, self.get_nsqy()-1)
            
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
                if sq_piece is not None:    # stopping at first piece
                    sq_piece_color = self.piece_color(sq_piece)
                    if (special_dir != "move"
                            and sq_piece_color != our_color):
                        sqs_d[sq] = sq_piece
                    break
                
                # Check on empty square    
                if special_dir != "capture":
                    sqs_d[sq] = sq_piece    # save empty square


        return sqs_d
    
    """ 
    Links to board
    """    
            
    def file_rank_to_sq(self, file=None, rank=None):
        """ Convert rank, file to sq notation
        :file: int 1-8 or str: a-h
        :rank: int 1-8 or str 1-8
        :returns: sq notation
        """
        return self.board.file_rank_to_sq(file=file, rank=rank)

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

    def get_assert_test_count(self):
        """ Get test count
        """
        return self.board.get_assert_test_count()

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
        return self.board.get_pieces(piece=piece, piece_type=piece_type)

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

    """ end of board links """
        