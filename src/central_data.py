#central_data.py    17Aug2026  crs, Author
# Central settings to coordinate game status
from graphics_braille.select_trace import SlTrace

class CentralData:
    def __init__(self, cgd=None, ccs=None, cgm=None, move_index=0):
        """ Centralized game state, on which all displays work
        :move_index: game move index,0 - before first move_index
        :cgd: (ChessGameDisplay) - Board Display, control, central part
        :ccs: (ChessCentralShow) - Main show and control logic, e.g., move parsing
        :cgm: (ChessGotoMove) - Move list display/control
                    Must be set before any movement, via self.set_cgm
        :move_index: initialize base board state
        """
        self.cgd = cgd
        self.ccs = ccs
        self.cgm = cgm      # Setting may be delayed till cgm is created
        self.move_index = move_index

    def set_cgm(self, cgm):
        self.cgm = cgm
            
    def set_move_index(self, move_index=0, update_display=True, source="cgd"):
        """ Set new move_index
        :move_index: board move index
        :update_display: update all displays default:True
        :source: source of command  default: cgd (ChessGameDisplay)
        :returns: new move_index if OK, else -1
        """
        new_index = move_index
        if move_index >= self.cgd.move_index:
            new_index = self.ccs.update_board_state_for_goto_move_index(move_index)
        if new_index >= 0:
            self.move_index = move_index
        if update_display:
            self.update_display(source=source)
        return new_index
        
    def set_move_index_relative(self, index_adj=1,
                                update_display=True, source="cgd"):
        """ Adjust move_index relative to current index
        :index_adj: board move index adjustment 1-forward by 1
        :update_display: update all displays default:True
        :source: source of command  default: cgd (ChessGameDisplay)
        """
        new_index = index_adj + self.get_move_index()
        return self.set_move_index(move_index=new_index,
                                   update_display=update_display,
                                   source=source) 
        
    def get_move_index(self):
        """ Get centralized move_index
        :returns: centralized move index
        """
        return self.move_index

    """
    centralized functions to set/get action/state
    """
    def exit(self, source="cgd"):
        """ exit
        For now just bring down cgd
        """
        if source != "cgd":
            self.cgd.exit()

    def chess_move(self, source="cgd"):
        """ Do chess move, updating state and notifying all parties
        returning new move_index
        """
        return self.set_move_index_relative(index_adj=1,
                            source=source)

    def chess_unmove(self, source="cgd"):
        """ Do chess unmove, updating state and notifying all parties
        """
        return self.set_move_index_relative(index_adj=-1,
                            source=source)

    def chess_loop(self, source="cgd"):
        """ Do chess loop
        """
        self.cgd.cmd_btn_loop()

    def chess_stop(self, source="cgd"):
        """ Do chess loop stop, updating state and notifying all parties
        """
        self.cgd.cmd_btn_stop(self, source="cgd")

    def chess_goto_move(self, move_no, moved="white", source="cgd"):
        """ Do chess move, updating state and notifying all parties
        """
        new_move_index = self.ccs.update_board_state_for_goto_move(move_no, moved=moved)
        if new_move_index >= 0:
            self.set_move_index(new_move_index, source=source)

    def on_key_down(self, event):
        """ Centralized distribution for key events
        :event: """
        self.cgm.on_key_down(event)
        
    def restart_game(self, source="cgd"):
        """ Restart chess game
        """
        self.chess_goto_move(0, source=source)
        
    def update_display(self, source="cgd"):
        """ Update all displays
        """
        self.cgd.display_board()
        if source != "cgm":
            if self.cgm is not None:
                self.cgm.update_display(source=source)
            else:
                SlTrace.lg("cgm not setup yet")
