#chess_spec_parse.py 18Sep 2026  crs, Author
""" Chess move specification parser
Developed after the fact to demonstrate onion-skin
parsing technique
"""
import re

class ChessSpecParse:
    """ Parsing table, list in order of matching
    attribute name: unique identifier of move attribute
    regex matching pattern: regular expression used
            to match
    match_pat_group: match group index for attribute pattern
    """
    pt = [
        ["game_res", r"^(.*)(1-0|0-1|1/2-1/2)$", 2],
        ["ck", r"^(.*)([+])$", 2],
        ["ck_mate", r"^(.*)([#])$", 2],
        ["castle_queen", r"^(.*)(O-O-O)$", 2], # MUST preceed king
        ["castle_king", r"^(.*)(O-O)$", 2],
        ["promotion", r"^(.*)(=[QRBN])$", 2],
        ["destination", r"^(.*)([a-h][1-8])$",2],
        ["capture", r"^(.*)([x:])$", 2],

        # looking from the left end
        ["piece", r"^([KQRBN])(.*)$", 1],
        ["source_file", r"^([a-h])(.*)$",1],
        ["source_rank", r"^([1-8])(.*)$", 1],
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
        rem_str = self.spec
        for ptm in self.pt:
            pt_name, pt_regex, pt_i = ptm
            pat_match = re.match(pt_regex, rem_str)
            if pat_match:
                if pt_i == 1:
                    game_pat, rem_str = pat_match.groups()
                else:
                    rem_str, game_pat = pat_match.groups()
                self.matched[pt_name] = game_pat
                if pt_name == "game_res":
                    if rem_str == "":
                        self._is_ok = True
                        return
                
                if pt_name in ["castle_king", "castle_queen"]:
                    self._is_ok = True
                    return
                
            elif pt_name == "piece":
                self.matched[pt_name] = "P" # Pawn if no piece letter
        self._is_ok = True
    
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

if __name__ == '__main__':
    import pgn

    def test_parse_game(game_desc, game_text):
        """ Test parsing on game text
        :game_desc: game description
        :game_text: game text string
        :returns: error msg if any else None
        """
        print(game_desc)
        pgn_games = pgn.loads(game_text)
        game = pgn_games[0]
        moves = game.moves
        for spec in moves:
            csp = ChessSpecParse(spec)
            if not csp.is_ok():
                print(f"{spec}: parse failed")
                break
            
            print(f"{spec}: {csp.atts_str()}")

    def test_parse_specs(specs_desc, specs_list):
        """ Test parsing on game text
        :specs_desc: specs examples description
        :specs_list: specs list of the following
            spec_text, description[, failure expected description]            
        :returns: error msg if any else None
        """
        print(specs_desc)
        for spl_ent in specs_list:
            spec = spl_ent[0]
            spec_desc = spl_ent[1]
            ###if len(sp)
                
            csp = ChessSpecParse(spec)
            if not csp.is_ok():
                print(f"{spec}: parse failed")
                break
            
            print(f"{spec}: {csp.atts_str()}")

    """ Test cases
    """
    pattern_examples_desc = """
    Game of pattern examples
    Not really a game just a set of specs
    """
    
    
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
    msg = test_parse_game(game_commentary, demo_game_text)
    if msg:
        error_count += 1
        print(f"ERROR {error_count} {msg}")
            
