#wx_anotated_chess_panel.py   26Aug2026  crs, extend ChesssPanel
""" Support arrow from from-sq to to-sq
"""
import time
import math

import wx

from graphics_braille.select_trace import SlTrace

from wx_chess_canvas_panel import ChessCanvasPanel

test_spot = False           # True to display show_spot

class ArrowElement:
    def __init__(self, from_sq, to_sq,
                    moves="white",
                     fill="blue", width=5, **kwargs):
        """ Arrow element history
        :acp: AnotatedChessPanel
        :from_sq: starting chess square [a-h][1-8]
        :to_sq: destination chess square [a-h][1-8]
        :moves: side moved default: white
        :fill: color fill default: "red"
        :width: line width default: 10 pixels
        :**kwargs: optional keyword options
        """
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.moves = moves
        self.fill = fill
        self.width = width
        self.kwargs = kwargs


class ArrowHistory:
    def __init__(self, acp):
        """ Handle Arrow History
        :acp: AnotatedChessPanel
        """
        self.acp = acp
        self.history = []           # Arrow history, list of ArrowElement
        self.from_sq = None         # latest - for debugging
        self.to_sq = None
        self.display_direction_offset = 0    # current choice

    def clear_history(self):
        """ JUst clear history of arrows
        """
        self.history = []
                
    def change_display_direction(self):
        """ Change/Bump move direction display
        adds to base number
        """
        self.display_direction_offset += 1  
        if self.acp.cgd and self.acp.cgd.display_board_count > 1:
            self.acp.cgd.display_board()

    def add(self, arrow):
        """ Add element
        :arrow: arrow element ArrowElemtnt
        """
        self.history.append(arrow)

    def get_display_fun(self):
        display_choice_d = {1: self.md_display_arrows_line,
                            2: self.md_display_arrows_growing,
                            3: self.md_display_long_spike}
        disp_num = self.get_display_move_direction_number()
        disp_num = 1        # Force beginning
        disp_num += self.display_direction_offset
        if disp_num not in display_choice_d:
            self.display_direction_offset = 0
            if disp_num + self.display_direction_offset not in display_choice_d:
                disp_num = 1
        if disp_num in display_choice_d:
            display_fun = display_choice_d[disp_num]
        else:
            display_fun = display_choice_d[1] 
        SlTrace.lg(f"direction: {disp_num=} {display_fun=}")
        return display_fun
        
                        
    def md_display(self):
        """ Choose and then make move display
        """
        display_fun = self.get_display_fun() 
        SlTrace.lg(f"direction: {display_fun=}")
        display_fun()
        self.clear_history()

    def get_display_move_direction_number(self):
        """"Get current direction move style number
        """
        return self.acp.get_display_move_direction_number()
        
    def md_display_long_spike(self):            
        dc = wx.PaintDC(self.acp.grid_panel)
        
        for arrow in self.history:
            if arrow.from_sq is None or arrow.to_sq is None:
                continue  # Ignore as moves
            
            from_center = self.acp.square_center(arrow.from_sq)
            to_center = self.acp.square_center(arrow.to_sq)
            pts = (*from_center, *to_center)
            SlTrace.lg(f"add_arrow: {pts=}")
            #self.acp.create_line(*pts, fill=arrow.fill, width=arrow.width,
            #                     **arrow.kwargs)
            # 4 lines from a small square within the origin
            # square to a point at the center of the destination
            # square
            # width is a fraction of square width
            # Add a square to hide the distraction of multiple
            # line beginnings
            
            base_width = self.acp.sq_size/4
            offset = base_width//2
            x_center, y_center = from_center
            p1 = (x_center, y_center+offset)
            p2 = (x_center, y_center-offset)
            p3 = (x_center+offset, y_center)
            p4 = (x_center-offset, y_center)
            p5 = (x_center, y_center+offset//2)
            p6 = (x_center, y_center-offset//2)
            p7 = (x_center+offset//2, y_center)
            p8 = (x_center-offset//2, y_center)
            start_pts = (x_center-offset, y_center-offset,  x_center+offset, y_center+offset)
            for pstart in [p1,p2,p3,p4,p5,p6,p7,p8]:
                pts = (*pstart, *to_center)
                self.acp.create_line(*pts, fill=arrow.fill, width=arrow.width,
                                 **arrow.kwargs)
            ir, ic = self.acp.sq_to_row_col(arrow.from_sq)    
            sq_color = self.acp.dark_sq if (ic+ir)%2==0 else self.acp.light_sq
            dc.SetPen(wx.Pen(sq_color, style=wx.SOLID))
            dc.SetBrush(wx.Brush(sq_color, wx.SOLID))
            boarder_pen = wx.Pen(wx.Colour(0, 0, 0), style=wx.PENSTYLE_TRANSPARENT)
            dc.SetPen(boarder_pen)
            start_fill = sq_color
            self.acp.create_rectangle(*start_pts, fill=start_fill)

            
        for item in self.acp.items:
            self.acp.add_item(item)
        self.acp.display_pending(dc)

    def show_spot(self, spot, label=None, spot_size=1,
                 color="red", label_color="black",
                 include_loc=True, include_sqs=True):
            """Place spot in display - for debugging
            :spot: (x,y) for dot
            :label: optional label
            :color: spot color default: red
            :label_color: default: spot's color
            :include_loc: display location (x,y)
            :include_sqs: include from to sqs default: False
            """
            if not test_spot:
                return
            
            if label_color is None:
                label_color = color

            spot_x, spot_y = spot
            
            oval_off = spot_size//2
            if oval_off < 1:
                oval_off = 1
            oval_ul = (spot_x-oval_off, spot_y-oval_off)
            oval_lr = spot_x+oval_off, spot_y+oval_off
            self.acp.create_oval(*oval_ul, *oval_lr, fill=color)
            title_sep = 3
            ch_w = 10       # Estimated character width (HACK)
            title_pt = (oval_lr[0]+title_sep, oval_ul[1])
            if label is not None:
                self.acp.create_text(*title_pt, text=label, fill=color)
            if include_loc:
                title_pt = (title_pt[0]+len(label)*ch_w, title_pt[1])
                loc_text = f"({int(spot_x)}, {int(spot_y)})"
                self.acp.create_text(*title_pt, text=loc_text, fill=label_color)
                
            if include_sqs and self.to_sq is not None:
                """TBD"""
            SlTrace.lg(f"show_spot({self.int_list(spot)} {label} {self.from_sq} to {self.to_sq})")
                
    def md_display_arrows_growing(self):
        """ Display direction as a narrow band of > from the from
        sq middle to the middle of the to square, possibly with an increasing
        or decreasing width
        """            
        dc = wx.PaintDC(self.acp.grid_panel)
        
        for arrow in self.history:
            if arrow.from_sq is None or arrow.to_sq is None:
                continue  # Ignore as moves
            
            self.from_sq = arrow.from_sq        # latest - for debugging
            self.to_sq = arrow.to_sq
            from_center = self.acp.square_center(arrow.from_sq)
            to_center = self.acp.square_center(arrow.to_sq)
            chg_x = to_center[0] - from_center[0]
            chg_y = to_center[1] - from_center[1]
            direction_angle = math.atan2(chg_y, chg_x)
            arrow_sep = self.acp.sq_size*.5
            shaft_length = arrow_sep*.7
            line_start = self.add_len(from_pt=from_center, direction_angle=direction_angle,
                                      add_length=shaft_length)
            shaft_width = int(arrow_sep//8)
            arrow_spots = self.inner_points(from_point=line_start, to_point=to_center,
                sep=arrow_sep)
            direction_time = .5 # Time  for direction showing
            dt_per = direction_time/len(arrow_spots)
            for arrow_index, arrow_spot in enumerate(arrow_spots):
                if arrow_index < len(arrow_spots)-1:
                    arrow_color = "blue"
                else:
                    arrow_color = "black" if arrow.moves=="white" else "white"
                self.display_arrow(head_pt=arrow_spot,
                                direction_angle=direction_angle,
                                shaft_length=shaft_length,
                                shaft_width=shaft_width,
                                arrow_color = arrow_color)
                self.do_items()
                #self.acp.Refresh()
                self.acp.Update()
                time.sleep(dt_per)
    
    def do_items(self):
        """ Run over items"""        
        dc = wx.PaintDC(self.acp.grid_panel)
        for item in self.acp.items:
            self.acp.add_item(item)
        self.acp.display_pending(dc)
                
    def md_display_arrows_line(self):
        """ Display fixed set of arrows from orig sq to dest squ
        sq middle to the middle of the to square, possibly with an increasing
        or decreasing width
        """            
        dc = wx.PaintDC(self.acp.grid_panel)
        
        for arrow in self.history:
            if arrow.from_sq is None or arrow.to_sq is None:
                continue  # Ignore as moves
            
            self.from_sq = arrow.from_sq        # latest - for debugging
            self.to_sq = arrow.to_sq
            from_center = self.acp.square_center(arrow.from_sq)
            to_center = self.acp.square_center(arrow.to_sq)
            chg_x = to_center[0] - from_center[0]
            chg_y = to_center[1] - from_center[1]
            direction_angle = math.atan2(chg_y, chg_x)
            arrow_sep = self.acp.sq_size*.5
            shaft_length = arrow_sep*.7
            line_start = self.add_len(from_pt=from_center, direction_angle=direction_angle,
                                      add_length=shaft_length)
            shaft_width = int(arrow_sep//8)
            arrow_spots = self.inner_points(from_point=line_start, to_point=to_center,
                sep=arrow_sep)
            
            for arrow_index, arrow_spot in enumerate(arrow_spots):
                if arrow_index < len(arrow_spots)-1:
                    arrow_color = "blue"
                else:
                    arrow_color = "black" if arrow.moves=="white" else "white"
                self.display_arrow(head_pt=arrow_spot,
                                direction_angle=direction_angle,
                                shaft_length=shaft_length,
                                shaft_width=shaft_width,
                                arrow_color = arrow_color)
                
        self.do_items()
        '''            
        for item in self.acp.items:
            self.acp.add_item(item)
        self.acp.display_pending(dc)
        '''

    def add_len(self, from_pt, direction_angle,
                        add_length):
        """ Add length to point in a direction
        :from_pt: (x,y) beginning point
        :direction_angle: direction in radians
        :add_length: length to add
        :returns: (x_new,y_new) result
        """
        from_pt_x, from_pt_y = from_pt
        chg_x = math.cos(direction_angle)*add_length
        chg_y = math.sin(direction_angle)*add_length     # y decreases
        to_pt_x = from_pt_x + chg_x
        to_pt_y = from_pt_y + chg_y
        to_pt = (to_pt_x, to_pt_y)
        return to_pt

    def display_arrow(self, head_pt, direction_angle, point_angle_deg=80,
                                head_length=None, head_line_width=5,
                                shaft_length=None, shaft_width=5,
                                arrow_color="blue"):
        """ Display arrow head (<)
        :head_pt: arrow  head point location
        :direction_angle: arrow pointing direction radians
        :point_angle_deg: arrow sharpness, separtion of edge lines (degree)
        :head_length: length of head default: sq size/4
        :head_line_width: head line width default: 2
        :shaft_length: Length of shaft default: twice head length
        :line_width: line width in pixels default: 4
        :arrow_color:  arrow color default: blue
        """
        self.show_spot(head_pt, "head_pt")
        if shaft_length is None:
            shaft_length = self.acp.sq_size/4
            
        if head_length is None:
            head_length = shaft_length/2
            
        head_angle_offset_rad = math.radians(point_angle_deg/2)
        head_top_angle = direction_angle - head_angle_offset_rad 
        head_bottom_angle = direction_angle + head_angle_offset_rad
        head_pt_x, head_pt_y = head_pt
        head_top_line_end_x = head_pt_x - math.cos(-head_top_angle)*head_length
        head_top_line_end_y = head_pt_y + math.sin(-head_top_angle)*head_length     # y decreases
        head_top_line_end = (head_top_line_end_x, head_top_line_end_y)
        head_top_line_pts = (*head_pt, *head_top_line_end)
        head_bottom_line_end_x = head_pt_x - math.cos(-head_bottom_angle)*head_length
        head_bottom_line_end_y = head_pt_y + math.sin(-head_bottom_angle)*head_length        # y decreases
        head_bottom_line_end = (head_bottom_line_end_x, head_bottom_line_end_y)
        head_bottom_line_pts = (*head_pt, *head_bottom_line_end)
        
        shaft_end_x = head_pt_x - math.cos(-direction_angle)*shaft_length
        shaft_end_y = head_pt_y + math.sin(-direction_angle)*shaft_length       # y decreases
        shaft_end = (shaft_end_x, shaft_end_y)
        self.show_spot(shaft_end, "shaft end")
        shaft_pts = (*head_pt, *shaft_end)
         
        self.acp.create_line(*self.int_list(head_top_line_pts), fill=arrow_color, width=int(head_line_width))
        self.acp.create_line(*self.int_list(head_bottom_line_pts), fill=arrow_color, width=int(head_line_width))
        self.acp.create_line(*self.int_list(shaft_pts), fill=arrow_color, width=int(shaft_width))
        

    def int_list(self, lst):
        """ because wx and others don't like floats
        :list: of not ints
        :returns: list of ints
        """
        int_list = [int(x) for x in lst ]
        return int_list
    
    def inner_points(self, from_point, to_point, sep,
                     adjust_for_equal=True):
        """ Generate list of separated points between two ends
        :from_point: starting point
        :to_point: ending point
        :sep: separation between pointgs
        :adjust_for_equal: After getting sep (separation of points),
            adjust this slightly upward to provide equally separated
            points - from from_point to to_point
            This gives equally spaced points between from_point to
            to_point
        :returns: list (x,y) tuples
        """
        start_x, start_y = from_point
        end_x, end_y = to_point
        chg_x = end_x - start_x
        chg_y = end_y - start_y
        direction_angle = math.atan2(chg_y, chg_x)
        cos_angle = math.cos(direction_angle)
        sin_angle = math.sin(direction_angle)
        inc_x = sep * cos_angle
        inc_y = sep * sin_angle
        dist = 0
        end_dist = math.sqrt(chg_x**2+chg_y**2)
        if adjust_for_equal:
            n_arrow = int(end_dist/sep)
            if n_arrow < 1:
                n_arrow = 1
            sep = end_dist/n_arrow
        inner_points = []
        while True:
            if dist > end_dist:
                break
            x = dist*cos_angle
            y = dist*sin_angle
            inner_points.append((start_x+x, start_y+y))
            dist += sep
        return inner_points    

class AnotatedChessPanel(ChessCanvasPanel):
    def __init__(self,
                 parent=None,
                 **kwargs,       # passed to ChessCanvasPanel -> wx.Frame                 
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
        super().__init__(parent, **kwargs)
        self.arrow_history = ArrowHistory(self)
        self.grid_panel.Bind(wx.EVT_PAINT, self.OnPaint_acp)    # set to us
        self.set_display_move_direction_number(2)

    def get_display_move_direction_number(self):
        """ Get move direction move number/level
        :returns: display number
        """
        return self.display_move_direction_number

    def set_display_move_direction_number(self, num=1):
        """ Set move direction move number/level
        :num: level default: 1
        """
        self.display_move_direction_number = num
        
    def clear_arrow_history(self):
        """ Clear arrow display
        """
        self.arrow_history.clear_history()
        
    def OnPaint_acp(self, event):
        """ Handle wx.EVT_PAINT
        Do parent's OnPaint then our stuff
        """
        super().OnPaint(event)
        self.arrow_history.md_display()

    def sq_to_row_col(self, sq):
        """ Convert sq to (irow,icol)
        :sq: square e.g e4
        :returns: irow, icol
        """
        file, rank = sq[0], sq[1]
        icol = ord(file)-ord('a')
        irow = ord(rank)-ord('1')
        return irow, icol        

    def square_center (self, sq):
        """ Display piece in square
        :sq: piece-square e.g. e8
        returns (x,y) of square center
        """            
        sq_file = sq[0]
        sq_rank = sq[1]
        ic = ord(sq_file)-ord('a')
        ir = int(sq_rank)-1
        sq_bounds = self.squares_bounds[ic,ir]
        ul_cx1, ul_cy1, lr_cx2, lr_cy2 = sq_bounds
        c_x = (ul_cx1+lr_cx2)//2
        c_y = (ul_cy1+lr_cy2)//2
        return c_x,c_y


    def add_arrow(self, from_sq, to_sq, fill="red", width=5,
                  **kwargs):
        """ Add arrow annotation to list which will
        be displayed on display update (OnPaint)
        :from_sq: from square, e.g. e2
        :to_sq: to square e.g., e4
        :fill: color fill default: "red"
        :width: line width default: 10 pixels
        :**kwargs: additional attributes
        """
        if from_sq is None or to_sq is None:
            SlTrace.lg("add_arrow: {from_sq=} {to_sq=} ignored")
            return
        
        history_element = ArrowElement(from_sq=from_sq, to_sq=to_sq,
                                       kwargs=kwargs)
        self.arrow_history.add(history_element)

if __name__ == '__main__':
    from graphics_braille.select_trace import SlTrace
    from chessboard import Chessboard
    from wx_chess_canvas_panel import ChessCanvasPanel
        
    SlTrace.clearFlags()
    pieces = ':Kc1Qe1kh7 w'
    
    #pieces_list = pieces_list[0:1]  # TFD - In tkinter version,second board loses images
    #pieces_list *= 2
    cbds = []
    cBd = None
    cbds.append(cBd)
    
    def test_on_cmd(cbd, cmd, *args, **kwargs):
        SlTrace.lg(f"{cmd = } {args = } {kwargs = }")

    ccs = None
    app = wx.App()        
    width = int(80*8+80*1.3)
    height = int(80*8+80*2.5)
    frame = wx.Frame(None, size=wx.Size(width,height)) 
    cb = Chessboard(pieces=pieces)
    SlTrace.lg(f"After pieces={pieces}")
    #ccp = ChessCanvasPanel()
    from_sq ="e1"
    to_sq = "g3"
    SlTrace.lg(f"Annotated move {from_sq=} {to_sq=}")
    chess_pan = AnotatedChessPanel(parent=frame, title="AnotatedChessPanel Test", board=cb)
    #chess_pan.set_display_move_direction_number(2)
    chess_pan.Refresh()
    chess_pan.Update()
    chess_pan.add_arrow(from_sq=from_sq, to_sq=to_sq)
    from_sq = "a8"
    to_sq = "g1"
    SlTrace.lg(f"Annotated move {from_sq=} {to_sq=}")
    chess_pan.add_arrow(from_sq=from_sq, to_sq=to_sq)
    from_sq = "h6"
    to_sq = "h7"
    SlTrace.lg(f"Annotated move {from_sq=} {to_sq=}")
    chess_pan.add_arrow(from_sq=from_sq, to_sq=to_sq)
    from_sq = "b1"
    to_sq = "c1"
    SlTrace.lg(f"Annotated move {from_sq=} {to_sq=}")
    chess_pan.add_arrow(from_sq=from_sq, to_sq=to_sq)
    chess_pan.Refresh()
    chess_pan.Update()
    app.MainLoop()
