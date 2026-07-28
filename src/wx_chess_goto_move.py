import wx
import wx.grid

from graphics_braille.select_trace import SlTrace

from chess_move_notation import ChessMoveNotation

"""
Game of the Century
From https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
[Event "Third Rosenwald Trophy"]
[Site "New York, NY USA"]
[Date "1956.10.17"]
[EventDate "1956.10.07"]
[Round "8"]
[Result "0-1"]
[White "Donald Byrne"]
[Black "Robert James Fischer"]
"""    
test_moves = """
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

class ChessGotoMove(wx.Frame):
    def __init__(self,
                 moves=None,
                 on_move_change=None):
        """ Setup goto move window
        :moves: moves string default: test_moves
        :on_move_change: called with new move_no, moved
                default: no call
        """
        super().__init__(None, title="Chess Goto", size=(150, 300))
        if moves is None:
            moves = test_moves
        self.on_move_change = on_move_change
        self.move_specs = ChessMoveNotation.game_to_specs(moves)
        move_pairs = []
        move_pair = []
        for move_spec in self.move_specs:
            if len(move_pair) > 1:
                move_pairs.append(tuple(move_pair))
                move_pair = []
            move_pair.append(move_spec)
                
        if len(move_pair) > 0:
            if len(move_pair) == 1:
                move_pair.append("")    # make a pair
            move_pairs.append(tuple(move_pair))
        
        num_pair = len(move_pairs)    
        SlTrace.lg(f"{num_pair=}")
                    
        # Create the grid widget
        self.grid = wx.grid.Grid(self)
        
        # Initialize a grid with 5 rows and 3 columns
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
                
        # Make a specific cell read-only as an example
        #self.grid.SetReadOnly(2, 2, True)
        
        # Auto-size columns to fit the content perfectly
        self.grid.AutoSizeColumns()
        
        
        
        # Center the window on the screen
        self.Center()
        # Bind cell selection
        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_select)
        
    def on_cell_select(self, event):
        irow = event.GetRow()
        icol = event.GetCol()
        SlTrace.lg(f"Selected cell at Row: {irow}, Col: {icol}", "all_time")
        move_no = irow
        moved = "black" if icol == 2 else "white"
        if self.on_move_change is not None:
            self.on_move_change(move_no=move_no, moved=moved)
            
        # Always call Skip() so the grid updates normally
        event.Skip()


    def set_move(self, move_no=0, moved="white"):
        """ Set move display
        :move_no: move number 0 - beginning, else recent move
        :moved: who "white", "black"
        """
        if moved == "white":
            icol = 1
        else:
            icol = 2
            
        self.grid.SetGridCursor(move_no, icol)
        
if __name__ == "__main__":
    def on_move_change(move_no=None, moved=None):
        """ Called on move changes
        :move_no: move number 0-beginning,
        :moved: color moved "white"/"black"
        """
        if move_no == 0:
            SlTrace.lg("Beginning")
            return
        SlTrace.lg(f"{move_no=} {moved=}")
        
    app = wx.App()
    gtm = ChessGotoMove(on_move_change=on_move_change)
    gtm.set_move(5, moved="black")
    gtm.Show()
    app.MainLoop()
