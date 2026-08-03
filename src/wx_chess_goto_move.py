import wx
import wx.grid
from itertools import zip_longest
from graphics_braille.select_trace import SlTrace, SelectError

from chess_move_notation import ChessMoveNotation


class ChessGotoMove(wx.Frame):
    def __init__(self,
                 chess_game_display,
                 game=None,
                 moves=None,
                 on_move_change=None,
                 pos=(900,100),
                 size=(240,700)):
        """ Setup goto move window
        :chess_game_display: chess game display object
        :game: game (PGN)
        :moves: moves 
        :on_move_change: called with new move_no, moved
                to export move change to chess_game_display
                default: no call
        :pos:  x,y position default:(600,600)
        :size: (width,height) default:(200,300)
        """
        self.chess_game_display = chess_game_display
        self.total_half_moves = 0 # Updated as found
        self.cur_half_moves = 0   # Current position, in half moves
        self.ignore_select = False
        super().__init__(None, title="Chess Goto",
                         size=size)
        self.on_move_change = on_move_change
        
        self.set_moves(game=game,  moves=moves)
        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL,
                       self.on_cell_select)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        gw = self.grid.GetGridWindow()
        gw.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.SetPosition(pos)
        self.in_goto_num = False  # building goto number from key strokes
        self.Show()

    def export_move_change(self, move_no=None, moved=None): 
        """ Export move change to chess_game_display
        :move_no: move number 0-beginning,
        :moved: color moved "white"/"black"
        """
        if self.on_move_change is not None:
            self.on_move_change(move_no=move_no, moved=moved)

    def get_total_half_moves(self):
        """ Count of half moves
        """
        return self.total_half_moves

    def get_cur_half_moves(self):
        """ Count of half moves
        """
        return self.cur_half_moves
    
    def on_key_down(self, event):
        key = event.GetKeyCode()
        SlTrace.lg(f"\n\non_key_down:{key=}"
                   f" {chr(key)=}")
        if not self.in_goto_num:
            if key in [ord("0"),ord("1"),ord("2"),ord("3"),ord("4"),
                     ord("5"),ord("6"),ord("7"),ord("8"),ord("9")]:
                self.in_goto_num = True
                self.key_str =  ""
                self.key_str += chr(key)
                return
        else:       # Building goto number
            if key in [ord("0"),ord("1"),ord("2"),ord("3"),ord("4"),
                     ord("5"),ord("6"),ord("7"),ord("8"),ord("9"),
                     ord("b"),ord("B")]:
                self.key_str += chr(key)
                return
            
            elif key in [wx.WXK_RETURN, ord("G")]:  # Goto number terminator
                self.in_goto_num = False
                if self.goto_move_no(self.key_str):
                    return
                else:
                    SelectError(f"Goto num {self.key_str} unrecognized")
                return
        if key in [wx.WXK_SPACE, 43]:       # 43 code for +                   
            self.set_half_move_relative(1)
            return
        
        elif key in [wx.WXK_BACK, ord("-")]:
            self.set_half_move_relative(-1)
            return
        
        
        elif chr(key) in "LS":
            self.chess_game_display.on_chess_goto_move_cmd(chr(key))
            return
        # Call event.Skip() so the grid still moves the selection/cursor
        event.Skip()

    def on_left_click(self, event):
        SlTrace.lg("\n\non_left_click")
        event.Skip()
        
    def on_cell_select(self, event):
        if self.ignore_select:
            event.Skip()
            return          # Just update selection
        
        irow = event.GetRow()
        icol = event.GetCol()
        SlTrace.lg(f"Selected cell at Row: {irow}, Col: {icol}")
        moved = "black" if icol == 2 else "white"
        move_no_plus = str(irow)
        if moved == "black":
            move_no_plus += "B"
        self.goto_move_no(move_no_plus)    
        event.Skip()

    def goto_move_no(self, move_no_plus):
        """ Go to move number
                
        :move_no_plus: number d+[bB]?
        :returns: True iff successful
        """
        SlTrace.lg(f"goto_move_no({move_no_plus})")
        move_no_str = move_no_plus
        if move_no_str.upper().endswith("B"):
            moved = "black"
            move_no_str = move_no_str[:-1]
        else:
            if move_no_str.upper().endswith("W"):
                move_no_str = move_no_str[:-1] 
            moved = "white"
        try:
            move_no = int(move_no_str)
            self.set_move(move_no=move_no, moved=moved,
                          ignore_select=True)
        except:
            return False
        SlTrace.lg(f"goto_move_no({move_no_plus}) {move_no=} {moved=}")
        SlTrace.lg(f"{self.get_cur_half_moves()=}")
        return True
    
    def hm_to_row_col(self, half_move):
        """ Half-move to row,col
        grid table 3 cols, n+1 rows, first for beginning
        row - move number, white move, black move + game status
        col - 0 move number
              1 white move
              2 black move
        :half_move: number of moves white+black
        :returns: (row, col), starting at 0
        Legal half-moves range:
            hm  row col move(number,moved)
            0 - 0   0   0 "" - beginning (before any moves)
            1 - 1   1   1 white  - after white's first move
            2 - 1   2   1 black  - after black's first move
            3 - 2   1   2 white  - after white's second move
            4 - 2   2   2 black  - after black's second move
            n                    - after nth move

        """
        if half_move <= 0:
            irow = 0
            icol = 0
        else:
            irow = (half_move+1)//2        
            icol = 1 if half_move%2 == 1 else 2
        return irow,icol


    def row_col_to_hm(self, row, col):
        """Convert table row, col(zero based)
        to half_moves
        """
        if row <= 0:
            return 0

        hm = row*2-col%2
        return hm

    def set_half_move_relative(self, hm_adj=1, ignore_select=False):
        """ Adjust current move by hm_adj
        Legal half-moves range: 0 - beginning (before any moves)
                                1 - after white's first move
                                2 - after black's first move
                                n - after nth move
                
        :hm_adj: half-move adjustment default: next move
                Illegal moves are ignored
        :ignore_select: True - suppress on_select events
                default: False
        """
        SlTrace.lg(f"set_half_move_relative({hm_adj=})")
        cur_hf = self.get_cur_half_moves()
        new_half_move = cur_hf + hm_adj
        self.set_half_move(new_half_move, ignore_select=ignore_select)

    def set_half_move(self, half_move, ignore_select=False):
        """ Adjust current move by hm_adj
                
        :half_move: half-move default: next move
                Illegal moves are ignored
        :ignore_select: True - suppress on_select events
                default: False
        """
        SlTrace.lg(f"set_half_move:{half_move=},"
                   f" beginning  hm ={self.get_cur_half_moves()}")
        total_half_move = self.get_total_half_moves()
        min_half_move = 0
        if half_move < min_half_move or half_move > total_half_move:
            SlTrace.lg(f"half_move {half_move} is out of range"
                       f" {min_half_move}"
                       f" - {total_half_move}")
            return

        irow, icol = self.hm_to_row_col(half_move)
        SlTrace.lg(f"{irow=} {icol=}")
        self.ignore_select = ignore_select        
        self.DoSetGridCursor(irow, icol)
        self.ignore_select = False
        self.cur_half_moves = half_move
        SlTrace.lg(f"    {half_move=},{ignore_select=})")
        SlTrace.lg(f"    {irow=}, {icol=}, hm={self.get_cur_half_moves()}")

    def set_cur_half_moves(self, half_moves):
        """Set half_moves count
        :half_moves: half-moves in play
        """
        self.cur_half_moves = half_moves
            


    def set_move(self, move_no=0, moved="white",
                    ignore_select=False):
        """ Set move display
        :move_no: move number 0 - beginning, else recent move
        :moved: who "white", "black"
        :ignore_select: True - block select
                default: False
        """
        SlTrace.lg(f"set_move({move_no=}, {moved=})")
        if moved == "white":
            icol = 1
        else:
            icol = 2
        self.ignore_select = ignore_select        
        self.DoSetGridCursor(move_no, icol)
        self.ignore_select = False
        cur_half_moves = self.row_col_to_hm(move_no, icol)
        self.cur_half_moves = cur_half_moves
        self.export_move_change(move_no=move_no,
                                moved=moved)

    def set_moves(self, game=None, moves=None):
        """ Set game moves
        :game: game  PGN
            OR
        :moves: move specification string
        """
        self.total_half_moves = 0 # Updated as found
        SlTrace.lg(f"set_moves: {game=} {moves=}")
        move_pairs = []
        half_moves = 0
        if game is not None:
            move_pairs = list(zip_longest(game.moves[::2],
                            game.moves[1::2], fillvalue=""))
            half_moves = len(game.moves)
        elif moves is not None:            
            move_specs = ChessMoveNotation.game_to_specs(moves)
            move_pairs = list(zip_longest(move_specs[::2],
                                move_specs[1::2], fillvalue=""))
            half_moves = len(move_specs)
        self.total_half_moves = half_moves
        num_pair = len(move_pairs)    
        SlTrace.lg(f"{num_pair=}")
        # Create the grid widget
        self.grid = wx.grid.Grid(self)
        gf = self.grid.GetDefaultCellFont()
        gf.SetPointSize(18)
        self.grid.SetDefaultCellFont(gf)
        
        # Initialize a grid with move+1 rows and 3 columns
        self.grid.CreateGrid(num_pair+1, 3)
        self.grid.HideRowLabels()
        self.grid.HideColLabels()
        
        for nr in range(num_pair+1):    # beginning + num_pair
            if nr == 0:
                self.grid.SetCellValue(0, 0, "-")
            else:
                self.grid.SetCellValue(nr, 0, str(nr))
                self.grid.SetCellValue(nr, 1, move_pairs[nr-1][0])
                self.grid.SetCellValue(nr, 2, move_pairs[nr-1][1])
        self.grid.AutoSize()
        self.grid.EnableEditing(False)        
        # Make a specific cell read-only as an example
        #self.grid.SetReadOnly(2, 2, True)
        
        # Auto-size columns to fit the content perfectly
        self.grid.AutoSizeColumns()
        
        
        
        # Center the window on the screen
        #self.Center()
        # Bind cell selection
        
    def on_close_window(self, event):
        SlTrace.lg("wx_chess_goto_move.py: on_close_window")
        self.Destroy()

    def DoSetGridCursor(self, irow, icol):
        """ Force visible cell after
        SetGridCursor
        :irow: row starting with 0 for beginning
        :icol: col startgin with 0 for move_no
        """
        SlTrace.lg(f"DoSetGridCursor({irow=}, {icol=})")
        self.grid.SetGridCursor(irow, icol)
        self.grid.SetSelectionForeground(wx.BLACK)
        self.grid.SetSelectionBackground(wx.Colour((173, 216, 230)))
        # Explicitly create a selection block on this single cell
        self.grid.SelectBlock(irow, icol, irow, icol) 
        self.grid.Refresh()
        self.grid.MakeCellVisible(irow, icol)

    def simulate_key_down(self, ch):
        """ Simulate key down
        :ch: char string char to simulate key_down
        """
        self.grid.SetFocus()
        sim = wx.UIActionSimulator()
        sim.Char(ord(ch.upper()))

        
if __name__ == "__main__":
    import pgn
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
    pgn_games = pgn.loads(demo_game_text)
    demo_game = pgn_games[0]

    
    def on_move_change(move_no=None, moved=None):
        """ Called on move changes
        :move_no: move number 0-beginning,
        :moved: color moved "white"/"black"
        """
        if move_no == 0:
            SlTrace.lg("on_move_change: Beginning")
            return
        SlTrace.lg(f"on_move_change: {move_no=} {moved=}")
    
    class ChessGameDisplay:
        def on_gtm_move_changed(self, move_no,
                                moved):
            """ Called on chess goto move command
            :move_no: move_no
            :moved: white/black
            """
            SlTrace.lg(f"ChessGameDisplay recieved:"
                       f"{move_no=}, {moved=}")
        
    app = wx.App()
    cgd = ChessGameDisplay()
    gtm = ChessGotoMove(cgd, game=demo_game,
                on_move_change=cgd.on_gtm_move_changed)
    
    gtm.set_move(5, moved="black")
    gtm.set_half_move_relative(1, ignore_select=True)
    #gtm.Show()
    app.MainLoop()
