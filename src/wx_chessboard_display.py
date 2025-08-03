#wx_chessboard_display.py    05Apr2025  crs, Author, from chessboard_display.py __init__
""" Chessboard display, using basic wxPython
"""
import re

import wx

from select_trace import SlTrace
from wx_chess_piece_images import ChessPieceImages

            
""" Setup the piece images, currently size fixed
"""
class ChessboardDisplay(wx.Frame):
    
    def __init__(self,
                 cbs,
                 parent=None,   # prepended to *args list
                 title = None,
                 sq_size = 80,
                 nsqx = 8,
                 nsqy = 8,
                 light_sq = "#fc9",        # tan
                 dark_sq = "#a65",         # brown
                 #light_sq = "#ffffff",      # white
                 #dark_sq = "#769656",       # green
                 **kwargs,       # passed to wx.Frame                 
                ):
        """ Create new chessboard display
        :cbs:  chessboard stack (ChessboardStack)
        :parent: Frame parent default: None passed to Frame
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
        self.cbs = cbs
        self.base_bd_index = cbs.get_bd_index()   # Initial index
        super().__init__(parent, **kwargs)

        self.InitUI(
            title = title,
            sq_size = sq_size,
            nsqx = nsqx,
            nsqy = nsqy,
            light_sq = light_sq,        # tan
            dark_sq = dark_sq,         # brown            
            )

    def InitUI(self,
        parent = None,
        title = None,
        sq_size = 80,
        nsqx = 8,
        nsqy = 8,
        light_sq = "#fc9",        # tan
        dark_sq = "#a65",         # brown
        ):
        self.parent = parent
        self.title = title
        self.sq_size = sq_size
        self.nsqx = nsqx
        self.nsqy = nsqy
        self.light_sq= light_sq
        self.dark_sq = dark_sq
        brt = 245
        self.background = wx.Colour(brt,brt,brt)
        border_size = self.sq_size//2
        bd_width = self.nsqx*self.sq_size+2*border_size
        bd_height = self.nsqy*self.sq_size+2*border_size+border_size
        self.SetInitialSize(wx.Size(bd_width, bd_height))
        #self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.SetBackgroundColour( self.background )
        self.cpi = ChessPieceImages()       # Must come after default window setup
        self.pieces = []        # piece-squares if any
        #self.SetTitle("wxPython Canvas shapes")
        self.Centre()
        self.Show()

    '''
    def OnResize(self, e):
        width,height = self.GetClientSize()
        self.width = width
        self.height = height
        self.Refresh()        
    '''

    def OnPaint(self, e):
        """ Draw board
        """
        dc = wx.PaintDC(self)
        self.SetBackgroundColour(self.background)
        self.squares_bounds = []         # square bounds array [ic][ir]
        border_size = self.sq_size//2
        x_left = border_size    ### - self.sq_size//2
        y_top = border_size  -   self.sq_size//2        
        y_bot = y_top + self.nsqy*self.sq_size   # y increases downward
        bd_width = int(self.nsqx*self.sq_size+2*border_size)
        bd_height = int(self.nsqy*self.sq_size+2*border_size+2*border_size)
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
            #self.chess_pan.clear(refresh=True) # Remove after display
            self.display_pieces(dc, piece_squares=piece_squares)

    def get_pieces(self):
        """ Get current chess board
        Uses chessboard stack
        """
        board = self.cbs.get_bd(index=self.base_bd_index)
        if board is not None:
            return board.get_pieces()
        else:
            return []

                        
    def display_pieces(self, dc, title=None, piece_squares=None):
        """ Display pieces CALLED from OnPaint
        erase all displayed pieces tags="piece_tags"
        :dc: wx.PaintDC(self) - device context
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
            self.display_piece_square(dc, ps)

    def display_piece_square(self, dc, ps):
        """ Display piece in square
        tag piece items with "piece_tags"
        :dc: wx.PaindDC(self)  - device context
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
            bitmap = self.cpi.get_piece_bitmap(piece, width=self.sq_size,
                                               height=self.sq_size )            
            dc.DrawBitmap(bitmap, c_x, c_y)

        else:
            err = f"Unrecognized piece-square: {ps}"
            SlTrace.lg(err)
            raise Exception(err)
                
        

if __name__ == '__main__':
    from select_trace import SlTrace

    from chessboard_stack import ChessboardStack
    from chessboard_print import ChessboardPrint
    from chessboard import Chessboard
    from wx_cgd_menus import CgdMenus
    
    app = wx.App()
        
    SlTrace.clearFlags()
    cbs = ChessboardStack()
    
    pieces_list = [
        'FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        ':Kc1Qe1kh7 w',
    ]
    cbs = ChessboardStack()
    cbds = []
    fpos_x = 200
    fpos_y = 200
    fpos_x_inc = 700
    fpos_y_inc = 100
    for pieces in pieces_list:
        frame = wx.Frame(None, pos=(fpos_x, fpos_y))
        fpos_x += fpos_x_inc
        fpos_y += fpos_y_inc 
        cb = Chessboard(pieces=pieces)
        cbs.push_bd(cb)
        cbp = ChessboardPrint(cb)
        cbp.display_board()
        cbd = ChessboardDisplay(cbs, parent=frame, title=f"pieces={pieces}")
        cbds.append(cbd)
        bd_pieces = cb.get_pieces()
        SlTrace.lg(f"After pieces={bd_pieces}")
        cbd.Refresh()
        cbd.Show()
        pass
    app.MainLoop()
