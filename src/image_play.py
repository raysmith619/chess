#image_play.py  06Feb2025  crs, from ai
#
import os

import tkinter as tk
from PIL import Image, ImageTk
from select_trace import SlTrace

os.chdir(os.path.dirname(__file__))     # set this dir to be working dir
pieces_dir = "../chess_pieces"

# Create main window
root = tk.Tk()
root.title("Image on Canvas")

# Create a canvas
canvas = tk.Canvas(root, width=800, height=800)
canvas.pack()

# Open the images
piece_files = os.listdir(pieces_dir)
np = 0
im_size_x = 80
im_size_y = im_size_x
im_size = (im_size_x, im_size_y)

images = []     # Store images or only last is shown
im_x_start = im_size_x
im_y_start = im_size_y
im_y = im_x_start
im_x = im_y_start
n_per_row = 8
for piece_file in piece_files:
    piece_path = os.path.join(pieces_dir,piece_file)
    image_file = os.path.abspath(piece_path)
    if not os.path.isfile(image_file):
        continue
    
    np += 1
    SlTrace.lg(image_file)
    image = Image.open(image_file)  # Replace with your image path
    image = image.convert("RGBA")       # Add alpha chanel, supporting transparency
    # Resize the image if needed
    image = image.resize(im_size)
    # Convert the image to a Tkinter-compatible format
    photo = ImageTk.PhotoImage(image)
    images.append(photo)        # So image does not get lost
    # Add the image to the canvas
    if np % n_per_row != 1:
        im_x += im_size_x
    else:
        im_x = im_x_start
        im_y += im_size_y
        
    SlTrace.lg(f"im_x:{im_x}, im_y:{im_y}")
    canvas.create_image(im_x, im_y, anchor=tk.CENTER, image=photo)
    
# Start the main loop
root.mainloop()