#chess_spec_parse.py 18Sep 2026  crs, Author
""" Chess move specification parser
Developed after the fact to demonstrate onion-skin
parsing technique
"""
import re

class ChessSpecParse:
    """ Parsing table, list in order of matching
    The goal is to recognize and parse all legal
    move specifications and to recognize most illegal
    specifications.
    attribute name: unique identifier of move attribute
    regex matching pattern: regular expression used
            to match
    match_pat_group: match group index for attribute pattern
    """
    pt = [
        ["game_res", r"^(.*)(1-0|0-1|1/2-1/2)$"],
        ["ck", r"^(.*)([+])$"],
        ["ck_mate", r"^(.*)([#])$"],
        ["castle_queen", r"^(.*)(O-O-O)$"], # MUST preceed king
        ["castle_king", r"^(.*)(O-O)$"],
        ["promotion", r"^(.*)(=[QRBN])$"],
        ["destination", r"^(.*)([a-h][1-8])$"],
        ["capture", r"^(.*)([x:])$"],
        ["source_rank", r"^(.*)([1-8])$"],
        ["source_file", r"^(.*)([a-h])$"],
        ["piece", r"^(.*)([KQRBN])$"],

    ]
    """ Table of display instructions
    for atts_str()
    List is in order, left to right,
    of description display
    Each entry is a of instructions:
        pt_name: pattern attribute
        displayed
            value - display value
            name - display attribute name
            name_value - display name, value
        """
    display_order = [
        ["piece", "value"],
        ["source_file", "name_value"],
        ["source_rank",  "name_value"],
        ["destination", "value"],
        ["capture", "name"],
        ["promotion", "name_value"],
        ["ck", "name"],
        ["ck_mate", "name"],
        ["castle_queen", "name"],
        ["castle_king", "name"],
        ["game_res", "name_value"],
    ]
    def __init__(self, spec):
        """ Parse specification
        :spec: chess move specification (algebraic notation
            e.g.s., e4, Rfe+, O-O-O)
        """
        self.spec = spec
        self._is_ok = False # Set True iff successful
        self.matched = {}   # Matched attributes, by name
                            # matched sub pattern
        self.match_list()
        
    def match_list(self):
        """ Run through list of matches
        Check matches for special circumstances
        """
        self._msg = "UNKNOWN REASON"
        self.rem_str = self.spec
        
        if " " in self.spec:
            return self.error(f"Embeded space in spec '{self.spec}'")
        
        for ptm in self.pt:
            pt_name, pt_regex = ptm
            pat_match = re.match(pt_regex, self.rem_str)
            if pat_match:
                self.rem_str, matched_pat = pat_match.groups()
                self.matched[pt_name] = matched_pat

                # Check for obvious errors after each matched pattern type
                match pt_name:
                    case "game_res":
                        if self.rem_str == "":
                            self._is_ok = True
                            return
                        
                    case "ck" | "ck_mate":
                        if pat_match and (ck:=self.is_any(["+","#"])):
                            return self.error(f"misplaced {ck}")
                    
                    case "castle_king" | "castle_queen":
                        if self.rem_str != "":
                            return self.error(f"Non-empty remaining string: '{self.rem_str}'")

                        self._is_ok = True
                        return
                    
                    case "promotion":
                        if pat_match and (ck:=self.is_any(["=","(",")"])):
                            return self.error(f"misplaced {ck}")
                    
                    case "destination":
                        pass
                    case "capture":
                        if (ck:=self.is_any(["x",":"])):
                            return self.error(f"misplaced {ck}")
                        
                    case "piece":
                        if (ck:=self.is_any(list("KQRBNP"))):
                            return self.error(f"misplaced piece {ck}")
                        
                    case "source_file":
                        if (ck:=self.is_any(list("abcdefgh"))):
                            return self.error(f"misplaced {ck}")
                        
                    case "source_rank":
                        if (ck:=self.is_any(list("12345678"))):
                            return self.error(f"misplaced {ck}")
                        
            else:
                # For match fails
                match pt_name:
                    case "game_res":
                        if (err_match:=re.match(r"^(.*?)(\d+-\d+)$", self.rem_str)):
                            return self.error(f"Bad game_res:'{err_match.group(2)}'")
                        
                        if (err_match:=re.match(r"^(.*?)(\d+/\d+-\d+/\d+)$", self.rem_str)):
                            return self.error(f"Bad game_res: {err_match.group(2)}'")
                    
                    case "destination":
                        if (err_match:=re.match(r"^(.*?)(\w\d+)$", self.rem_str)):
                            return self.error(f"Bad destination: {err_match.group(2)}'")
                    
                    case "source_rank":
                        if (err_match:=re.match(r"^(.*?)([09])$", self.rem_str)):
                            return self.error(f"Bad rank: {err_match.group(2)}'")
                    
                    case "source_file":
                        if (err_match:=re.match(r"^(.*?)([i-z])$", self.rem_str)):
                            return self.error(f"Bad rank: {err_match.group(2)}'")
                            
                    case "piece":
                        self.matched[pt_name] = "P" # Pawn if no piece letter
                        if (ck:=self.is_any(list("KQRBNP"))):
                            return self.error(f"misplaced piece {ck}")
                        
                     
        if self.rem_str != "":
            second_look = ChessSpecParse(self.rem_str)
            if second_look and second_look.is_ok():
                return self.error(f"Contains second spec: {self.rem_str}")
            
            self._is_ok = False
            self._msg = f"Unused = '{self.rem_str}'"
            return
        
        self._is_ok = True

    def error(self, msg):
        """ Announce error
        :msg: error message string
        :returns: msg
        """
        self._is_ok = False
        self._msg = msg
        return msg

    def is_any(self, list_of, st=None):
        """ Return first if found
        :list_of: list of substrings
        :st: target string
            default: self.rem_str
        :returns: first found, None if none found
        """
        if st is None:
            st = self.rem_str
        for ck_str in list_of:
            if ck_str in st:
                return ck_str
        return None
                
    def att(self, att):
        """ Get attribute
        :att: attribute
        :returns: att value, None if not present
        """
        if att in self.matched:
            return self.matched[att]
        return None
        
    def atts_str(self):
        """ Return list of move attributes
        """
        st = ""
        if not self.is_ok():
            st += f"Illegal specification: {self.msg()} "
        for do in self.display_order:
            pt_name, disp_type = do
            if pt_name in self.matched:
                if disp_type == "name":
                    disp = pt_name
                elif disp_type == "value":
                    disp = self.matched[pt_name]
                elif disp_type == "name_value":
                    disp = f"{pt_name}:{self.matched[pt_name]}"
                else:
                    print(f"atts_str: unsupported {disp_type=}")
                    continue
                
                st += f" {disp}"
        return st
                       
    def is_ok(self):
        """ Test if parsing succeeded
        """
        return self._is_ok
    
    def msg(self):
        """ Returns error message
            None if OK
        """
        return self._msg

if __name__ == '__main__':
    import pgn

    def test_parse_game(game_desc, game_text, list_ok=False):
        """ Test parsing on game text
        :game_desc: game description
        :game_text: game text string
        :list_ok: list if ok, default: True
        :returns: error msg if any else None
        """
        print(game_desc)
        pgn_games = pgn.loads(game_text)
        game = pgn_games[0]
        moves = game.moves
        for spec in moves:
            csp = ChessSpecParse(spec)
            if not csp.is_ok():
                print(f"{spec}: parse failed {csp.msg()}")
                break
            if list_ok:
                print(f"{spec}: {csp.atts_str()}")

    def test_parse_specs(specs_desc, specs_list, list_ok=False):
        """ Test parsing on game text
        :specs_desc: specs examples description
        :specs_list: specs list of the following
            spec_text, description[, failure expected description]
        :list_ok: list if ok, default:False            
        :returns: error msg if any else None
        """
        print(specs_desc)
        for spl_ent in specs_list:
            spec = spl_ent[1]
            spec_desc = spl_ent[0]
            if len(spl_ent) == 3:
                spec_err_desc = spl_ent[2]
            else:
                spec_err_desc = None
                
            csp = ChessSpecParse(spec)
            if not csp.is_ok() and spec_err_desc is None:
                msg = f"{spec}: parse failed"
                print(msg)
                return msg
            
            if csp.is_ok() and spec_err_desc is not None:
                msg = f"{spec}: did not fail when {spec_err_desc}"
                print(msg)
                return msg
            
            if list_ok:
                print(f"{spec}: {csp.atts_str()}")

    """ Test cases
    """
    pattern_examples_desc = """
    Game of pattern examples
    Not really a game just a set of specs
    """
    pat_exs = [
        ["game_res",        "1/2-1/2"],
        ["game_res",        "1/2-1/4",  "no result 1/2-1/4"],
        ["ck",              "Rfe8+"],
        ["ck",              "Rfe8++",   "check is +"],
        ["ck_mate",         "Rc2+#",    "mate:Rc2+#"],
        ["ck_mate",         "#Rc2",     "# goes last"],
        ["castle_queen",    "O-O-O+"],
        ["castle_queen",    "+O-O-O", "+ is after"],
        ["castle_king",     "O-O#"],
        ["castle_king",     "KO-O", "No piece for castle"],
        ["promotion",       "=Q+"],
        ["promotion",       "=P", "can't promote to pawn"],
        ["destination",     "Qa4"],
        ["destination",     "Qj4", "files only a-h"],
        ["capture",         "Rxe1"],
        ["capture",         "Rxe9", "Ranks only a-8"],

        ["piece",           "Ne5"],
        ["piece",           "Nx5", "Files only a-h"],
        ["piece",           "h3"],
        ["piece",           "j3", "Pawn file only a-h"],
        ["source_file",     "Rfe8+"],
        ["source_file",     "R1aa4", "source file, then rank"],
        ["source_file",     "Rie8+", "source_file only a-h"],
        ["source_rank",     "R1d1"],
        ["source_rank",     "R9d1", "source_rank only 1-8"],
        ["multiple spec",   "e4 e5", "Two moves separated"],
        ["multiple spec",   "e4e5", "Two moves together"],
    ]
    
    game_commentary = """
    Game of the Century
    From https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
    """
    demo_game_text = """
    [Event "Third Rosenwald Trophy"]
    [Site "New York, NY USA"]
    [Date "1956.10.17"]
    [EventDate "1956.10.07"]
    [Round "8"]
    [Result "0-1"]
    [White "Donald Byrne"]
    [Black "Robert James Fischer"]
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
    error_count = 0
    list_ok = False
    #list_ok = True
    pat_exs_list_ok = True
    
    msg = test_parse_game(game_commentary, demo_game_text, list_ok=list_ok)
    if msg:
        error_count += 1
        print(f"ERROR {error_count} {msg}")
    msg = test_parse_specs(pattern_examples_desc, pat_exs, list_ok=pat_exs_list_ok)
    if msg:
        error_count += 1
        print(f"ERROR {error_count} {msg}")
            
