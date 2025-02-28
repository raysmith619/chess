# chessboard_display.py 11Feb2025  crs recover from _OLD
import re
        
import tkinter as tk
import tkinter.font
import sys
import copy

from select_trace import SlTrace
from chess_piece_images import ChessPieceImages
 
class ChessboardDisplay:
    window_list = []    # list of tuples (title, ChessboardDisplay)
                        # in the order created
    window_current = 0  # current choice index
    def __init__(self,
                 board,
                 mw = None,
                 sq_size = 80,
                 light_sq = "#fc9",        # tan
                 dark_sq = "#a65",         # brown
                 #light_sq = "#ffffff",      # white
                 #dark_sq = "#769656",       # green
                 title=None,
                ):
        self.board = board
        if mw is None:
            mw = tk.Tk()
        self.mw = mw
        self.sq_size = sq_size
        self.light_sq = light_sq
        self.dark_sq = dark_sq
        self.title = title
        self.setup_board_canvas(self.mw)
        self.setup_chess_piece_Images()
        self.chess_piece_images = ChessPieceImages()
        ChessboardDisplay.window_list.append(self)
        self.mw.bind('<KeyPress>', self.on_key_press)
        self.on_cmd = None          # To hold user display command processor

    def set_cmd(self, on_cmd):
        """ Setup cmd link
        :on_cmd: cmd(input) cmd
        :returns: previous on_cmd
        """
        old_cmd = self.on_cmd
        self.on_cmd = on_cmd
        return old_cmd
    
    """
    Capture std keyboard key presses
    and redirect they to input
    """
    def on_key_press(self, event):
        keysym = event.keysym
        self.buttonClick(input=keysym)


    # function for button click
    def buttonClick(self, input):
        if self.on_cmd is not None:
            self.on_cmd(input)

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
        self.rank_font = tk.font.Font(size=-int(.2*self.sq_size))



    def mainloop(self):
        """ Do mainloop
        """
        while True:
            self.mw.update()
            
            
    
    def update(self):
        """ Do update, allowing graphics to update
        """
            
    def display_board(self, title=None,
                      include_pieces=True):
        self.mw.update()
        """ Display board
        :title: board title - placed on window
        :include_pieces: include board pieces in display
            default: True - show pieces
        """
        if title is None:
            title = self.title
        self.title = title
        self.include_pieces = include_pieces    
        if title is None:
            title = self.title
        self.mw.title(title)
            
        self.setup_menus()
            
            
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

    def setup_menus(self):
        """ Setup menus
        """
        # creating a menu instance
        menubar = tk.Menu(self.mw)
        self.menubar = menubar      # Save for future reference
        self.mw.config(menu=menubar)

        # create the file object)
        file_open_cmd = self.file_open
        if file_open_cmd is None:
            file_open_cmd = self.File_Open_tbd
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=file_open_cmd)
        file_save_cmd = self.file_save
        if file_save_cmd is None:
            file_save_cmd = self.File_Save_tbd
        filemenu.add_command(label="Save", command=file_save_cmd)
        filemenu.add_separator()
        filemenu.add_command(label="Log", command=self.LogFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.pgmExit)
        menubar.add_cascade(label="File", menu=filemenu)
                                # Trace control
        menubar.add_command(label="Windows", command=self.show_window)
        self.mw.bind( '<Configure>', self.win_size_event)


    def show_window(self):
        windows_d = {}     # windows by title
        windows_options = []
        for wt in ChessboardDisplay.window_list:
            win_cbd = wt
            win_title = win_cbd.title
            windows_options.append(win_title) 
            windows_d[win_title] = win_cbd
              
        win_variable = tk.StringVar(self.mw)
        win_variable.set(windows_options[0]) # default value

        w = tk.OptionMenu(self.mw, win_variable, *windows_options)
        w.pack()

        def ok():
            win_title = win_variable.get()
            print ("window title is:" + win_title)
            win_cbd = windows_d[win_title]
            win_cbd.mw.lift()
             
        button = tk.Button(self.mw, text="OK", command=ok)
        button.pack()
        
        
    def win_size_event(self, e):
        pass
    
    def pgmExit(self):
        code = 0
        sys.exit(code) 
        
    def file_open(self):
        raise Exception("Not yet implemented")

    def file_save(self):
        raise Exception("Not yet implemented")

    def LogFile(self):
        raise Exception("Not yet implemented")

    def move_control(self):
        raise Exception("Not yet implemented")
                        
    def display_pieces(self, piece_squares=None, title=None):
        """ Display pieces
        erase all displayed pieces tags="piece_tags"
        :title: updated title     
        :piece_squares: list of piece_squares to display
            default: use board.setting
        """
        if title is None:
            title = self.title
        self.title = title
        self.mw.title(title)
        self.canvas.delete("piece_tags")
        if piece_squares is None:
            piece_squares = self.board.get_pieces()
        for ps in piece_squares:
            self.display_piece_square(ps)

    def display_piece_square(self, ps):
        """ Display piece in square
        tag piece items with "piece_tags"
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
            self.canvas.create_image(c_x, c_y, anchor=tk.CENTER, image=photo, tags="piece_tags")

        else:
            err = f"Unrecognized piece-square: {ps}"
            SlTrace.lg(err)
            raise Exception(err)

    def setup_chess_piece_Images(self):
        """ Setup the piece images, currently size fixed
        """
        self.cpi = ChessPieceImages()
        piece_images = self.cpi.get_image_dict()
        self.piece_images = copy.copy(piece_images)

if __name__ == '__main__':
    import  tkinter as tk
    
    from select_trace import SlTrace
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    
        
    SlTrace.clearFlags()
    mw1 = tk.Tk()   # Controlling window
    pieces_list = [
        'FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
        ':Kc1Qe1kh7 w',
    ]
    for pieces in pieces_list: 
        mw2 = tk.Toplevel()     # Subsequent window
        cb2 = Chessboard(pieces=pieces)
        cbp = ChessboardPrint(cb2)
        cbp.display_board()
        cbd = ChessboardDisplay(cb2, mw=mw2,title=f"pieces={pieces}")
        cbd.display_board()
    mw2.mainloop()
