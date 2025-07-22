#wx_chessboard_panel.py    13Apr2025  crs, Author, from chessboard_display.py __init__
""" Chessboard display, using basic wxPython
"""
import re

import wx

from select_trace import SlTrace
from wx_canvas_panel import CanvasPanel

from wx_chess_piece_images import ChessPieceImages

            
""" Setup the piece images, currently size fixed
"""
class ChessboardPanel(CanvasPanel):
    
    def __init__(self,
                 parent=None,   # prepended to *args list
                 app = None,
                 title = None,
                 board = None,
                 sq_size = 80,
                 nsqx = 8,
                 nsqy = 8,
                 light_sq = "#fc9",        # tan
                 dark_sq = "#a65",         # brown
                 #light_sq = "#ffffff",      # white
                 #dark_sq = "#769656",       # green
                 color=None,
                 key_press_proc=None,                 
                 **kwargs,       # passed to wx.Frame                 
                ):
        """ Create new chessboard display
        :parent: Frame parent default: None passed to Frame
        :app: applicatin ref
                default: pass to base
        :board: chessboard default: None
        :sq_size: square size, in pixels
                default: 80
        :nsqx: Number of squares(columns) in x direction
                default: 8
        :nsqy: Number of squares(rows) in y direction
                default: 8
        :light_sq: Color of light squares
                default: "#fc9" (tan) tan
        :dark_sq: Color of dark squares
                default: "#a65" (brown)
        """
        brt = 245
        self.background = wx.Colour(brt,brt,brt)
        self.title = title
        self.board = board
        self.sq_size = sq_size
        self.nsqx = nsqx
        self.nsqy = nsqy
        self.light_sq= light_sq
        self.dark_sq = dark_sq
        border_size = self.sq_size//2
        bd_width = self.nsqx*self.sq_size+2*border_size
        bd_height = self.nsqy*self.sq_size+2*border_size+border_size
        self.cpi = ChessPieceImages()       # Must come after default window setup
        super().__init__(parent, app=app, color=color,
                         key_press_proc=key_press_proc,
                         **kwargs)
        self.SetInitialSize(wx.Size(bd_width, bd_height))
        self.SetBackgroundColour( self.background )
        
        if parent is None:
            parent = wx.Frame(None)

        self.parent = parent
        self.grid_panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Refresh()

    
    def get_piece_bitmap(self, piece, width=None, height=None):
        """ Get bitmap of piece (rnbkqpRNBKQP)
        :piece: rnbkqpRNBKQP
        :returns: photo bitmap
        :width: width of piece in pixels
            default: no scaling
        :height: height of piece in pixels
            default: no scaling
        """
        if not hasattr(self, "cpi"):
            SlTrace.lg("cpi attr missing")
            return None
        
        return self.cpi.get_piece_bitmap(piece, width=width,
                                         height=height)
        
    def display_items(self):
        """ Make items displayable
        """
        ### TFD add items to pending
        for item in self.items:
            self.add_item(item)
        
        
    def get_pieces(self):
        """ Get current chess board
        Uses chessboard stack
        """
        if self.board is not None:
            return self.board.get_pieces()
        else:
            return []

                        
    def display_pieces(self, title=None, piece_squares=None):
        """ Display pieces CALLED from OnPaint
        Adds pieces (bitmaps) to pannel
        erase all displayed pieces tags="piece_tags"
        :title: updated title     
        :piece_squares: list of piece_squares to display
            default: use board.setting
        """
        if title is None:
            title = self.title
        self.title = title
        #if self.err_count > 0:
        #    title = f"ERRORS: {self.err_count} {title}"
        #self.mw.title(title)

        if piece_squares is None:
            piece_squares = self.get_pieces()
        for ps in piece_squares:
            self.display_piece_square(ps)
        ### TFD add items to pending
        #for item in self.items:
        #    self.add_item(item)

    def display_piece_square(self, ps):
        """ Display piece in square
        tag piece items with "piece_tags"
        :dc: wxPaintDC device context
        :ps: piece-square e.g. Ke8 is black King in original square e8
        """            
        if match := re.match(r'([KQRBNPkqrbnp])([a-h])([1-8])', ps):
            piece = match.group(1)
            sq_file = match.group(2)
            sq_rank = match.group(3)
            ic = ord(sq_file)-ord('a')
            ir = int(sq_rank)-1
            sq_bounds = self.squares_bounds[ic][ir]
            ul_cx1, ul_cy1, lr_cx2, lr_cy2 = sq_bounds
            c_x = (ul_cx1+lr_cx2)//2  - self.sq_size//2      ### ??? Fudge
            c_y = (ul_cy1+lr_cy2)//2  - self.sq_size//2      ### ??? Fudge
            bitmap = self.get_piece_bitmap(piece, width=self.sq_size,
                                               height=self.sq_size )
            
            item = self.create_bitmap(ul_cx1, ul_cy1,
                               lr_cx2, lr_cy2, bitmap=bitmap,
                               desc=ps)
            self.add_item(item)
        else:
            err = f"Unrecognized piece-square: {ps}"
            SlTrace.lg(err)
            raise Exception(err)
                

    def OnPaint(self, e):
        rect = self.GetClientRect()
        cv_width = rect.GetWidth()
        x_min = cv_width*.05
        x_max = cv_width*.95
        bd_width = width = x_max-x_min
        
        cv_height = rect.GetHeight() 
        y_min = cv_height*.05       # tk .1 ???
        y_max = cv_height*.95
        bd_height = height = abs(y_max-y_min)
        bd_size = min(width, height)
        sq_size = bd_size/(self.nsqx+1) # Border == sq/2
        self.sq_size = sq_size
        border_size = sq_size/2
        """ Draw board
        """
        dc = wx.PaintDC(self.grid_panel)
        self.SetBackgroundColour(self.background)
        self.squares_bounds = []         # square bounds array [ic][ir]
        x_left = border_size    ### - self.sq_size//2
        y_top = border_size     ### - self.sq_size//2        
        y_bot = y_top + self.nsqy*self.sq_size   # y increases downward
        # Example: canvas.create_rectangle(ul_cx1,ul_cy1, lr_cx2,lr_cy2, ...)
        for ic in range(self.nsqx):     # index col left to right
            sb_col = []
            for ir in range(self.nsqy): # index row bottom to top
                ul_cx1 = int(x_left + ic*self.sq_size)
                ul_cy1 = int(y_bot - (ir+1)*self.sq_size)
                lr_cx2 = int(ul_cx1 + self.sq_size) 
                lr_cy2 = int(ul_cy1 + self.sq_size)
                sq_color = self.dark_sq if (ic+ir)%2==0 else self.light_sq
                dc.SetPen(wx.Pen(sq_color, style=wx.SOLID))
                dc.SetBrush(wx.Brush(sq_color, wx.SOLID))
                rect = wx.Rect(wx.Point(ul_cx1, ul_cy1), wx.Point(lr_cx2, lr_cy2))
                dc.DrawRectangle(rect)
                sq_bounds = (ul_cx1, ul_cy1, lr_cx2, lr_cy2)
                sb_col.append(sq_bounds)    # Add next row to up
                rank_font = wx.Font(wx.FontInfo(12))
                dc.SetFont(rank_font)
                rank_label = str(ir+1)
                rank_w,rank_h = dc.GetTextExtent(rank_label)
                rank_label_cx = int(x_left - border_size/2 - rank_w/2)
                rank_label_cy = int((lr_cy2+ul_cy1)//2 -5)
                dc.SetPen(wx.Pen(sq_color, style=wx.SOLID))
                dc.SetBrush(wx.Brush(sq_color, wx.SOLID))
                dc.DrawText(text=rank_label,  pt=wx.Point(rank_label_cx, rank_label_cy))
                SlTrace.lg(f"{ic} {ir} self.DrawRectangle("
                           f"x1:{ul_cx1},y1:{ul_cy1},x2:{lr_cx2},y2:{lr_cy2}, fill={sq_color})",
                                "build_display")
                file_label_cx = int((ul_cx1+lr_cx2)//2)
                file_label_cy = int(y_bot + border_size/4)
                dc.SetFont(rank_font)
                file_label = chr(ord('a')+ic)
                dc.DrawText(text=file_label,  pt=wx.Point(file_label_cx, file_label_cy))
            self.squares_bounds.append(sb_col)   # Add next column to right
        piece_squares = self.get_pieces()
        if piece_squares:
            self.display_pieces(dc, piece_squares=piece_squares)
        #self.display_items()
        self.display_pending(dc)
        self.Show()
        #self.clear() # Remove after display
        pass
if __name__ == '__main__':
    from select_trace import SlTrace

    from chessboard_print import ChessboardPrint
    from chessboard import Chessboard
    from wx_cgd_menus import CgdMenus
    
    app = wx.App()
        
    SlTrace.clearFlags()
    pieces_list = [
        'FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        ':Kc1Qe1kh7 w',
    ]
    for pieces in pieces_list:
        side = 80*8+80*2
        frame = wx.Frame(None, size=wx.Size(side,side)) 
        cb = Chessboard(pieces=pieces)
        cbp = ChessboardPrint(cb)
        cbp.display_board()
        cbd = ChessboardPanel(parent=frame, title=f"pieces={pieces}", board=cb)
        SlTrace.lg(f"After pieces={pieces}")

    app.MainLoop()

    
    