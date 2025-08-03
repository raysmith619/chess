#chess_piece_images.py  07Feb2025
""" Supply chess images for chess board display
    wxPyhon version
"""
import os
import re

import wx

from select_trace import SlTrace

os.chdir(os.path.dirname(__file__))     # set this dir to be working dir
pieces_dir = "../chess_pieces"
im_size_x = 80
im_size_x = 200
im_size_y = im_size_x

class ChessPieceImages:
    name2ch_d = {"king":"k", "queen":"q", "rook":"r", "bishop":"b",
               "knight":"n", "pawn":"p"}
               
    def __init__(self, pieces_dir=pieces_dir, im_size_x=im_size_x, im_size_y=im_size_y):
        """
        Store display images as bitmaps
        Store instances of bitmaps
        so they do not get garbage collected to early
        """
            
        self.base_bitmaps = {}       # base bitmaps
        self.bitmap_dict = {}        # bitmaps by piece K=white king, q=black queen
        self.pieces_dir = pieces_dir
        self.im_size_x = im_size_x
        self.im_size_y = im_size_y
        self.pieces = []        # Pieces KkQq...
        pieces_files = os.listdir(self.pieces_dir)
        SlTrace.lg(f"ChessPieceImages.name2ch_d:{ChessPieceImages.name2ch_d}", "chess_images")
        for piece_file in pieces_files:
            piece_path = os.path.join(pieces_dir,piece_file)
            image_file = os.path.abspath(piece_path)
            base_file = os.path.basename(image_file)
            if not os.path.isfile(image_file):
                continue
            
            #SlTrace.lg(image_file, "chess_images")
            wx.Image.AddHandler(wx.PNGHandler())
            img = wx.Image(image_file, wx.BITMAP_TYPE_ANY)
            bitmap = wx.Bitmap(img)         # Convert to bitmap
            #image = image.convert("RGBA")       # Add alpha chanel, supporting transparency
            # Resize the bitmap if needed
            if (match_file:=re.match(r'(black|white)-(\w+)', base_file)):
                color = match_file.group(1)
                piece_name = match_file.group(2)
                #SlTrace.lg(f"piece_name:'{piece_name}'", "chess_images")
                #SlTrace.lg(f"ChessPieceImages.name2ch_d:{ChessPieceImages.name2ch_d}", "chess_images")
                piece_ch = ChessPieceImages.name2ch_d[piece_name]
                if color == "white":
                    piece_ch = piece_ch.upper()                
            else:
                err = f"piece file name {base_file} not r'(black|white)-(whitespace+)' - use filename"
                SlTrace.lg(err)
                piece_ch = base_file
                
            #image = image.resize((im_size_x, im_size_y))
            self.base_bitmaps[piece_ch] = bitmap
            self.bitmap_dict[piece_ch] = bitmap        # So image does not get lost

    def get_pieces(self):
        """ Get all pieces
        :returns list of pieces (rnbqkpRNBQKP)
        """
        return self.bitmap_dict.keys()
            
    def get_bitmap_dict(self):
        """ Returns dictionary of bitmaps by piece_ch e.g. K - white king
        :returns: dictionary of photo bitmaps by piece_ch
        """
        return self.bitmap_dict
    
    def get_piece_bitmap(self, piece, width=None, height=None):
        """ Get bitmap of piece (rnbkqpRNBKQP)
        :piece: rnbkqpRNBKQP
        :returns: photo bitmap
        :width: width of piece in pixels
            default: no scaling
        :height: height of piece in pixels
            default: no scaling
        """
        bitmap = self.bitmap_dict[piece]
        if width is not None or height is not None:
            bitmap = self.scale_bitmap(bitmap, width, height)
        return bitmap

    @staticmethod
    def scale_bitmap(bitmap, width, height):    # From Stackoverflow
        """ force width, height to int
        """
        image = bitmap.ConvertToImage()
        image = image.Scale(int(width), int(height), wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result
    
if __name__ == '__main__':

    class CanvasFrame(wx.Frame):
        def __init__(self, *args, **kw):
            super(CanvasFrame, self).__init__(*args, **kw)

            self.cpi = ChessPieceImages()
            self.InitUI()
            self.Show()

        def InitUI(self):

            self.Bind(wx.EVT_PAINT, self.OnPaint)

            self.SetTitle("wxPython Canvas shapes")
            self.Centre()

        @staticmethod
        def scale_bitmap(bitmap, width, height):    # From Stackoverflow
            image = bitmap.ConvertToImage()
            image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
            result = wx.Bitmap(image)
            return result

        def OnPaint(self, e):
            global color_idx
            
            size=self.GetClientSize()
            cv_w = size.width
            cv_h = size.height
            print(f"OnPaint cv_w:{cv_w} cv_h:{cv_h}")
            x_min = int(cv_w*.1)
            x_max = int(cv_w*.9)
            pat_width = x_max-x_min
            x_mid = int((x_min+x_max)/2)

            y_min = int(cv_h*.1)
            y_max = int(cv_h*.9)
            
                
            n_per_row = 4
            im_x_start = im_size_x//5
            im_y_start = 0
            np = 0
            im_x = im_x_start
            im_y = im_y_start
            dc = wx.PaintDC(self.grid_panel)
            dc.Clear()
            for piece_ch in self.cpi.get_pieces():
                np += 1
                bitmap = self.cpi.get_piece_bitmap(piece_ch)
                bitmap_scaled = self.scale_bitmap(bitmap, self.cpi.im_size_x,
                                                  self.cpi.im_size_y)
                dc.DrawBitmap(bitmap_scaled, im_x, im_y)
                if np % n_per_row != 0:
                    im_x += self.cpi.im_size_x
                else:
                    im_x = im_x_start
                    im_y += im_size_y
            
            
    
    SlTrace.clearFlags()
    app = wx.App()
    # Create main window
    cf = CanvasFrame(None)
    cv_width = im_size_x*5
    cv_height = cv_width
    cf.SetInitialSize(wx.Size(cv_width, cv_height))
    cf.Show()
    cf.Refresh()

    app.MainLoop()
