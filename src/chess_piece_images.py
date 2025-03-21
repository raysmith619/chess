#chess_piece_images.py  07Feb2025
""" Supply photo images fro chess board display
"""
import os
import re
from PIL import Image, ImageTk

from select_trace import SlTrace

os.chdir(os.path.dirname(__file__))     # set this dir to be working dir
pieces_dir = "../chess_pieces"
im_size_x = 80
im_size_y = im_size_x

class ChessPieceImages:
    name2ch_d = {"king":"k", "queen":"q", "rook":"r", "bishop":"b",
               "knight":"n", "pawn":"p"}
               
    def __init__(self, pieces_dir=pieces_dir, im_size_x=im_size_x, im_size_y=im_size_y):
        self.image_dict = {}        # Images by piece K=white king, q=black queen
        self.pieces_dir = pieces_dir
        self.im_size_x = im_size_x
        self.im_size_y = im_size_y
        pieces_files = os.listdir(self.pieces_dir)
        SlTrace.lg(f"ChessPieceImages.name2ch_d:{ChessPieceImages.name2ch_d}", "chess_images")
        for piece_file in pieces_files:
            piece_path = os.path.join(pieces_dir,piece_file)
            image_file = os.path.abspath(piece_path)
            base_file = os.path.basename(image_file)
            if not os.path.isfile(image_file):
                continue
            
            SlTrace.lg(image_file, "chess_images")
            image = Image.open(image_file)  # Replace with your image path
            image = image.convert("RGBA")       # Add alpha chanel, supporting transparency
            # Resize the image if needed
            image = image.resize((im_size_x, im_size_y))
            # Convert the image to a Tkinter-compatible format
            photo = ImageTk.PhotoImage(image)
            if match_file:=re.match(r'(black|white)-(\w+)', base_file):
                color = match_file.group(1)
                piece_name = match_file.group(2)
                SlTrace.lg(f"piece_name:'{piece_name}'", "chess_images")
                SlTrace.lg(f"ChessPieceImages.name2ch_d:{ChessPieceImages.name2ch_d}", "chess_images")
                piece_ch = ChessPieceImages.name2ch_d[piece_name]
                if color == "white":
                    piece_ch = piece_ch.upper()                
            else:
                err = f"piece file name {base_file} not r'(black|white)-(whitespace+)' - use filename"
                SlTrace.lg(err)
                piece_ch = base_file
                
            self.image_dict[piece_ch] = photo        # So image does not get lost
    
    def get_image_dict(self):
        """ Returns dictionary of images by piece_ch e.g. K - white king
        :returns: dictionary of photo images by piece_ch
        """
        return self.image_dict
    
    
if __name__ == '__main__':
    import tkinter as tk
    
    SlTrace.clearFlags()
    
    # Create main window
    root = tk.Tk()
    root.title("Image on Canvas")

    cpi = ChessPieceImages()
    
    image_d = cpi.get_image_dict()
    # Create a canvas
    canvas = tk.Canvas(root, width=800, height=800)
    canvas.pack()
    n_per_row = 4
    im_x_start = cpi.im_size_x
    im_y_start = 0
    np = 0
    im_x = im_x_start
    im_y = im_y_start
    for piece_ch in image_d:
        np += 1
        image = image_d[piece_ch]
        if np % n_per_row != 1:
            im_x += cpi.im_size_x
        else:
            im_x = im_x_start
            im_y += im_size_y
        canvas.create_image(im_x, im_y, anchor=tk.CENTER, image=image)

    root.mainloop()