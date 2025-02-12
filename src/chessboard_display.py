# chessboard_display.py 11Feb2025  crs recover from _OLD
import re
        
import tkinter as tk
import tkinter.font
from chess_piece_images import ChessPieceImages
 
class ChessboardDisplay:
    def __init__(self,
                 board,
                 sq_size = 80,
                 light_sq = "#fc9",        # tan
                 dark_sq = "#a65",         # brown
                 #light_sq = "#ffffff",      # white
                 #dark_sq = "#769656",       # green
                ):
        self.board = board
        self.sq_size = sq_size
        self.light_sq = light_sq
        self.dark_sq = dark_sq

    def setup_board_canvas(self, mw):
        """ Setup board frame, canvas
        :mw: main window
        """
        board = self.board
        border_thickness = self.sq_size//2
        board_frame = tk.Frame(mw, bg="red")
        board_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        board_squares_frame = tk.Frame(board_frame)
        board_squares_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        
        bd_width=self.sq_size*board.nsqx + 2*border_thickness
        bd_height=self.sq_size*board.nsqy + 2*border_thickness + 2*border_thickness  # fudge
        canvas = tk.Canvas(board_squares_frame, width=bd_width, height=bd_height)
        canvas.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        self.canvas = canvas
        self.chess_piece_images = ChessPieceImages()
        self.rank_font = tk.font.Font(size=-int(.2*self.sq_size))

    def mainloop(self):
        """ Do mainloop
        """
        while True:
            self.mw.update()
            
            
    
    def update(self):
        """ Do update, allowing graphics to update
        """
        self.mw.update()
            
    def display_board(self, mw=None, include_pieces=True):
        """ Display board
        """
        self.include_pieces = include_pieces    
        if mw is None:
            mw = tk.Tk()
        self.mw = mw
        self.setup_board_canvas(mw)
        self.setup_chess_piece_Images()
        squares_bounds = []         # square bounds array [ic][ir]
        board = self.board
        border_size = self.sq_size//2
        x_left = border_size
        y_top = border_size        
        y_bot = y_top + board.nsqy*self.sq_size   # y increases downward
        # Example: canvas.create_rectangle(ul_cx1,ul_cy1, lr_cx2,lr_cy2, ...)
        for ic in range(board.nsqx):     # index col left to right
            sb_col = []
            for ir in range(board.nsqy): # index row bottom to top
                ul_cx1 = x_left + ic*self.sq_size
                ul_cy1 = y_bot - ir*self.sq_size
                lr_cx2 = ul_cx1 + self.sq_size 
                lr_cy2 = ul_cy1 + self.sq_size
                sq_color = self.dark_sq if (ic+ir)%2==0 else self.light_sq
                self.canvas.create_rectangle(ul_cx1, ul_cy1, lr_cx2, lr_cy2, fill=sq_color)
                sq_bounds = (ul_cx1, ul_cy1, lr_cx2, lr_cy2)
                rank_label_cx = x_left - border_size/2
                rank_label_cy = (lr_cy2+ul_cy1)//2
                self.canvas.create_text(rank_label_cx, rank_label_cy,
                                        text=str(ir+1), font=self.rank_font)
                sb_col.append(sq_bounds)    # Add next row to up
                SlTrace.lg(f"{ic} {ir} self.canvas.create_rectangle("
                           f"x1:{ul_cx1},y1:{ul_cy1},x2:{lr_cx2},y2:{lr_cy2}, fill={sq_color})",
                           "build_display")
            file_label_cx = (ul_cx1+lr_cx2)//2
            file_label_cy = y_bot + self.sq_size + border_size//2
            file_label = chr(ord('a')+ic)
            self.canvas.create_text(file_label_cx, file_label_cy,
                                    text=file_label, font=self.rank_font)
            squares_bounds.append(sb_col)   # Add next column to right
        self.squares_bounds = squares_bounds
        if include_pieces:
            self.display_pieces()
            
    def display_pieces(self, piece_squares=None):
        """ Display pieces
        :piece_squares: list of piece_squares to display
            default: use board.setting
        """
        if piece_squares is None:
            piece_squares = self.board.get_board_pieces()
        for ps in piece_squares:
            self.display_piece_square(ps)

    def display_piece_square(self, ps):
        """ Display piece in square
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
            c_x = (ul_cx1+lr_cx2)//2
            c_y = (ul_cy1+lr_cy2)//2
            photo = self.piece_images[piece]
            self.canvas.create_image(c_x, c_y, anchor=tk.CENTER, image=photo)

        else:
            err = f"Unrecognized piece-square: {ps}"
            SlTrace.lg(err)
            raise Exception(err)

    def setup_chess_piece_Images(self):
        """ Setup the piece images, currently size fixed
        """
        self.cpi = ChessPieceImages()
        self.piece_images = self.cpi.get_image_dict()

if __name__ == '__main__':
    import  tkinter as tk
    
    from select_trace import SlTrace
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    
        
    SlTrace.clearFlags()
    test = 2
    if test == 1:
        cb = Chessboard(pieces='FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        cbp = ChessboardPrint(cb)
        cbp.display_board()
        cbd = ChessboardDisplay(cb)
        cbd.display_board()
    
    if test == 2:
        cb = Chessboard(pieces=':Kc1Qe1kh7 w')
        cbp = ChessboardPrint(cb)
        cbp.display_board()
        cbd = ChessboardDisplay(cb)
        cbd.display_board()
    cbd.mainloop()