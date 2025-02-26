#chess_move_notation.py 19Feb2025  crs from chess_move.py
r""" 
Parse chess move notation, saving move information
for further analysis, execution

Notation summary
general patterns
Additions:
    stuff 0-1, 0-0, 1-0     Rc2# 0-1   game result
    stuff +                 Bxc4+      move with check
    stuff #
    
basic move patterns                      
    O-O, O-O-O              O-O O-O-O
    ([A-Z])([a-z]\d+)     Nf3 Nf6 Nc3 Bg7 Rd1
    [a-z]\d+            c4 g6 d4 c6
    [a-z]x[a-z]\d+          dxc4
    [A-Z]x[a-z]\d+          Qxc4 Nxc3 Nxd4+
    [A-Z][a-z][a-z]\d+      Nbd7
    [A-Z][a-z][a-z]\d+      Rfe8+
    [A-Z][a-z]]d+[a-z]\d+   Qh4e1
    [a-z]x[a-z]             bxc
    """

"""
"""
import re

from select_trace import SlTrace


class ChessMoveNotation:
    """ Do all chess move specification parsing
    """
    def __init__(self, chess_move):
        """ Setup link with chess move
        :chess_move: reference to ChessMove instance
        :returns: None if OK, error message text if problem
        """
        self.cm = chess_move
        self.err_count = 0          # Count of errors      
        self.err_first = None       # first error, if any   
        self.err_first_move_no = 0  # first error move no
                
    def __str__(self):
        """ String form for debugging/analysis
        """
        ret = f"CMN: {self.spec}"
        ret += f"  {self.get_to_move()}"
        if self.piece is not None:
            ret += f" {self.piece}"
        elif self.piece_type is not None:
            ret += f" type:{self.piece_type}"
        if self.err:
            ret += f" {self.err}\n    "
        if self.is_castle:
            ret += f" castle"
            if self.is_castle_queen_side:            
                ret += f" queen side"
            else:
                ret += f" king side"
        if self.orig_sq is not None:
            ret += f" orig_sq:{self.orig_sq}"  # move's original square
        elif self.orig_sq_file is not None:
            ret += f" orig_sq_file:{self.orig_sq_file}"
        ret += f" dest_sq:{self.dest_sq}" # move's destination square
        if self.dest_sq_mod:
            ret += f"dest_sq_mod:{self.dest_sq_mod}"
        if self.is_capture:
            ret += " capture"
        if self.is_check:
            ret += " check"
        if self.is_check_mate:
            ret += " checkmate"
        if self.game_result is not None:
            ret += f" {self.game_result}"
        return ret
            
                        
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
        # Change if/when appropriate
        self.err = None         # Error msg, None == no error
        self.spec = spec        # move specification
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

        spec_rem = spec     # remaining, adjusted as parts are decoded
        # Check if game result
        if (match_res := re.match(r'(.*)\s+([0-1]-[0-1])\s*$', spec_rem)):
            spec_rem, self.game_result = match_res.groups()
        
        # Check if check or mate
        if (match_res := re.match(r'(.*)\s*([+#])$', spec_rem)):
            spec_rem,check_or_mate = match_res.groups()
            if check_or_mate == '+':
                self.is_check = True
            else:
                self.is_check_mate = True    

        # Check if castle
        if (match_castle := re.match(r'(O-O|O-O-O)', spec_rem)):
            self.is_castle = True
            if match_castle.group(1) == 'O-O-O':
                self.is_castle_queen_side = True
            else:
                self.is_castle_king_side = True
            return None     # Done part checking
        
        # Pick off destination from tail end
        # <file><rank> or <file>
        if (match_res := re.match(r'(.*)([a-z]\d+)$', spec_rem)):
            spec_rem,self.dest_sq = match_res.groups()
        elif (match_res := re.match(r'(.*)([a-z])$', spec_rem)):
            spec_rem,self.dest_sq_file = match_res.groups()

        # Determine if capture
        if (match_res := re.match(r'(.*)([x:])$', spec_rem)):
            self.is_capture = True
            spec_rem,self.capture_ind = match_res.groups()
            
        # Determine move active piece
        if (match_res := re.match(r'([A-Z])(.*)$', spec_rem)):
            piece, spec_rem = match_res.groups()
            self.piece_type = self.piece_to_type(piece)
            self.piece_choice = spec_rem
        elif (match_res := re.match(r'([a-z])(.*)$', spec_rem)):
            self.orig_sq_file,spec_rem = match_res.groups()
            self.piece_choice = spec_rem
        elif spec_rem == "":
            self.piece_type = 'p'
            self.piece_choice = ""
        else:
            self.err = f"Can't determine active piece from {spec_rem}"
            self.err += f" spec: {self.spec}"
            return self.err_add(self.err)
        
        return None
    
    def decode_complete(self):
        """ Finish decoding process, started by decode_spec_parts
        Uses settings in self (ChessMoveNotation instance)
        """
        if self.is_castle:
            self.decode_castle()
            return self.err_add()

        # Complete piece determination
        if self.decode_piece():
            return self.err_add()
        
        # Complete parsing destination square
        if self.decode_orig_sq():
            return self.err_add()
        
        # Complete parsing origin square
        if self.decode_orig_sq():
            return self.err_add()

    def decode_piece(self):
        """ Complete determination of move piece
        """
        if self.piece is not None:
            return self.err_add()
        
        if self.piece_type is None:
            if self.orig_sq_file is not None:
                self.piece_type = 'p'

        self.piece = self.piece_type_to_piece(self.piece_type)
        if self.piece is None:
            return self.err_add("Can't determine piece from {self.spec}")        
        return self.err_add()

    def decode_dest_sq(self):
        """ Complete parsing destination square
        """
        if self.dest_sq is not None:
            return self.err_add()   # Quit if already got it.
        
        if self.dest_sq_file is not None:
            if self.orig_sq_file is not None:
                return self.err_add("Going to do axb case later")
        return self.err_add()       # OK 
    
    def decode_orig_sq(self):
        """ Continue spec parsing to determine move's piece
        original sqare
        :Uses instance values setup by decode_spec_parts
        :returns:None if OK, error msg if parsing error
        """
        if self.orig_sq is not None:
            return self.err_add()   # Quit if already got it.
        
        if self.dest_sq is None:
            return self.err_add("Can't get orig_sq if no dest_sq")

        sq = self.get_orig_sq(piece = self.piece,
                              piece_choice=self.piece_choice,
                              dest_sq=self.dest_sq)
        if sq is None:
            return self.err_add("Can't find orig_sq"
                                f" with piece = {self.piece},"
                              f" piece_choice={self.piece_choice},"
                              f" dest_sq={self.dest_sq}")
        self.orig_sq = sq
        return self.err_add()
         
    def decode_castle(self):
        """ Complete castle parsing
        :spec: castle specification oo or ooo
        :to_move:white or black
            default: ChessMove to_move, else current board.to_move 
        :returns: None if OK, else error message           
        """
        spec = self.spec
        if spec == "O-O":
            self.is_castle_king_side = True
        elif spec == "O-O-O":
            self.is_castle_queen_side =True
        else:
            self.err = "Unrecognized castle {spec}"
            return self.err
        
        to_move = self.get_to_move()
        
        if self.is_castle_king_side:
            if not(err := self.can_castle()):
                return err
            
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
            if not(err := self.can_castle(False)):
                return err
            
            if to_move == "white":
                king_sq = "e1"
                king_dest = "c1"
                rook_sq = "a1"
                rook_dest = "d1"
            else:
                king_sq = "e8"
                king_dest = "g8"
                rook_sq = "h8"
                rook_dest = "f8"
        self.orig_sq = king_sq
        self.dest_sq = king_dest
        self.orig2_sq = rook_sq
        self.dest2_sq = rook_dest
        
        self.err = None
        return None     # Successful
    
    def err_add(self, msg=None):
        """ Set and Count errors
        :msg: count as error if msg != ""
            default: self.err - current parsing error message
        :returns: msg
        """
        if msg is None:
            msg = self.err
            
        if msg is not None and msg != "":
            self.err = msg
            self.err_count += 1
            if self.err_first is None:
                self.err_first = msg
                self.err_first_move_no = self.cm.get_move_no()
        return msg    

    @staticmethod
    def game_to_specs(game_str):
        """ Convert standard game string into a
        list of move specs
        e.g.
            1.Nf3 Nf6 2.c4 g6 3.Nc3 Bg7 4.d4 O-O
            5.Bf4 d5 6.Qb3 dxc4 7.Qxc4 c6 8.e4 Nbd7 ...
            into
                ["Nf3","Nf6",  "c4","g6",  "Nc3","Bg7",
                "d4", "O-O",
                "Bf4","d5",  "Qb3","dxc4",  "Qxc4","c6",
                "e4" "Nbd7" ...] 
        :game_str: string above
        :returns: list of move specs
        """
        game_str = game_str.rstrip()
        gs_move_pairs = re.split(r'\s*\d+\.', game_str)
        moves = []
        for move_pair in gs_move_pairs:
            if move_pair == '':
                continue
            wmove, bmove = re.split(r'\s+', move_pair, maxsplit=1)
            moves.append(wmove)
            moves.append(bmove)
        return moves


    """
    Links to Chessboard
    """

    def get_prev_move(self):
        """ Get previous move, with no change
        Used to check for thigs suchas E.P
        :returns: previous move (ChessSaveUnit)
            None if no previous move saved
        """
        return self.self.board.get_prev_move()      # indirect rather than add board just for this

    """
    Links to ChessMove
    """

    def can_castle(self, king_side=True, to_move=None):
        """ Determine if we can castle
        :king_side: True if king side, else queen side
                default: kingside                
        :returns: True if the requested castling is permited
        """
        return self.cm.can_castle(king_side=king_side, to_move=to_move)

    def get_orig_sq(self, piece, piece_choice=None,
                    dest_sq=None):
        """ Find move's original square
        :piece: piece to move e.g. K,Q...P
        :piece_choice: disambiguation if choice
        :dest_sq:  destination square
        :returns: sq, None if none apply
        """
        return self.cm.get_orig_sq(piece=piece, piece_choice=piece_choice,
                                   dest_sq=dest_sq)

    def get_to_move(self):
        """ Whose move is it?
        """
        return self.cm.get_to_move()

    def piece_to_type(self, piece):
        """ Get piece's type (lowercase of piece)
        :piece: piece uppercase for white
        :returns: piece type (lowercase)
        """
        return self.cm.piece_to_type(piece)
    
    def piece_type_to_piece(self, type, to_move=None):
        """ Get piece's color
        :piece_type_to_piece: piece uppercase for white
        :to_move: black/white
            default: from board
        :returns: piece    # uppercase if white lowercase if black
        """
        return self.cm.piece_type_to_piece(type=type, to_move=to_move)
    
    def make_move_update(self, move=None):
        """ Update move object with parsing results
        :move: move object to update
            default: use self.move
        """
        if move is None:
            move = self.cm
        move.orig_sq = self.orig_sq
        move.dest_sq = self.dest_sq
        move.spec = self.spec
        move.dest_sq_mod = self.dest_sq_mod
        move.orig2_sq = self.orig2_sq
        move.dest2_sq = self.dest2_sq
        move.dest2_sq_mod = self.dest2_sq_mod
        
    def make_move(self, just_notation=False,
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
                
        return self.cm.make_move(just_notation=just_notation,
                                    orig_sq=orig_sq,
                                    dest_sq=dest_sq,
                                    dest_sq_mod=dest_sq_mod,
                                    orig2_sq=orig2_sq,
                                    dest2_sq=dest2_sq,
                                    dest2_sq_mod=dest2_sq_mod,
                                    update=update,
                                    spec=spec)

           
if __name__ == "__main__":

    SlTrace.clearFlags()
    #SlTrace.setFlags("print_board,no_ts")
    SlTrace.setFlags("no_ts")
    
    import argparse
    
    from chess_move import ChessMove  # For minimal support
    from chessboard import Chessboard  # For minimal support
    from chessboard_print import ChessboardPrint
    from chessboard_display import ChessboardDisplay
    
    show_passes = True          # Show passed tests
    quit_on_fail = True         # Quit on first fail    
    just_parts = False          # Just do/display the notation parsing
    just_complete = False       # Just display complete parseing
    just_board = False          # Just display the board state
    #just_parts = True
    #just_complete = True
    #just_board = True
    include_board = True
    gui_display = True
    cb = Chessboard()
    cb.standard_setup()
    cbp = ChessboardPrint(cb)

    cm = ChessMove(cb)
    cmn = ChessMoveNotation(cm)


    if gui_display:
        import tkinter as tk
        mw = tk.Tk()   # Controlling window

    cbds = []
    def display_board(desc=None):
        """ Display current board state
        :desc: description
            default: no description
        """
        if desc is None:
            desc = ""
        display_options = "visual_s"
        #display_options = None
        bd_str = cbp.display_board_str(display_options=display_options)
        SlTrace.lg("\n"+desc+"\n"+bd_str, replace_non_ascii=None)
        if gui_display:
            mw2 = tk.Toplevel()     # Subsequent window                
            cbd = ChessboardDisplay(cb.copy())
            cbds.append(cbd)
            cbd.display_board(title=desc)
            cbd.update()
    
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
    

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--moves', default=moves,
                        help=("Move string"
                              " (default:moves"))
    parser.add_argument('-f', '--file', default=None,
                        help=("Moves file"
                              " (default:use string"))

    parser.add_argument('-p', '--just_parts', default=just_parts,
                        help=("Just print initial parts parsing"
                              " (default:no restriction"))
    parser.add_argument('-c', '--just_complete', default=just_complete,
                        help=("Just print complete move parsing"
                              " (default:no restriction"))
    parser.add_argument('-b', '--just_board', default=just_board,
                        help=("Just print board after move"
                              " (default:no restriction"))
    parser.add_argument('-s', '--show_passes', action='store_true', default=show_passes,
                        help=(f"Show passes"
                              f" (default: {show_passes}"))
    parser.add_argument('-q', '--quit_on_fail', action='store_true', default=quit_on_fail,
                        help=(f"Quit on first failure"
                              f" (default: {quit_on_fail}"))

    args = parser.parse_args()             # or die "Illegal options"
    
    file = args.file
    moves = args.moves
    just_parts = args.just_parts
    just_complete = args.just_complete
    just_board = args.just_board
    show_passes = args.show_passes
    quit_on_fail = args.quit_on_fail
        
    
    
    move_specs = ChessMoveNotation.game_to_specs(moves) 
    for move_spec in move_specs:
        cm = ChessMove(cb)
        move_no = cm.get_move_no()
        to_move = cm.get_to_move()
        move_no_str = f"move {move_no:2}: "
        if   to_move == "black":
            move_no_str = " " * len(move_no_str)
        stage = "notation"
        if cmn.decode_spec_parts(move_spec):
           SlTrace.lg(f"{move_no_str} {stage} Error: {move_spec}: {cmn.err}")
           if quit_on_fail:
               break
           
        else:
            if not just_complete and not just_board:
                SlTrace.lg(f"{move_no_str} {stage} {cmn}")
                if just_parts:
                    cmn.make_move(just_notation=True)
                    continue
            stage = "+bd info"
            if cmn.decode_complete():
                SlTrace.lg(f"{move_no_str} {stage} {cmn.err}")
                bd_str = cbp.display_board_str()
                SlTrace.lg("\n"+bd_str)                
                if quit_on_fail:
                    break
                continue
            else:
                if not just_board:
                    SlTrace.lg(f"{move_no_str} {stage} {cmn}")
                
        cmn.make_move()
        if include_board or just_board or SlTrace.trace("print_board"):
            desc = f"After Move: {move_no}" 
            if to_move == "black":
                prev_white_move = cb.get_prev_move(back=-2)   # After save
                prev_desc = prev_white_move.spec
                desc += f" {prev_desc}"
            desc += f" {cmn.spec}"
            display_board(desc)

    SlTrace.lg(f"End of selftest from {__file__}")
    if cmn.err_count > 0:
        SlTrace.lg(f"Parse Errors:{cmn.err_count}")
        SlTrace.lg(f"First error: move {cmn.err_first_move_no}:"
                   f" {cmn.err_first}")
    if gui_display:
        mw.mainloop()     