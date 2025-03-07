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
        """
        if bd is None:
            bd = self.get_bd()
        self.board_stack.append(bd.copy())  # subsequent changs not seen
        self.cur_bd_index = len(self.board_stack)-1     # Point to last pushed
                
    def move_undo(self):
        """ Undo current move
        :returns: current board, None if can't undo
        """
        cb = self.get_bd(-1)
        if cb is None:
            return None
        
        self.cur_bd_index -= 1
        cm =  cb.get_move()    # board's latest move
        if cm is None:
            cm = ChessMove(cb)
            cm.desc = "End of Undo"
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
                    
    def get_bd(self, back=None):
        """ Get board from board stack
        :back: going relative:
            0-current board
            < 0 previous/undo boards,
            > 0 future/redo boards
                default: get bd at cur_bd_index
        :returns: board, None if none available at  this place
        """
        if back is None:
            back = 0
        bd_index = self.cur_bd_index+back
        if bd_index < 0:
            return None
        
        if bd_index > len(self.board_stack)-1:
            return None
        
        return self.board_stack[bd_index]
    
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
    
    def move_redo(self):
        """ Backup one move
        :returns: previous move, None if none
        """
        cb = self.get_bd(1)
        if cb is None:
            return None
        
        self.cur_bd_index += 1
        return self.get_move()     

  
        