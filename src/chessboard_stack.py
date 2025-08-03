#chessboard_stack.py    28Feb2025  crs, Author
""" 
Provides a stack of chessboards (Chessboard)
to facilitate such things as undo,redo game branching
"""
import copy

from chessboard import Chessboard
from chess_move import ChessMove

class ChessboardStack:
    def __init__(self):
        self.board_stack = []
        self.cur_bd_index = -1      # Reference to current board in stack
                                # < 0 ==> no current board

        

    def push_bd(self, bd=None):
        """ Push board onto board stack
        :bd: board to push
            default: push current board
        :returns: copy of bd
        """
        if bd is None:
            bd = self.get_bd()
        self.board_stack.append(bd.copy())  # subsequent changs not seen
        self.cur_bd_index = len(self.board_stack)-1     # Point to last pushed
        return self.board_stack[self.cur_bd_index]
            
    def move_undo(self):
        """ Undo current move
        :returns: current board, None if can't undo
        """
        cb = self.get_bd(-1)
        if cb is None:
            return None
        
        self.cur_bd_index -= 1
        cm =  cb.get_move()    # board's latest move

        return cm
        
    def redo(self):
        """ Redo last undone move
        :returns: current board, None if can't redo
        """
        cb = self.get_bd(1)
        if cb is None:
            return None
        
        self.cur_bd_index += 1
        return cb.get_move()

    def set_cur_bd_index(self, index):
        """ Set current board index
        :index: board index
                0 - beginning
                Negative: from end, e.g. -1 last 
        """
        if index < 0:
            index = len(self.board_stack)-index
        self.cur_bd_index = index
                    
    def get_bd(self, back=None, index=None):
        """ Get board from board stack
        :back: going relative:
            0-current board
            < 0 previous/undo boards,
            > 0 future/redo boards
                default: get bd at cur_bd_index
        :index: base index
            default: current board index (cur_bd_index)
        :returns: board, None if none available at  this place
        """
        bd_index = self.get_bd_index(back=back, index=index)
        if bd_index is None:
            return None
                
        return self.board_stack[bd_index]
                    
    def get_bd_index(self, back=None, index=None):
        """ Get board index in stack
        :back: going relative:
            0-current board
            < 0 previous/undo boards,
            > 0 future/redo boards
                default: get bd at cur_bd_index
        :index: base index
            default: current board index (cur_bd_index)
        :returns: board, None if none available at  this place
        """
        if index is None:
            index = self.cur_bd_index
        if back is None:
            back = 0
        bd_index = index+back
        if bd_index < 0:
            return None
        
        if bd_index > len(self.board_stack)-1:
            return None
        
        return bd_index

    def get_move_desc(self, back=None):
        """ Get move descriptor / title
            AFTER move has been made (i.e., in title of board display)
            We use the push down boards to get states before the move
            <move_no>: <white move spec>
                OR
            <move_no>: <white move spec> <black move spec>
        """
        # looking before the make_move update
        cb = self.get_bd(back=back)
        cm = cb.get_move()  # ChessSaveUnit
        if cm is not None:
            move_spec = cm.spec
            move_no = cm.get_move_no()
            to_move = cm.get_to_move()
            desc = f"{move_no}:"
            if to_move == "black":
                cm_w = self.get_move(-1)
                if cm_w is not None:
                    white_spec = cm_w.spec
                    desc += f" {white_spec}"
            desc += f" {move_spec}"
        else:
            desc = "Begin Game"
        return desc
    
    def copy(self):
        """ Copy chess stack
        :returns: copy of stack
        """
        new_cbs = copy.copy(self)
        new_cbs.board_stack = self.board_stack[:]
        return new_cbs
    
    """ 
    Operations on current board
    """
    
    def get_err_count(self):
        cb = self.get_bd()
        if cb is None:
            return 0
        
        return cb.get_err_count()
        

    def standard_setup(self):
        cb = self.get_bd()
        if cb is None:
            return None
        
        cb.standard_setup()
                
    def get_move(self, rel=0):
        """ Get game move
        :rel: relative to current move
        :returns: move, None if none
        """
        cb = self.get_bd(rel)
        if cb is None:
            return None     

        return cb.get_move()
    
    def get_move_no(self, rel=0):
        """ Get current move no
        :rel:  releative to current default: current
        """
        cb = self.get_bd()
        if cb is None:
            return 0
        
        return cb.get_board_no()
    
    def move_redo(self):
        """ Backup one move
        :returns: previous move, None if none
        """
        cb = self.get_bd(1)
        if cb is None:
            return None
        
        self.cur_bd_index += 1
        return self.get_move()     

  
