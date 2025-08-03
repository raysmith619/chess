# wx_chess_canvas_panel.py 25Apr2025  crs, combine ChessboardPanel with CanvasPanel
#                    08Nov2023  crs
"""
Trying to avoid wx_chess_panel.py error:
    wxPython wxPaintDC must be associated with
    the window being repainted
    
Support for very limited list of tkinter Canvas type actions
on wxPython Panel  Our attempt here was to ease a port
from tkinter Canvas use to wxPython.
"""
import time
import re

import wx
from select_trace import SlTrace, SelectError

from wx_chess_piece_images import ChessPieceImages

from wx_stuff import *
from wx_canvas_panel import CanvasPanel 
from wx_canvas_panel_item import CanvasPanelItem            
from wx_adw_display_pending import AdwDisplayPending

        
class ChessCanvasPanel(CanvasPanel):
    
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
        self.changed = True     # Set True iff painting required
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
        
        if parent is None:
            parent = wx.Frame(None)
        super().__init__(parent, **kwargs)
        self.SetInitialSize(wx.Size(bd_width, bd_height))
        self.SetBackgroundColour( self.background )
        self.cpi = ChessPieceImages()       # Must come after default window setup
        self.parent = parent
        self.grid_panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Refresh()


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
        erase all displayed pieces tags="piece_tags"
        :title: updated title     
        :piece_squares: list of piece_squares to display
            default: use board.setting
        """
        if not hasattr(self, 'cpi'):
            return  # Piece info not ready  yed
        
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
        for item in self.items:
            self.add_item(item)

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
            sq_bounds = self.squares_bounds[ic,ir]
            ul_cx1, ul_cy1, lr_cx2, lr_cy2 = sq_bounds
            c_x = (ul_cx1+lr_cx2)//2  - self.sq_size//2      ### ??? Fudge
            c_y = (ul_cy1+lr_cy2)//2  - self.sq_size//2      ### ??? Fudge
            bitmap = self.cpi.get_piece_bitmap(piece, width=self.sq_size,
                                               height=self.sq_size )
            
            self.create_bitmap(ul_cx1, ul_cy1,
                               lr_cx2, lr_cy2, bitmap=bitmap,
                               desc=ps)

        else:
            err = f"Unrecognized piece-square: {ps}"
            SlTrace.lg(err)
            raise Exception(err)

    def set_board(self, board):
        """ Set board
        """
        self.board = board
                        
    def set_changed(self, set=True):
        """ Set canvas changed requesting
        repaint
        :set: state default: True
        """
        self.changed = set
        #if set:
        #    self.Refresh()
        #self.changed = True

    def draw_square(self, ic=None, ir=None, dc=None):
        """ Draw one board square
        Setup via OnPaint beginning
        :ic: column index starting at 0 from left
        :ir: row index, index row bottom to top
        :dc: device context
        """
        ul_cx1 = int(self.x_left + ic*self.sq_size)
        ul_cy1 = int(self.y_bot - (ir+1)*self.sq_size)
        lr_cx2 = int(ul_cx1 + self.sq_size) 
        lr_cy2 = int(ul_cy1 + self.sq_size)
        sq_color = self.dark_sq if (ic+ir)%2==0 else self.light_sq
        dc.SetPen(wx.Pen(sq_color, style=wx.SOLID))
        dc.SetBrush(wx.Brush(sq_color, wx.SOLID))
        rect = wx.Rect(wx.Point(ul_cx1, ul_cy1), wx.Point(lr_cx2, lr_cy2))
        dc.DrawRectangle(rect)
        sq_bounds = (ul_cx1, ul_cy1, lr_cx2, lr_cy2)
        self.squares_bounds[ic,ir] = sq_bounds    # store bounds
        self.squares_colors[ic,ir] = sq_color    
    
    def OnPaint(self, e):
        """ Draw board
        """
        #self.Freeze()
        dc = wx.PaintDC(self.grid_panel)
        #if not self.changed:
        #    return
        
        self.SetBackgroundColour(self.background)
        self.squares_colors = {}  # square colors dict [ic,ir]
        self.squares_bounds = {}  # square bounds dict [ic,ir]
        border_size = self.sq_size//2
        self.x_left = border_size    ### - self.sq_size//2
        self.y_top = border_size     ### - self.sq_size//2        
        self.y_bot = self.y_top + self.nsqy*self.sq_size   # y increases downward
        bd_width = int(self.nsqx*self.sq_size+2*border_size)
        bd_height = int(self.nsqy*self.sq_size+2*border_size+2*border_size)
        # Example: canvas.create_rectangle(ul_cx1,ul_cy1, lr_cx2,lr_cy2, ...)
        for ic in range(self.nsqx):     # index col left to right
            for ir in range(self.nsqy): # index row bottom to top
                self.draw_square(ic=ic, ir=ir, dc=dc)
                ul_cx1, ul_cy1, lr_cx2, lr_cy2 = self.squares_bounds[ic,ir]
                sq_color = self.squares_colors[ic,ir]    
                
                rank_font = wx.Font(wx.FontInfo(12))
                dc.SetFont(rank_font)
                rank_label = str(ir+1)
                rank_w,rank_h = dc.GetTextExtent(rank_label)
                rank_label_cx = int(self.x_left - border_size/2 - rank_w/2)
                rank_label_cy = int((lr_cy2+ul_cy1)//2 -5)
                dc.SetPen(wx.Pen(sq_color, style=wx.SOLID))
                dc.SetBrush(wx.Brush(sq_color, wx.SOLID))
                dc.DrawText(text=rank_label,  pt=wx.Point(rank_label_cx, rank_label_cy))
                SlTrace.lg(f"{ic} {ir} self.DrawRectangle("
                           f"x1:{ul_cx1},y1:{ul_cy1},x2:{lr_cx2},y2:{lr_cy2}, fill={sq_color})",
                                "build_display")
                file_label_cx = int((ul_cx1+lr_cx2)//2)
                file_label_cy = int(self.y_bot + border_size/4)
                dc.SetFont(rank_font)
                file_label = chr(ord('a')+ic)
                dc.DrawText(text=file_label,  pt=wx.Point(file_label_cx, file_label_cy))
        piece_squares = self.get_pieces()
        if piece_squares:
            self.clear(refresh=False) # Remove after display
            self.display_pieces(piece_squares=piece_squares)
        self.display_pending(dc)
        #self.Refresh()
        #self.set_changed(False)
        #self.Thaw()
        
    def scale_points(self, pts, sfx=None, sfy=None):
        """ scale a list of two dimensional points
        :pts: list of wx.Points
        :sfx: x scale factor  default: 1
        :sfy: y scale factor default: 1
        :returns: scaled points list
        """
        """ TFD Return original points unscalled
        """
        use_orig_points = True
        use_orig_points = False
        if use_orig_points:
            SlTrace.lg("use_orig_points", "paint")
            return pts[:]   # Copy of original points, unchanged
        
        if sfx is None:
            sfx = self.sfx
        if sfy is None:
            sfy = self.sfy
        pts_s = []
        if len(pts) == 0:
            return pts_s
        
        scale_1to1 = True
        if scale_1to1:
            sfx = sfy = 1.0
            SlTrace.lg(f"Force sfx:{sfx} sfy:{sfy}", "paint")
        x0,y0 = pts[0]
        for i in range(len(pts)):
            x,y = pts[i]
            x_s = x0 + int((x-x0)*sfx)
            y_s = y0 + int((y-y0)*sfy)
            pts_s.append(wx_Point(x_s,y_s))
        return pts_s
      
    def get_id(self):
        """ Get unique item id id
        """
        self.can_id += 1
        return self.can_id

    def no_call(self):
        """ Just a nothing call
        """
        return
    
    def after(self, delay, callback=None):
        """ Call after delay
        :delay: delay in milliseconds
        :callback: function to call
            default: no function, just delay
        """
        if callback is None:
            callback = self.no_call
        wx.CallLater(delay, callback)

    def create_composite(self, disp_type=None, desc=None):
        """ Create a composite display object
        whose components are displayed in order as an object
        :desc: description, if one
        """
        item = CanvasPanelItem(self, "create_composite",
                               disp_type=disp_type, desc=desc)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
                    
    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                **kwargs):
        """ Implement create_rectangle
            supporting: fill, outline, width
        :returns: id
        """
        item = CanvasPanelItem(self, "create_rectangle",
                               cx1,cy1,cx2,cy2,
                               **kwargs)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
                    
    def create_bitmap(self, cx1,cy1,cx2,cy2,
                      bitmap, desc=None,
                                **kwargs):
        """ Implement create_bitmap
        :returns: id
        """
        item = CanvasPanelItem(self, "create_bitmap",
                               cx1,cy1,cx2,cy2,
                               bitmap=bitmap,
                               desc=desc,
                               **kwargs)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
    
    def create_cursor(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_cursor
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_cursor",
                               x0,y0,x1,y1,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_oval(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_oval
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_oval",
                               x0,y0,x1,y1,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_point(self, x0,y0, radius=2,
                        **kwargs):
        """ Helper function to create a point
            Shortcut using create_oval
            supporting fill, outline, width
        """
        px0 = x0-radius
        py0 = y0-radius
        px1 = x0+radius
        py1 = y0+radius
        item_id = self.create_oval(px0,py0,px1,py1,
                                **kwargs)
        return item_id

    def create_line(self, *args, **kwargs):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        item = CanvasPanelItem(self, "create_line",
                               *args,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_text(self, x0,y0,
                        **kwargs):
        """ Implement create_text
            supporting fill, font
        """
        item = CanvasPanelItem(self, "create_text",
                               x0,y0,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
        

    def delete(self, *id_tags):
        """ Delete object(s) in panel
        :id_tags: if str: "all" - all items, else tag
                else id
        """
        for id_tag in id_tags:
            self.delete_id(id_tag)

    def delete_id(self, id_tag):
        """ Delete items having id or tag
        :id_tag: id or tag
        """
        for item in self.items:
            if type(id_tag) == int:
                if id_tag == item.canv_id:
                    item.deleted = True
                    #item.refresh()          # Force redraw
                    break   # id is unique
            
                if id_tag in item.tags:
                    item.deleted = True

    def OnSize(self, e):
        self.Refresh()
        #self.Update()
        SlTrace.lg(f"\nOnSize paint count:{self.on_paint_count}", "paint")
        size = self.GetSize()
        SlTrace.lg(f"panel size: {size}", "paint")
        #e.Skip()

    def draw_item(self, item):
        """ Draw item
        :item: CanvasPanalItem/canv_id item to draw
        """
        if type(item) == int:
            item = self.id_to_item(item)
        item.draw()
        
    def draw_items(self, items=None, rect=None,
                   types="create_composite"):
        """ Draw scalled items
        :items: items to draw default: self.items
        :rect: Draw only items in this rectangle
                default: draw all items
        :types: item types to draw
                "ALL" - all types except "create_composite"
                default: "create_composite"
        """
        if items is None:
            items = self.items
        if len(items) == 0:
            return
        do_composite = False
        do_all = False
        if types == "create_composite":
            do_composite = True
        elif types == "ALL":
            do_all = True
        else:
            if not isinstance(types,list):
                types = [types]     # Make list
        self.pos_adj = self.cur_pos-self.orig_pos
        SlTrace.lg(f"orig_size: {self.orig_size}"
                   f" cur_size: {self.cur_size}", "item")
        self.sfx = self.cur_size.x/self.orig_size.x
        self.sfy = self.cur_size.y/self.orig_size.y
        if len(items) == 0:
            return      # Short circuit if no items
        
        items_points = self.get_items_points(items)
        items_points_scaled = self.scale_points(items_points)

        ipo = 0     # current offset into items_points_scaled
        for item in items:                
            npts = len(item.points)
            points = items_points_scaled[ipo:ipo+npts]
            SlTrace.lg(f"item: {item}", "item")
            if ((do_composite and item.canv_type == "create_composite")
                    or (do_all and item.canv_type != "create_composite")
                    or (item.canv_type in types)):
                item.draw(points=points, rect=rect)
            ipo += npts # move to next item

    def get_items_points(self, items=None):
        """ Get all drawing points, or embeded figures
        characterization
        points
        :items: items list default: self.items
        :returns: list of all drawn points
        """
        if items is None:
            items = self.items
        points = []
        for item in self.items:
            points += item.points
        return points
    
    def set_check_proceed(self, proceed=True):
        self.check_proceed = proceed

    def my_app_kill(self, my_app):
        """ stop sup application loop
        :my_app: local wx.App instance
        """         
        my_app.ExitMainLoop()
        
    def check_for_display(self):
        """ Debug wait with event processing
        """
        self.app.MainLoop()

        duration = 4
        self.check_proceed = False
        wx.CallLater(duration*1000, self.set_check_proceed)
        while not self.check_proceed:
            my_app = wx.App()
            wx.CallLater(10, self.my_app_kill, my_app=my_app)
            my_app.MainLoop()
            pass

    def clear(self, refresh=True):
        """ Clear panel
        :refresh: True - refresh after clear
        """
        self.items_by_id = {}   # Items stored by item.canv_id
                                # Augmented by CanvasPanelItem.__init__()
        self.items = []         # Items in order drawn
        self.prev_reg = None    # Previously displayed
        self.adw_dp.clear()
        self.Refresh()
        
                
                    
    def itemconfig(self, tags, **kwargs):
        """ Adjust items with tags with kwargs
        :tags: tag or tag list of items to change
        :kwargs: new attributes
                    supporting: outline
        """
        if type(tags) != list:
            tags = [tags]
            
        for item in self.items:
            ins = item.tags.intersection(tags)
            if len(ins) > 0:   # item have tag?
                for kw in  kwargs:
                    val = kwargs[kw]
                    if kw == "outline":
                        item.kwargs[kw] = val
                    else:
                        raise SelectError(f"itemconfig doesn't support {kw} (val:{val})")    

    
    def update_item(self, item, **kwargs):
        """ Update cell, with "inplace" attribute changes
            refreshes item's region 
        :item: item / id
        :**kwargs: attributes to be changed
        """
        if type(item) == int:
            item = self.items_by_id[item]
        item.update(**kwargs)
        bdrect = item.bounding_rect()
        self.grid_panel.RefreshRect(rect=bdrect)


    """
    ----------------------- Mouse Control --------------------
    """
    def get_panel_loc(self, e):
        """ Get mouse location in panel coordinates
        """
        screen_loc = e.Position
        panel_loc = wx_Point(screen_loc.x,
                            screen_loc.y-
                            self.grid_panel_offset)
        return panel_loc

    def id_to_item(self, canv_id):
        """ Return item, given id
        :returns: canv item
        """
        return self.items_by_id[canv_id]
    
    def get_panel_items(self, loc, canv_type="create_rectangle"):
        """ Get item/items at this location
        :loc: wx.Point location at this point
        :canv_type: canvas type e.g., create_rectangle
                default: create_rectangle
        """
        items = []
        for item in self.items:
            if item.bounding_rect().Contains(loc):
                if item.canv_type == canv_type:
                    items.append(item)
        return items
        
    def get_screen_loc(self, panel_loc):
        """ Convert panel location to screen location
        :panel_loc: wx_Point of location
        :returns: wx_Point on screen
        """
        screen_loc = wx_Point(panel_loc.x,
                              panel_loc.y+
                              self.grid_panel_offset)
        return screen_loc
    
    #import pyautogui   #??? comment this line
                       #??? and first click causes
                       #??? the window to shrink
    # mouse_left_down
    def on_mouse_left_down(self, e):
        """ Mouse down
        """
                
        loc = self.get_panel_loc(e) # grid relative
        SlTrace.lg(f"\non_mouse_left_down panel({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}", "paint"
                   )
        #e.Skip()
        size = self.grid_panel.GetSize()
        pts = self.scale_points([wx_Point(e.Position.x, e.Position.y),
                                 wx_Point(0,0), wx_Point(size.x,0),
                                 wx_Point(0,size.y), wx_Point(size.x,size.y)])
        pt = pts[0]
        self.mouse_left_down_proc(pt.x, pt.y)
        self.grid_panel.SetFocus() # Give grid_panel focus


    def on_mouse_left_down_win(self, e):
        """ Mouse down in window
        """
                
        loc = wx_Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_win ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}", "paint"
                   )
        e.Skip()

    def on_mouse_left_down_frame(self, e):
        """ Mouse down in window
        """
                
        loc = wx_Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_frame ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}", "paint"
                   )
        e.Skip()
        
    def mouse_left_down_def(self, x, y):
        """ process mouse left down event
        Replaced for external processing
        :x: mouse x coordiante
        :y: mouse y coordinate
        """
        SlTrace.lg(f"mouse_left_down_proc x={x}, y={y}", "mouse_proc")
    
    def set_mouse_left_down_proc(self, proc):
        """ Set link to front end processing of
        mouse left down event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_left_down_proc = proc

    # mouse motion and mouse down motion
    def on_mouse_motion(self, e):
        """ Mouse motion in  window
        we convert <B1-Motion> into on_button_1_motion calls
        """
        loc = self.get_panel_loc(e)
        if e.Dragging():
            self.mouse_b1_motion_proc(loc.x, loc.y)
        else:
            self.mouse_motion_proc(loc.x, loc.y)

    def mouse_motion_def(self, x, y):
        """ Set to connect to remote processing
        """
        SlTrace.lg(f"mouse_motion_proc(x={x}, y={y})", "motion")

    def mouse_b1_motion_def(self, x, y):
        """ Default mouse_b1_motion event proceessing
        """
        SlTrace.lg(f"mouse_b1_motion_proc(x={x}, y={y})")
    
    def set_mouse_motion_proc(self, proc):
        """ Default mouse_motion event processing
        mouse motion event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_motion_proc = proc
   
    def set_mouse_b1_motion_proc(self, proc):
        """ Set link to front end processing of
        mouse b1 down motion event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_b1_motion_proc = proc

    def redraw(self):
        """ Redraw screen
        """
        #self.Refresh()
        #self.Update()
        #self.Show()

    def refresh_item(self, item):        
        """ mark item's region to be displayed
        :item: CanvasPanelItem/id
        """
        if type(item) == int:
            if item >= len(self.items):
                return      # Outside bounds - ignore
            
            item = self.items[item]
        rect = item.bounding_rect()
        self.grid_panel.RefreshRect(rect)
                    
    def refresh_rectangle(self, *args,
                                **kwargs):
        """ Mark rectangle in need of repainting
        :arg[0]: wx.Rect 0 rectangle to refresh
        :
        :args[0]..args[3]: rectangle x1,y1, x2,y2 coordinates
        """
        if isinstance(args[0], wx.Rect):
            rect = args[0]
        else:
            rect = wx.Rect(wx.Point(args[0],args[1]),wx.Point(args[2],args[3]))
        SlTrace.lg(f"refresh_rectangle({rect})", "refresh")
        self.grid_panel.RefreshRect(rect)

    def update(self, x1=None, y1=None, x2=None, y2=None,
               full=False):
        """ Update display
            If x1,...y2 are present - limit update to rectangle
            If x1 is a wx.Rect use Rect
            :full: force full update
        """
        return  # TFD
        now = time.time()
        '''
        since_last = now - self.time_of_update
        if since_last < self.min_time_update:
            delay_ms = int((self.time_of_update + self.min_time_update-now)*1000)
            wx.CallLater(delay_ms, self.update, x1=x1, y1=y1, x2=x2, y2=y2)
            return          # Too soon for update
        '''
        self.time_of_update = time.time()
        if full:
            #self.grid_panel.Refresh()
            #self.grid_panel.Update()
            return
    
        SlTrace.lg(f"update: refresh({x1,y1, x2,y2})", "refresh")
        if x1 is not None or x2 is not None:
            if isinstance(x1, wx.Rect):
                self.grid_panel.RefreshRect(x1)
            else:
                self.grid_panel.RefreshRect(rect=wx.Rect(wx_Point(x1,y1),
                                                         wx_Point(x2,y2)))
        else:
            self.grid_panel.Refresh()
        #self.grid_panel.Update()
        
    """
    ----------------------- Keyboard Control --------------------
    """

    def set_key_press_proc(self, proc):
        """ Set key press processing function to facilitating 
        setting/changing processing function to after initial
        setup
        :proc: key processing function type proc(keysym)
        """
        self.key_press_proc = proc

       
    def on_char_hook(self, e):
        SlTrace.lg(f"\non_char_hook:{e}", "keys")
        
        if e.AltDown():
            SlTrace.lg(f"{self.get_mod_str(e)}", "keys")
            e.Skip()    # Pass up to e.g., Menu
            return
        
        SlTrace.lg(f"sym: {self.get_mod_str(e)}", "keys")
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}", "keys")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}", "keys")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}", "keys")
        SlTrace.lg(f"chr(GetKeyCode){chr(e.GetKeyCode())}"
                   f" {ord(chr(e.GetKeyCode()))}", "keys")
        
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)
        self.grid_panel.SetFocus() # Give grid_panel focus

    def on_key_down(self, e):
        SlTrace.lg(f"on_key_down:{e}", "keys")
        SlTrace.lg(f"sym: {self.get_mod_str(e)}", "keys")
        if e.AltDown():
            SlTrace.lg(f"{self.get_mod_str(e)}", "keys")
            e.Skip()    # Pass up to e.g., Menu
            return
        
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}", "keys")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}", "keys")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}", "keys")
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)

    def get_mod_str(self, e):
        """ return modifier list string
        :e: event
        :returns: "[mod1-][mod2-][...]key_sym"
        """
        mod_str = ""
        if e.HasModifiers():
            mods = e.GetModifiers()
            if mods & wx.MOD_ALT:
                if mod_str != "": mod_str += "-"
                mod_str += "ALT"
            if mods & wx.MOD_CONTROL:
                if mod_str != "": mod_str += "-"
                mod_str += "CTL"
            if mods & wx.MOD_SHIFT:
                if mod_str != "": mod_str += "-"
                mod_str += "SHIFT"
            if mods & wx.MOD_ALTGR and mods == wx.MOD_ALTGR:
                if mod_str != "": mod_str += "-"
                mod_str += "ALTGR"
            if mods & wx.MOD_META:
                if mod_str != "": mod_str += "-"
                mod_str += "META"
            if mods & wx.MOD_WIN:
                if mod_str != "": mod_str += "-"
                mod_str += "WIN"
        ret = mod_str
        if ret != "": ret += "-"
        ret += self.get_keysym(e)
        return ret
        

    def key_press(self, keysym):
        """ default/null simulated key event
        :keysym: Symbolic key value/string
        """
        SlTrace.lg(keysym)
        return

    def get_keysym(self, e):
        """ Convert key symbol to keysym(tkinter style)
        :e: key event
        :returns: keysym(tkinter) string
        """
        unicode = e.GetUnicodeKey()
        raw_key_code = e.GetRawKeyCode()
        key_code = e.GetKeyCode()
        ch = chr(unicode)  # lazy - accept all single char

        if (key_code >= wx.WXK_NUMPAD0 and
            key_code <= wx.WXK_NUMPAD9):
            return str(key_code-wx.WXK_NUMPAD0)        
        if key_code == wx.WXK_ALT:
            return 'Alt_L'
        if key_code == wx.WXK_ESCAPE:
            return 'Escape'
        if key_code == wx.WXK_UP:
            return 'Up'
        if key_code == wx.WXK_DOWN:
            return 'Down'
        if key_code == wx.WXK_LEFT:
            return 'Left'
        if key_code == wx.WXK_RIGHT:
            return 'Right'
        if key_code == wx.WXK_WINDOWS_LEFT:
            return 'win_l'

        if len(ch) == 1:
            return ch
        
        return '???'    # Unrecognized


    """
    canvas_panel functions
    """
        
    def scale_points(self, pts, sfx=None, sfy=None):
        """ scale a list of two dimensional points
        :pts: list of wx.Points
        :sfx: x scale factor  default: 1
        :sfy: y scale factor default: 1
        :returns: scaled points list
        """
        """ TFD Return original points unscalled
        """
        use_orig_points = True
        use_orig_points = False
        if use_orig_points:
            SlTrace.lg("use_orig_points", "paint")
            return pts[:]   # Copy of original points, unchanged
        
        if sfx is None:
            sfx = self.sfx
        if sfy is None:
            sfy = self.sfy
        pts_s = []
        if len(pts) == 0:
            return pts_s
        
        scale_1to1 = True
        if scale_1to1:
            sfx = sfy = 1.0
            SlTrace.lg(f"Force sfx:{sfx} sfy:{sfy}", "paint")
        x0,y0 = pts[0]
        for i in range(len(pts)):
            x,y = pts[i]
            x_s = x0 + int((x-x0)*sfx)
            y_s = y0 + int((y-y0)*sfy)
            pts_s.append(wx_Point(x_s,y_s))
        return pts_s
      
    def get_id(self):
        """ Get unique item id id
        """
        self.can_id += 1
        return self.can_id

    def no_call(self):
        """ Just a nothing call
        """
        return
    
    def after(self, delay, callback=None):
        """ Call after delay
        :delay: delay in milliseconds
        :callback: function to call
            default: no function, just delay
        """
        if callback is None:
            callback = self.no_call
        wx.CallLater(delay, callback)

    def create_composite(self, disp_type=None, desc=None):
        """ Create a composite display object
        whose components are displayed in order as an object
        :desc: description, if one
        """
        item = CanvasPanelItem(self, "create_composite",
                               disp_type=disp_type, desc=desc)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
                    
    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                **kwargs):
        """ Implement create_rectangle
            supporting: fill, outline, width
        :returns: id
        """
        item = CanvasPanelItem(self, "create_rectangle",
                               cx1,cy1,cx2,cy2,
                               **kwargs)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
                    
    def create_bitmap(self, cx1,cy1,cx2,cy2,
                      bitmap, desc=None,
                                **kwargs):
        """ Implement create_bitmap
        :returns: id
        """
        item = CanvasPanelItem(self, "create_bitmap",
                               cx1,cy1,cx2,cy2,
                               bitmap=bitmap,
                               desc=desc,
                               **kwargs)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
    
    def create_cursor(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_cursor
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_cursor",
                               x0,y0,x1,y1,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_oval(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_oval
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_oval",
                               x0,y0,x1,y1,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_point(self, x0,y0, radius=2,
                        **kwargs):
        """ Helper function to create a point
            Shortcut using create_oval
            supporting fill, outline, width
        """
        px0 = x0-radius
        py0 = y0-radius
        px1 = x0+radius
        py1 = y0+radius
        item_id = self.create_oval(px0,py0,px1,py1,
                                **kwargs)
        return item_id

    def create_line(self, *args, **kwargs):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        item = CanvasPanelItem(self, "create_line",
                               *args,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_text(self, x0,y0,
                        **kwargs):
        """ Implement create_text
            supporting fill, font
        """
        item = CanvasPanelItem(self, "create_text",
                               x0,y0,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
        

    def delete(self, *id_tags):
        """ Delete object(s) in panel
        :id_tags: if str: "all" - all items, else tag
                else id
        """
        for id_tag in id_tags:
            self.delete_id(id_tag)

    def delete_id(self, id_tag):
        """ Delete items having id or tag
        :id_tag: id or tag
        """
        for item in self.items:
            if type(id_tag) == int:
                if id_tag == item.canv_id:
                    item.deleted = True
                    #item.refresh()          # Force redraw
                    break   # id is unique
            
                if id_tag in item.tags:
                    item.deleted = True

    def OnSize(self, e):
        #self.Update()
        SlTrace.lg(f"\nOnSize paint count:{self.on_paint_count}", "paint")
        size = self.GetSize()
        SlTrace.lg(f"panel size: {size}", "paint")
        #e.Skip()
        self.set_changed()

    def draw_item(self, item):
        """ Draw item
        :item: CanvasPanalItem/canv_id item to draw
        """
        if type(item) == int:
            item = self.id_to_item(item)
        item.draw()
        
    def draw_items(self, items=None, rect=None,
                   types="create_composite"):
        """ Draw scalled items
        :items: items to draw default: self.items
        :rect: Draw only items in this rectangle
                default: draw all items
        :types: item types to draw
                "ALL" - all types except "create_composite"
                default: "create_composite"
        """
        if items is None:
            items = self.items
        if len(items) == 0:
            return
        do_composite = False
        do_all = False
        if types == "create_composite":
            do_composite = True
        elif types == "ALL":
            do_all = True
        else:
            if not isinstance(types,list):
                types = [types]     # Make list
        self.pos_adj = self.cur_pos-self.orig_pos
        SlTrace.lg(f"orig_size: {self.orig_size}"
                   f" cur_size: {self.cur_size}", "item")
        self.sfx = self.cur_size.x/self.orig_size.x
        self.sfy = self.cur_size.y/self.orig_size.y
        if len(items) == 0:
            return      # Short circuit if no items
        
        items_points = self.get_items_points(items)
        items_points_scaled = self.scale_points(items_points)

        ipo = 0     # current offset into items_points_scaled
        for item in items:                
            npts = len(item.points)
            points = items_points_scaled[ipo:ipo+npts]
            SlTrace.lg(f"item: {item}", "item")
            if ((do_composite and item.canv_type == "create_composite")
                    or (do_all and item.canv_type != "create_composite")
                    or (item.canv_type in types)):
                item.draw(points=points, rect=rect)
            ipo += npts # move to next item

    def get_items_points(self, items=None):
        """ Get all drawing points, or embeded figures
        characterization
        points
        :items: items list default: self.items
        :returns: list of all drawn points
        """
        if items is None:
            items = self.items
        points = []
        for item in self.items:
            points += item.points
        return points
    
    def set_check_proceed(self, proceed=True):
        self.check_proceed = proceed

    def my_app_kill(self, my_app):
        """ stop sup application loop
        :my_app: local wx.App instance
        """         
        my_app.ExitMainLoop()
        
    def check_for_display(self):
        """ Debug wait with event processing
        """
        self.app.MainLoop()

        duration = 4
        self.check_proceed = False
        wx.CallLater(duration*1000, self.set_check_proceed)
        while not self.check_proceed:
            my_app = wx.App()
            wx.CallLater(10, self.my_app_kill, my_app=my_app)
            my_app.MainLoop()
            pass

    def clear(self, refresh=True):
        """ Clear panel
        :refresh: True - refresh after clear
        """
        self.items_by_id = {}   # Items stored by item.canv_id
                                # Augmented by CanvasPanelItem.__init__()
        self.items = []         # Items in order drawn
        self.prev_reg = None    # Previously displayed
        self.adw_dp.clear()
        if refresh:
            self.Refresh()
        
                
                    
    def itemconfig(self, tags, **kwargs):
        """ Adjust items with tags with kwargs
        :tags: tag or tag list of items to change
        :kwargs: new attributes
                    supporting: outline
        """
        if type(tags) != list:
            tags = [tags]
            
        for item in self.items:
            ins = item.tags.intersection(tags)
            if len(ins) > 0:   # item have tag?
                for kw in  kwargs:
                    val = kwargs[kw]
                    if kw == "outline":
                        item.kwargs[kw] = val
                    else:
                        raise SelectError(f"itemconfig doesn't support {kw} (val:{val})")    

    
    def update_item(self, item, **kwargs):
        """ Update cell, with "inplace" attribute changes
            refreshes item's region 
        :item: item / id
        :**kwargs: attributes to be changed
        """
        if type(item) == int:
            item = self.items_by_id[item]
        item.update(**kwargs)
        bdrect = item.bounding_rect()
        self.grid_panel.RefreshRect(rect=bdrect)


    """
    ----------------------- Mouse Control --------------------
    """
    def get_panel_loc(self, e):
        """ Get mouse location in panel coordinates
        """
        screen_loc = e.Position
        panel_loc = wx_Point(screen_loc.x,
                            screen_loc.y-
                            self.grid_panel_offset)
        return panel_loc

    def id_to_item(self, canv_id):
        """ Return item, given id
        :returns: canv item
        """
        return self.items_by_id[canv_id]
    
    def get_panel_items(self, loc, canv_type="create_rectangle"):
        """ Get item/items at this location
        :loc: wx.Point location at this point
        :canv_type: canvas type e.g., create_rectangle
                default: create_rectangle
        """
        items = []
        for item in self.items:
            if item.bounding_rect().Contains(loc):
                if item.canv_type == canv_type:
                    items.append(item)
        return items
        
    def get_screen_loc(self, panel_loc):
        """ Convert panel location to screen location
        :panel_loc: wx_Point of location
        :returns: wx_Point on screen
        """
        screen_loc = wx_Point(panel_loc.x,
                              panel_loc.y+
                              self.grid_panel_offset)
        return screen_loc
    
    #import pyautogui   #??? comment this line
                       #??? and first click causes
                       #??? the window to shrink
    # mouse_left_down
    def on_mouse_left_down(self, e):
        """ Mouse down
        """
                
        loc = self.get_panel_loc(e) # grid relative
        SlTrace.lg(f"\non_mouse_left_down panel({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}", "paint"
                   )
        #e.Skip()
        size = self.grid_panel.GetSize()
        pts = self.scale_points([wx_Point(e.Position.x, e.Position.y),
                                 wx_Point(0,0), wx_Point(size.x,0),
                                 wx_Point(0,size.y), wx_Point(size.x,size.y)])
        pt = pts[0]
        self.mouse_left_down_proc(pt.x, pt.y)
        self.grid_panel.SetFocus() # Give grid_panel focus


    def on_mouse_left_down_win(self, e):
        """ Mouse down in window
        """
                
        loc = wx_Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_win ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}", "paint"
                   )
        e.Skip()

    def on_mouse_left_down_frame(self, e):
        """ Mouse down in window
        """
                
        loc = wx_Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_frame ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}", "paint"
                   )
        e.Skip()
        
    def mouse_left_down_def(self, x, y):
        """ process mouse left down event
        Replaced for external processing
        :x: mouse x coordiante
        :y: mouse y coordinate
        """
        SlTrace.lg(f"mouse_left_down_proc x={x}, y={y}", "mouse_proc")
    
    def set_mouse_left_down_proc(self, proc):
        """ Set link to front end processing of
        mouse left down event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_left_down_proc = proc

    # mouse motion and mouse down motion
    def on_mouse_motion(self, e):
        """ Mouse motion in  window
        we convert <B1-Motion> into on_button_1_motion calls
        """
        loc = self.get_panel_loc(e)
        if e.Dragging():
            self.mouse_b1_motion_proc(loc.x, loc.y)
        else:
            self.mouse_motion_proc(loc.x, loc.y)

    def mouse_motion_def(self, x, y):
        """ Set to connect to remote processing
        """
        SlTrace.lg(f"mouse_motion_proc(x={x}, y={y})", "motion")

    def mouse_b1_motion_def(self, x, y):
        """ Default mouse_b1_motion event proceessing
        """
        SlTrace.lg(f"mouse_b1_motion_proc(x={x}, y={y})")
    
    def set_mouse_motion_proc(self, proc):
        """ Default mouse_motion event processing
        mouse motion event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_motion_proc = proc
   
    def set_mouse_b1_motion_proc(self, proc):
        """ Set link to front end processing of
        mouse b1 down motion event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_b1_motion_proc = proc

    def redraw(self):
        """ Redraw screen
        """
        #self.Refresh()
        #self.Update()
        #self.Show()

    def refresh_item(self, item):        
        """ mark item's region to be displayed
        :item: CanvasPanelItem/id
        """
        if type(item) == int:
            if item >= len(self.items):
                return      # Outside bounds - ignore
            
            item = self.items[item]
        rect = item.bounding_rect()
        self.grid_panel.RefreshRect(rect)
                    
    def refresh_rectangle(self, *args,
                                **kwargs):
        """ Mark rectangle in need of repainting
        :arg[0]: wx.Rect 0 rectangle to refresh
        :
        :args[0]..args[3]: rectangle x1,y1, x2,y2 coordinates
        """
        if isinstance(args[0], wx.Rect):
            rect = args[0]
        else:
            rect = wx.Rect(wx.Point(args[0],args[1]),wx.Point(args[2],args[3]))
        SlTrace.lg(f"refresh_rectangle({rect})", "refresh")
        self.grid_panel.RefreshRect(rect)

    def update(self, x1=None, y1=None, x2=None, y2=None,
               full=False):
        """ Update display
            If x1,...y2 are present - limit update to rectangle
            If x1 is a wx.Rect use Rect
            :full: force full update
        """
        return  # TFD
        now = time.time()
        '''
        since_last = now - self.time_of_update
        if since_last < self.min_time_update:
            delay_ms = int((self.time_of_update + self.min_time_update-now)*1000)
            wx.CallLater(delay_ms, self.update, x1=x1, y1=y1, x2=x2, y2=y2)
            return          # Too soon for update
        '''
        self.time_of_update = time.time()
        if full:
            self.grid_panel.Refresh()
            #self.grid_panel.Update()
            return
    
        SlTrace.lg(f"update: refresh({x1,y1, x2,y2})", "refresh")
        if x1 is not None or x2 is not None:
            if isinstance(x1, wx.Rect):
                self.grid_panel.RefreshRect(x1)
            else:
                self.grid_panel.RefreshRect(rect=wx.Rect(wx_Point(x1,y1),
                                                         wx_Point(x2,y2)))
        else:
            self.grid_panel.Refresh()
        #self.grid_panel.Update()
        
    """
    ----------------------- Keyboard Control --------------------
    """

    def set_key_press_proc(self, proc):
        """ Set key press processing function to facilitating 
        setting/changing processing function to after initial
        setup
        :proc: key processing function type proc(keysym)
        """
        self.key_press_proc = proc

       
    def on_char_hook(self, e):
        SlTrace.lg(f"\non_char_hook:{e}", "keys")
        
        if e.AltDown():
            SlTrace.lg(f"{self.get_mod_str(e)}", "keys")
            e.Skip()    # Pass up to e.g., Menu
            return
        
        SlTrace.lg(f"sym: {self.get_mod_str(e)}", "keys")
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}", "keys")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}", "keys")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}", "keys")
        SlTrace.lg(f"chr(GetKeyCode){chr(e.GetKeyCode())}"
                   f" {ord(chr(e.GetKeyCode()))}", "keys")
        
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)
        self.grid_panel.SetFocus() # Give grid_panel focus

    def on_key_down(self, e):
        SlTrace.lg(f"on_key_down:{e}", "keys")
        SlTrace.lg(f"sym: {self.get_mod_str(e)}", "keys")
        if e.AltDown():
            SlTrace.lg(f"{self.get_mod_str(e)}", "keys")
            e.Skip()    # Pass up to e.g., Menu
            return
        
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}", "keys")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}", "keys")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}", "keys")
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)

    def get_mod_str(self, e):
        """ return modifier list string
        :e: event
        :returns: "[mod1-][mod2-][...]key_sym"
        """
        mod_str = ""
        if e.HasModifiers():
            mods = e.GetModifiers()
            if mods & wx.MOD_ALT:
                if mod_str != "": mod_str += "-"
                mod_str += "ALT"
            if mods & wx.MOD_CONTROL:
                if mod_str != "": mod_str += "-"
                mod_str += "CTL"
            if mods & wx.MOD_SHIFT:
                if mod_str != "": mod_str += "-"
                mod_str += "SHIFT"
            if mods & wx.MOD_ALTGR and mods == wx.MOD_ALTGR:
                if mod_str != "": mod_str += "-"
                mod_str += "ALTGR"
            if mods & wx.MOD_META:
                if mod_str != "": mod_str += "-"
                mod_str += "META"
            if mods & wx.MOD_WIN:
                if mod_str != "": mod_str += "-"
                mod_str += "WIN"
        ret = mod_str
        if ret != "": ret += "-"
        ret += self.get_keysym(e)
        return ret
        

    def key_press(self, keysym):
        """ default/null simulated key event
        :keysym: Symbolic key value/string
        """
        SlTrace.lg(keysym)
        return

    def get_keysym(self, e):
        """ Convert key symbol to keysym(tkinter style)
        :e: key event
        :returns: keysym(tkinter) string
        """
        unicode = e.GetUnicodeKey()
        raw_key_code = e.GetRawKeyCode()
        key_code = e.GetKeyCode()
        ch = chr(unicode)  # lazy - accept all single char

        if (key_code >= wx.WXK_NUMPAD0 and
            key_code <= wx.WXK_NUMPAD9):
            return str(key_code-wx.WXK_NUMPAD0)        
        if key_code == wx.WXK_ALT:
            return 'Alt_L'
        if key_code == wx.WXK_ESCAPE:
            return 'Escape'
        if key_code == wx.WXK_UP:
            return 'Up'
        if key_code == wx.WXK_DOWN:
            return 'Down'
        if key_code == wx.WXK_LEFT:
            return 'Left'
        if key_code == wx.WXK_RIGHT:
            return 'Right'
        if key_code == wx.WXK_WINDOWS_LEFT:
            return 'win_l'

        if len(ch) == 1:
            return ch
        
        return '???'    # Unrecognized


    """
    Links to adw_display_pending
    """
    
    def add_item(self, item):
        """ Add display item
        :item: item/id (CanvasPanelItem)
        """
        self.adw_dp.add_item(item)

    def get_displayed_items(self):
        """ Get list of displayed items
        :returns: list of permanently displayed values (AdwDisplayPendingItem)
        """
        return self.adw_dp.get_displayed_items()


    def is_overlapping(self, item1, item2):
        """ Check if two display items are overlapping
        :returns: True iff overlapping
        """
        return self.adw_dp.is_overlapping(item1, item2)

        
    def add_cell(self, di_item):
        """ Add cell to be displayed
        :di_item: display item
        """            
        self.adw_dp.add_cell(di_item)

    def add_cursor(self, cursor):
        """ Display list and clear it
        """
        self.adw_dp.add_cursor(cursor)

    
    def display_pending(self, dc):
        """ Display list and clear it
        """
        self.adw_dp.display_pending(dc)
    """ end of canvas_panel functions
    """


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
        cbd = ChessCanvasPanel(frame, title=f"pieces={pieces}", board=cb)
        SlTrace.lg(f"After pieces={pieces}")

    app.MainLoop()
