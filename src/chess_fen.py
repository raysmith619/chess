#chess_fen.py    21Mar2025  crs,     Author
""" FEN (Forsyth-Edwards Notation strings parsing and generating
"""
import re

""" For folks who don't have/want the full logging support
"""
class SlTrace:
    @classmethod
    def lg(cls, msg="", NOT_USED=None):
        print(msg)
    

class ChessFEN:
    """ FEN (Forsyth-Edwards Notation strings parsing and generating
    """
    # FEN attributes shared between ChessFen and Chessboard
    attrs = [
        'board_setting',
        'to_move',
        'can_castle_white_kingside',
        'can_castle_white_queenside',
        'can_castle_black_kingside',
        'can_castle_black_queenside',
        'poss_en_passant',
        'half_move_clock',
        'full_move_clock',
    ]


 
    def __init__(self, fen_str=None, nsqx=8, nsqy=8):
        """ Setup
        :fen: FEN string, if one
                default: no parsing
        :nsqx: number of rows facilitationg non-standard
            default:8
        :nsqy: number of columns (files) facilitationg non-standard
            default:8
        """
        self.fen_str = fen_str
        self.nsqx = nsqx
        self.nsqy = nsqy
        self.clear()
        
        if fen_str is not None:
            if (err:=self.parse(fen_str)):
                raise Exception(f"FEN String parsing error: {err}")

    def clear(self):
        """ Initialize state with empty board and initial values 
        """
        self.err = None
        self.board_setting = {} # dictionary, by sq(e.g. a1), of pieces on board
        self.to_move = "white"
        self.can_castle_white_kingside = True
        self.can_castle_white_queenside = True
        self.can_castle_black_kingside = True
        self.can_castle_black_queenside = True
        self.poss_en_passant = None
        self.half_move_clock = 0
        self.full_move_clock = 0

    def parse(self, fen_str):
        """Parse FEN string, populating fen attributes
        :fen_str: FEN string with or without "FEN: " prefix
            e.g. rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0
        :returns: error string, None if OK
        """
        self.fen_str = fen_str
        self.clear()
        fs = fen_str
        if (match_fen:=re.match(r'FEN:\s*(.*)$', fs)):
            fs = match_fen.group(1)     # Remove FEN:\s*
        rank_n = self.nsqy
        while rank_n > 0 and len(fs) > 0:
            match_row = re.match(r'([^/\s]+)/?', fs)
            if match_row:
                row_str = match_row.group(1)
                self.err = self.fen_setup_row(
                            rank_n, row_str)
                if self.err:
                    return self.err
                
                match_str = match_row.group()
                fs = fs[len(match_str):]
            else:
                self.err = f"FEN error, bad row at {fs} in {fen_str}"
                return self.err
                
            rank_n -= 1      # from top to bottom
        if not (match_fen_color:=re.match(r' ([bw])(.*)$', fs)):
            self.err = f"FEN: Illegal color at {fs} in {fen_str}"
            return self.err
        
        color, fs =  match_fen_color.groups()
        self.to_move = "white" if color == 'w' else 'black'

        if not (match_fen_castling:=re.match(r' ([-KQkq]+)(.*)$', fs)):
            self.err = f"FEN: Illegal castling at {fs} in {fen_str}"
            return self.err
        
        castling, fs = match_fen_castling.groups()
        for ch in castling:
            if ch == 'K':
                self.can_castle_white_kingside = True
            elif ch == 'Q':
                self.can_castle_white_queenside = True
            elif ch == 'k':
                self.can_castle_black_kingside = True
            elif ch == 'q':
                self.can_castle_black_queenside = True
            elif ch == '-':
                pass        # No castling rights
            else:
                self.err = f"FEN: Illegal castling {ch=} at {fs} in {fen_str}"
                return self.err


        if not (match_fen_en_passant:=re.match(r' ((-)|([a-h][1-8]))(.*)$', fs)):
            self.err = f"FEN: Illegal en passant at {fs} in {fen_str}"
            return self.err

        grps = match_fen_en_passant.groups()
        
        ep_stuff, en_passant_none, en_passant_sq, fs = grps
        if en_passant_none == "_":
            self.poss_en_passant = None
        else:
            self.poss_en_passant = en_passant_sq
            

        if not (match_fen_halfmove:=re.match(r' (\d+)(.*)$', fs)):
            self.err = f"FEN: Illegal halfmove clock at {fs} in {fen_str}"
            return self.err
        
        halfmove_clock, fs = match_fen_halfmove.groups()    
        self.half_move_clock = int(halfmove_clock)

        if not (match_fen_fullmove:=re.match(r' (\d+)(.*)$', fs)):
            self.err = "FEN: Illegal fullmove clock at {fs} in {fen_str}"
            return self.err
        
        fullmove_clock, fs = match_fen_fullmove.groups()
        self.full_move_clock = int(fullmove_clock)
        
        return None     # Successful FEN parsing/setup
    
    def fen_setup_row(self, rank_n, row_str):
        """ Setup from fen row
        :board_rank_n: rank 1...self.nsqy
        :row_str: row str e.g. 3qkbnr
        :returns: error msg if failed, else None
        """
        board_file_strs = "abcdefgh"
        board_rank_strs = "12345678"
        board_file_no = 1
        n_placed = 0
        for ch in row_str:
            if pmatch := re.match(r'[rnbqkpRNBQKP]', ch):
                piece = pmatch.group()
                sq = board_file_strs[board_file_no-1] + board_rank_strs[rank_n-1]
                self.board_setting[sq] = piece
                board_file_no += 1
                n_placed += 1
            elif pmatch := re.match(r'[1-8]', ch):
                board_file_no += int(pmatch.group())    # Skip squares
            else:
                err = f"FEN row character:'{ch}' not recognized in row_str:'{row_str}'"
                return err
        return None

    # Modeled, i.e. coppied from, after this function in chessboard.py    
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

    # Modeled, i.e. coppied from, after this function in chessboard.py                
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

    
    def to_fen_str(self):
        """ Generate FEN notation string from current board state
        :returns: string of FEN notation
        """
        fen_str = "FEN: "
        for ir in range(self.nsqy):
            empty_count = 0            
            for ic in range(self.nsqy):
                piece = self.get_piece(file=ic+1, rank=self.nsqy-ir)                
                if piece is not None:
                    if empty_count > 0:
                        fen_str += str(empty_count)
                        empty_count = 0
                    fen_str += piece
                else:
                    empty_count += 1
            if empty_count > 0:
                fen_str += str(empty_count)
            if ir < self.nsqy-1:
                fen_str += "/"      # No slash at end
        fen_str += " "+self.to_move[0]
        # Castling rights
        ctr_str = ""
        if self.can_castle_white_kingside:
            ctr_str += 'K'
        if self.can_castle_white_queenside:
            ctr_str += 'Q'
        if self.can_castle_black_kingside:
            ctr_str += 'k'
        if self.can_castle_black_queenside:
            ctr_str += 'q'
        if ctr_str == "":
            ctr_str = "-"
        fen_str += f" {ctr_str}"
        if self.poss_en_passant:
            fen_str += f" {self.poss_en_passant}"
        else:
            fen_str += " -"    
        fen_str += f" {self.half_move_clock}"
        fen_str += f" {self.full_move_clock}"
        return fen_str

    def export_to_bd(self, bd, must_be_present=True):
        """Export FEN values(settings) to Chessboard
        :bd: ChessBoard type to receive FEN setup
        :must_be_present: attributes must be present in board
                default: True    
        """

        for attr in self.attrs:
            if must_be_present:
                assert(hasattr(bd, attr))

        for attr in self.attrs:
            setattr(bd, attr, getattr(self, attr))        

    def import_from_bd(self, bd, must_be_present=True):
        """Import FEN values(settings) from Chessboard
        :bd: ChessBoard type to supply values
        :must_be_present: attributes must be present in board
                default: True    
        """

        for attr in self.attrs:
            if must_be_present:
                assert(hasattr(bd, attr))

        for attr in self.attrs:
            setattr(self, attr, getattr(bd, attr))        


if __name__ == '__main__':
    SlTrace.lg(f"Selftest: {__file__}")
    ntest = 0
    nfail = 0       # Count  failures
    
    def testit(desc):
        """ Do test
        :desc: test description
        """
        global ntest
        
        ntest += 1
        SlTrace.lg(f"Test {ntest}: {desc}")
        
    def if_fail_report(msg=None):
        """ count tests, fails and report failure
        :msg: test result: fail if not None and not "", success if None
        """
        global nfail
        
        if msg is not None and not "":
            nfail += 1
            SlTrace.lg(f"fail {nfail}: in test {ntest}, {msg}")
        
    def  test_summary():
        """ Summarize failures
        """
        SlTrace.lg(f"{ntest} tests")
        if nfail > 0:
            SlTrace.lg(f"Total fails: {nfail}")
        else:
            SlTrace.lg(f"No Failures")
        
    cf = ChessFEN()
    testit("See that erroneous strings fail parse")
    bad_str = "What's this?"
    if (err:=cf.parse(bad_str)):
        SlTrace.lg(f"Expected error:{err} from '{cf.fen_str}'")
    else:
        if_fail_report(f"Did not fail string {bad_str}")
        
    test_fen_strs = [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", # Starting position
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",   # After 1.e4
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", # after 1.... c5
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",   # after 2. Nf3     
    ]

    for fstr in test_fen_strs:
        testit(f"FEN string: {fstr}")
        if (err:=cf.parse(fstr)):
            if_fail_report(f"Parse error: {err}")
            continue
        fstr_cvt = cf.to_fen_str()
        if fen_match:=re.match(r'FEN:\s*(.*)$', fstr_cvt):
            fstr_cvt = fen_match.group(1)
        if fstr_cvt != fstr:
            if_fail_report("Converted not equal to original:"
                           f"\n {fstr}"
                           f"\n {fstr_cvt}"
                           "\n")

    class TestFoo:
        def __init__(self):
            pass

    tf = TestFoo()
    cf = ChessFEN()
    testit("Check import from non-Chessboard type")
    try:
        cf.import_from_bd(tf)
        if_fail_report("import_from_bd Accepting non-Chessboard")
    except:
        SlTrace.lg("Correctly rejecting bad import")

    testit("Check export to non-Chessboard type")
    try:
        cf.export_from_bd(tf)
        if_fail_report("export_from_bd Accepting non-Chessboard")
    except:
        SlTrace.lg("Correctly rejecting bad export")
    
    from chessboard import Chessboard
    testit("Check Chessboard setup")
    cb = Chessboard()
    try:
        cf.import_from_bd(cb)
        SlTrace.lg("OK import from initial Chessboard")
    except:
        if_fail_report("Failed import from initial Chessboard")
    
