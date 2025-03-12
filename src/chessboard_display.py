# chessboard_display.py 11Feb2025  crs recover from _OLD
""" Chess board and pieces display
Currently uses tkinter, with hopes to move to or support
wxPython, with its better supporting screen readers
for the blind
"""
import re
        
import tkinter.filedialog
import tkinter as tk

import tkinter.font
import sys
import os
import copy

import pgn


from select_trace import SlTrace
from select_trace import TraceError
from chess_piece_images import ChessPieceImages
 
class ChessboardDisplay:
    master = None
    window_list = []    # list of tuples (title, ChessboardDisplay)
                        # in the order created
    window_current = 0  # current choice index

    def setup_chess_piece_images(self):
        """ Setup the piece images, currently size fixed
        """
        self.cpi = ChessPieceImages()
        piece_images = self.cpi.get_image_dict()
        ChessboardDisplay.piece_images = dict(piece_images)
    
    def __init__(self,
                 board,
                 master = None,
                 sq_size = 80,
                 light_sq = "#fc9",        # tan
                 dark_sq = "#a65",         # brown
                 #light_sq = "#ffffff",      # white
                 #dark_sq = "#769656",       # green
                 title=None,
                 games_dir="../games",       # chess games directory
                 errors_dir="../errors",
                 scan_max_loops=None,
                 new_display=False,
                ):
        self.board = board
        if master is None:
            master = tk.Tk()
            master.withdraw()
            ChessboardDisplay.master = master
            mw = tk.Toplevel(self.master)
        self.mw = mw
        self.chess_piece_images = ChessPieceImages()
        self.setup_chess_piece_images()
        self.sq_size = sq_size
        self.light_sq = light_sq
        self.dark_sq = dark_sq
        self.title = title
        self.games_dir = games_dir
        self.setup_errors(errors_dir)
        self.errors_dir = errors_dir
        
        self.scan_file_name = None
        self.scan_max_loops = scan_max_loops
        self.scan_loops = 0
        self.scan_is_force_next_game = False     # True - abandon current game
        self.setup_board_canvas(self.mw)
        ChessboardDisplay.window_list.append(self)
        self.mw.bind('<KeyPress>', self.on_key_press)
        self.on_cmd = None          # To hold user display command processor
        self.loop_interval = 250    # game move display interval (msec)     
        self.sel_short_desc = None  # Set if game selected
        self.sel_game = None        # Set if game selected
        self.is_scanning = False     # True = Scanning files in progress
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
                ul_cy1 = y_bot - (ir+1)*self.sq_size
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
            file_label_cy = y_bot + border_size//2
            file_label = chr(ord('a')+ic)
            self.canvas.create_text(file_label_cx, file_label_cy,
                                    text=file_label, font=self.rank_font)
            squares_bounds.append(sb_col)   # Add next column to right
        self.squares_bounds = squares_bounds

    def setup_errors(self, errors_dir):
        """ Setup errors directory
        :errors_dir:
        """
        self.err_count = 0          # Count of errors      
        self.err_first = None       # first error, if any   
        self.err_first_move_no = 0  # first error move no
        directory = errors_dir
        self.errors_dir = errors_dir
        
        if not os.path.exists(directory):
            try:
                os.mkdir(directory)
            except:
                raise TraceError("Can't create errors directory %s"
                                     % directory)
                sys.exit(1)
        
            print("Error games Directory %s  created\n"
                  % os.path.abspath(directory))


    """ Setup keyboard/button commands
    """
    def move_cmd(self):
        """ Make move
        """
        self.buttonClick(input="n")
        
    def unmove_cmd(self):
        """ Unmakeake move
        """
        self.buttonClick(input="u")

    def stop_cmd(self):
        """ Restart game
        """
        self.buttonClick(input="p")

    def loop_cmd(self):
        """ Restart game
        """
        self.buttonClick(input="l")

    def start_looping(self, loop_fun, interval=None):
        """ Start looping
        :loop_fun: loop function to call at interval
        :interval: interval (msec) to call loop_fun
            default: leave interval unchanged
        """
        self.loop_fun = loop_fun
        if interval is not None:
            self.loop_interval = interval
        self.is_looping = True  # Cleared to stop loop
        self.mw.after(self.loop_interval, self.loop_call)

    def stop_looping(self):
        """ Stop looping
        Note we do not stop the current exececution.
        If the function is exceptionally long, the
        user can check the status of self.is_looping
        within the function, to effect an early exit.
        """
        self.is_looping = False
        
    def loop_call(self):
        """ Function to call users looping function
        """
        if self.is_looping:
            self.loop_fun()
        if self.is_looping:
            self.after_no_arg(self.loop_interval, self.loop_call)
                
        
        

        
    def restart_cmd(self):
        """ Restart game
        """
        self.buttonClick(input="t")
                
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
        move_ctl_frame = tk.Frame(mw, bg="lightgray", height=50)
        move_ctl_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        self.setup_ctl(move_ctl_frame)
        board_frame = tk.Frame(mw, bg="red")
        board_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        board_squares_frame = tk.Frame(board_frame)
        board_squares_frame.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        
        bd_width=self.sq_size*board.nsqx + 2*border_thickness
        bd_height=self.sq_size*board.nsqy + 2*border_thickness
        canvas = tk.Canvas(board_squares_frame, width=bd_width, height=bd_height)
        #canvas = tk.Canvas(board_squares_frame, width=bd_width, height=300)
        canvas.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH)
        self.canvas = canvas
        self.rank_font = tk.font.Font(size=-int(.2*self.sq_size))



    def mainloop(self):
        """ Do mainloop
        """
        while True:
            self.mw.update()
            
    def after(self, int_ms=0, cmd=None, arg=None):
        """ Call cmd after interval
        :int_ms: after this interval in msec
                default: as soon as possible
        :cmd: function to call
        :arg: argument to cmd
        """
        self.mw.after(int_ms, cmd, arg)    
            
    def after_no_arg(self, int_ms=0, cmd=None):
        """ Call cmd after interval with no arg
        :int_ms: after this interval in msec
                default: as soon as possible
        :cmd: function to call
        :arg: argument to cmd
        """
        self.mw.after(int_ms, cmd)    
    
    def update(self):
        """ Do update, allowing graphics to update
        """
        self.mw.update()
            
    def display_board(self, title=None,
                      cb=None,
                      include_pieces=True):
        self.mw.update()
        """ Display board
        :title: board title - placed on window
        :cb: chessboard
            default: use initial board
        :include_pieces: include board pieces in display
            default: True - show pieces
        """
        if title is None:
            title = self.title
        self.title = title
        self.include_pieces = include_pieces    
        if title is None:
            title = self.title
        if self.err_count > 0:
            title = f"ERRORS: {self.err_count} {title}"
        self.mw.title(title)
        if cb is None:
            cb = self.board
        self.board = cb
        if include_pieces:
            self.display_pieces()
    
    def err_add(self, msg=None):
        """ Set and Count errors
        :msg: count as error if msg != ""
            default: self.err - current parsing error message
        :returns: msg
        """
        if msg is None:
            msg = self.err
            
        if msg is not None and msg != "":
            self.err = msg
            self.err_count += 1
            if self.err_first is None:
                self.err_first_file_name = self.scan_file_name
                self.err_first_desc = self.sel_short_desc
                self.err_first_game = self.sel_game
                self.err_first = msg
        return msg    

    def error_show(self, desc=None):
        """ Show error
        if scanning, then go to next file
        """
        self.err_add(msg=desc)
        self.save_error_game(desc)
        if self.is_scanning:
            self.scan_force_next_game()
        SlTrace.lg("Continuing")    
        
    def setup_ctl(self, ctl_frame):
        """ Setup control buttons
        :ctl_frame: control Frame
        """
        button = tk.Button(ctl_frame, text="Move", command=self.move_cmd,
                        fg="green", bg="light gray")
        button.pack(side=tk.LEFT)
        
        button = tk.Button(ctl_frame, text="UnMove", command=self.unmove_cmd,
                        fg="red", bg="light gray")
        button.pack(side=tk.LEFT)

        button = tk.Button(ctl_frame, text="Stop", command=self.stop_cmd,
                        fg="red", bg="light gray")
        button.pack(side=tk.RIGHT)

        button = tk.Button(ctl_frame, text="Loop play", command=self.loop_cmd,
                        fg="green", bg="light gray")
        button.pack(side=tk.RIGHT)

        button = tk.Button(ctl_frame, text="Restart", command=self.restart_cmd,
                        fg="black", bg="light gray")
        button.pack(side=tk.RIGHT)
        
        
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
        filemenu.add_command(label="Save", command=self.file_save)
        filemenu.add_separator()
        filemenu.add_command(label="Log", command=self.LogFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.pgmExit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Files", command=self.scan_files_cmd)
        menubar.add_cascade(label="Scanning", menu=game_menu)
        
        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label="Loop_interval", command=self.loop_interval_cmd)
        menubar.add_cascade(label="Settings", menu=setting_menu)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Goto move", command=self.goto_move_cmd)
        game_menu.add_command(label="Print Game", command=self.print_game_cmd)
        menubar.add_cascade(label="Game", menu=game_menu)
        
        self.mw.bind( '<Configure>', self.win_size_event)


    def loop_interval_cmd(self):
        """ Set/change loop interval
        """
        from gr_input import gr_input
        
        interval = self.loop_interval
        new_val_str = gr_input("Loop interval(msec)", default=str(interval))
        print(f"{new_val_str = }")
        if new_val_str == "":
            return
        interval = int(new_val_str)
        self.loop_interval = interval

    move_index = 0        # move index from selection
    def goto_move_cmd(self):
        """ Select game move and go to it
        """
        game = self.sel_game
        if game is None:
            return
        
        move_descs = []     # Descs <#>  <white spec> OR <... black spec>
        moves = game.moves
        move_pairs = [(i,j) for i,j in zip(moves[::2], moves[1::2])]
        move_descs.append("Begin")
        move_no = 0
        for move_pair in move_pairs:
            move_no += 1
            move_desc = f"{move_no}: {move_pair[0]}"
            move_descs.append(move_desc)
            move_desc = f"{move_no}:   ...  {move_pair[1]}"
            move_descs.append(move_desc)    
        input_win = tk.Toplevel(self.mw)
        win_variable = tk.StringVar(input_win, move_descs[-1])
        def ok_cmd():
            global move_index
            sel_text = win_variable.get()
            move_index = move_descs.index(sel_text)
            input_win.destroy()                    # cleanup
            input_win.quit()
            
        g_sel = tk.OptionMenu(input_win, win_variable, *move_descs)
        g_sel.pack()
        ok_button = tk.Button(input_win,text="OK", command=ok_cmd)
        ok_button.pack()
        input_win.mainloop()                   # Loop till quit
        self.mw.after(0, self.on_cmd,
                      f"goto_move_idx {move_index}")
        

    
    def print_game_cmd(self):
        """ list game info
        """
        self.print_game(self.sel_game, desc=self.sel_short_desc)

    def print_game(self, game, desc=None):
        """ List selected game
        :game: game to list
        :desc: optional description
        """
        if game is None:
            return
        
        if desc is not None:
            SlTrace.lg(desc)
        game_str = pgn.dumps(game)
        SlTrace.lg(game_str)
                 
    def win_size_event(self, e):
        pass
    
    def pgmExit(self):
        code = 0
        sys.exit(code) 
        
    def file_open(self):
        """Select chess game files and load the game
        game files are text files of Portable Game Notation (PGN).
        see: https://www.chess.com/terms/chess-pgn
        """
        game_file = tk.filedialog.askopenfile(
                            initialdir=self.games_dir,
                            initialfile="fischer.pgn",
                            filetypes=[("chess games",".pgn")])
        pgn_text = game_file.read()

        pgn_games = pgn.loads(pgn_text) # Returns a list of PGNGame
        game_selections = []
        games_by_selection = {}     # Unique selections ???
        
        max_g = 1000
        
        for game_index, pgn_game in enumerate(pgn_games):
            n = game_index + 1
            if game_index >= max_g:
                break
            SlTrace.lg(f"{game_index+1}:\n{pgn.dumps(pgn_game)}\n", "display")
            short_desc = (f"{n}: {pgn_game.white} vs. {pgn_game.black}"
                        f" {pgn_game.event} {pgn_game.date}")
            game_selections.append(short_desc) 
            games_by_selection[short_desc] = pgn_game
        input_win = tk.Toplevel(self.mw)
        win_variable = tk.StringVar(input_win, game_selections[0])
        def ok_cmd(e):
            global entry_text
            entry_text = win_variable.get()
            input_win.destroy()                    # cleanup
            input_win.quit()
            
        g_sel = tk.OptionMenu(input_win, win_variable, *game_selections,
                              command=ok_cmd)
        g_sel.pack()
        input_win.mainloop()                   # Loop till quit
        
        sel_short_desc = entry_text
        sel_game = games_by_selection[sel_short_desc]
        SlTrace.lg(f"{sel_short_desc} {sel_game = }")
        self.sel_short_desc = sel_short_desc
        self.sel_game = sel_game
        self.mw.after(0, self.on_cmd, "f")  # update show with new game

    def iterate_game_files(dir_path):
        """ Iterate over pgn game files
        :dir_path: game files directory
        :returns: next game file, else None at end
        """
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                yield file_path
        return None

    def save_error_game(self, desc=None, game=None):
        """ Report error, saving file png text
        :desc: description
        :game: game
                default: from cbd
        """
        if game is None:
            game = self.sel_game
            
        file_base = f"error_{SlTrace.getTs()}.pgn"
        file_name = os.path.join(self.errors_dir, file_base)
        with open(file_name,"w") as f:
            file_text = pgn.dumps(game)
            print(file_text, file=f)
            if desc is not None:
                print("\n{" + desc + "}\n", file=f)
        
    def scan_files_cmd(self):
        """ Scan chess files in games directory
        """
        self.is_scanning = True     # Scanning files in progress
        self.scan_loops = 0         # Keep count
        self.scan_files_start()

    def scan_force_next_game(self):
        """ Force next move to go to next game
        """
        self.scan_is_force_next_game = True
        
    def scan_files_start(self):
        """ Start files scan
        :games_dir: directory of games pgn files
        """
        self.scan_loops += 1
        if self.scan_max_loops is not None:
            if self.scan_loops > self.scan_max_loops:
                SlTrace.lg(f"Stopping at {self.scan_loops = }")
                return
        
        self.scan_moves_iter = None # Iterate through game moves
        self.scan_games_iter = None # Iterate through file games
        # Iterate through dir files
        self.scan_files_iter = self.scan_dir_iter(self.games_dir)
        self.scan_do_move()        # Start/continue move scan

    def scan_is_wanted_game(self, pnggame):
        """ Check if we want to scan this game
        :pgngame: our game
        :returns: True if this game is our list
        """
        return True     # everything
            
    def scan_do_move(self):
        """ Continue game moves scan
        """
        if not self.is_scanning:
            return      # Scanning is over
    
        move = self.scan_get_move()            
        if move is None:
            self.after_no_arg(0, self.scan_files_start)  # start over
            return
        
        self.scan_call(move)
            
    def scan_call(self, move):
        """ Function to call users scan looping function
        We use the looping function
        :move: move specification
        """
        self.buttonClick(input=f"scan_move {move}")
        if self.is_scanning:
            self.after_no_arg(0, self.scan_do_move)

    def scan_moves_iterator(self, pgngame):
        """ Iterate moves through pgngame
        :pgngame: game returned via pgn.GameIterator()
        :returns: move if one, None if none left
        """
        move_index = 0
        while move_index < len(pgngame.moves):
            move = pgngame.moves[move_index]
            move_index += 1
            yield move
        
        return None
        
    def scan_get_move(self):
        """ Get next move from scanning
        :returns: move, None if at end of scanning list
        """
        # Loop to handle empty games
        while True:
            try:
                if self.scan_moves_iter is not None:
                    move = next(self.scan_moves_iter)
                    if self.scan_is_force_next_game:
                        raise StopIteration()   # force end of game
                    
                    return move
                
            except StopIteration:
                pass        # End of this game's moves
                self.scan_is_force_next_game = False

            # Get next game.
            if (game := self.scan_get_game()) is None:
                return None                 # No more games
            
            # Check if a desired game.
            if not self.scan_is_wanted_game(game):
                continue
            
            # Update with new game info
            self.scan_moves_iter = self.scan_moves_iterator(game)
            short_desc = (f"{game.white} vs. {game.black}"
                        f" {game.event} {game.date}")
            self.sel_game = game
            self.sel_short_desc = short_desc
            self.buttonClick("scan_new_game")
        return move
 
    def scan_get_game(self):
        """ Get next game, None if no more
        :returns: PgnGame, else None if nomore games
        """
        # Loop to handle empty files
        game = None
        while  True:
            if self.scan_games_iter is None:
                game = None
            else:
                try:
                    game = next(self.scan_games_iter)
                except StopIteration:
                    game = None
            if game is None:    
                if (file := self.scan_get_file()) is None:
                    return None
                
                SlTrace.lg(f"\nFile: {file}")
                self.scan_file_name = file
                with open(file) as game_file:
                    pgn_text = game_file.read()
                    pgn_games = pgn.loads(pgn_text) # Returns a list of PGNGame
                    self.scan_games_iter = iter(pgn_games)
            else:
                return game
 
    def scan_get_file(self):
        """ Get next file, None if no more
        :returns: file_path, else None if nomore files
        """

        try:
            file = next(self.scan_files_iter)
        except StopIteration:
            return None
        
        return file
        
    def scan_next_game(self):
        """ Do next game
        """
        game = self.game_iter.next()

    def scan_pause(self):
        """ Pause scanning
        """
        self.is_scanning = False
                
    def scan_dir_iter(self, games_dir):
        """ Iterate over directory, yielding next file path
        each time
        :games_dir: directory to scan
        :returns: next file path, None if end
        """
        for file in os.listdir(games_dir):
            # check the games files
            if file.endswith(".pgn"):
                # print path name of selected files
                file_path = os.path.join(games_dir, file)
                yield file_path
            
        return None
    
        
    def scan_file(file_path):
        """ Play games witin this file
        :file_path: path to game file
        :returns: game iterator for this file
        """                        
        pgn_iter = pgn.GameIterator(file_path)
        return pgn_iter    

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
        if self.err_count > 0:
            title = f"ERRORS: {self.err_count} {title}"
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

    def mainloop(self):
        """ Primary wait loop
        """
        self.mw.mainloop()

if __name__ == '__main__':
    from select_trace import SlTrace
    from chessboard import Chessboard
    from chessboard_print import ChessboardPrint
    
        
    SlTrace.clearFlags()
    pieces_list = [
        'FEN:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
        ':Kc1Qe1kh7 w',
    ]
    pieces_list = pieces_list[0:1]  # TFD - second board loses images
    cBd = None
    def test_on_cmd(input):
        SlTrace.lg(f"{input = }")
        
    for pieces in pieces_list: 
        cb2 = Chessboard(pieces=pieces)
        cbp = ChessboardPrint(cb2)
        cbp.display_board()
        cbd = ChessboardDisplay(cb2, new_display=True, title=f"pieces={pieces}",
                                games_dir="../games_test", scan_max_loops=2)
        cbd.set_cmd(test_on_cmd)    # Set in each window
        if cBd is None:
            cBd = cbd
        cbd.display_board()
        
    cBd.mainloop()
