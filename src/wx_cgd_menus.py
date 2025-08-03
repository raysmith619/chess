# wx_cgd_menus.py    09Mar2023  crs, Adapted from resource_lib/src/wx_adw_menus.py

import wx

from select_trace import SlTrace
from wx_trace_control_window import TraceControlWindow


class MenuDisp:
    """ Menu dispatch table entry
    Supporting multiple mode dispatch (e.g, Dropdown item plus command mode)
    """

    def __init__(self, label, command, underline):
        self.label = label
        self.command = command
        self.underline = underline
        self.shortcut = label[underline].lower()
        self.Properties = None


class CgdMenus:
    def __init__(self, fte, frame=None):
        """ Setup menus for ChessGameDisplay
        Setup from front end, from which it gets access to adw
        :fte: (CgdFrontEnd)
        :frame: frame containing menus
        """
        self.fte = fte
        self.adw = fte.adw
        if frame is None:
            frame = wx.Frame(None)
        self.frame = frame
        self.frame.Show()
        
        self.menu_setup()

    def on_alt_a(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_a")

    def on_alt_m(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_m")

    def on_alt_n(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_n")

    def on_alt_f(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_f")

    def on_alt_s(self, _=None):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_s")

    def menu_setup(self):
        """ Setup menu system
        """
        adw = self.adw
        # creating a menu instance
        menubar = wx.MenuBar()
        menu_name_list = [
            "file", "scanning","settings",
            "game", "enter moves", "auxiliary"
            ]
            
        # Settings for each menu heading    
        menus_settings = {
            "file" : {"heading" : "File"},
            "scanning" : {"heading" : "S&canning"},
            "settings" : {"heading" : "Settings"},
            "game" : {"heading" : "Game"},
            "enter moves" : {"heading" : "Enter Moves"},
            "auxiliary" : {"heading" : "Auxiliary"},
        }
        
        """ menus_items defines all the menu drop downs
        SEP - specifies a separator line
        
        "name" specifies name and heading
        if value is a str the heading == name
        else name is a tuple with
            name = tuple[0]
            heading = tuple[1]
        """
        fte = self.fte
        SEP = {"sep": "sep"}    # Menu item separator
          
        menus_items = {
            "file":
                [
                {"name" : "Open",  "cmd" : fte.cmd_file_open},
                {"name" : "Save",  "cmd" : fte.cmd_file_save},
                SEP,
                {"name" : "Log",   "cmd" : fte.cmd_file_log_file},
                {"name" : "Properties",   "cmd" : fte.cmd_file_properties_file},
                SEP,
                {"name" : "E&xit",  "cmd" : fte.cmd_file_exit},
                ],
            "scanning" :
                [
                {"name" : "Help",    "cmd" : fte.scan_help_cmd},
                {"name" : "Files",   "cmd" : fte.cmd_scanning_files},
                {"name" : "Game &S", "cmd" : fte.setting_game_start_cmd},
                {"name" : "Game &E", "cmd" : fte.setting_game_end_cmd},
                ],
            "settings" :
                [
                #         list - only using second - heading
                {"name" : ("help","Help"), "cmd" : fte.settings_help_cmd},
                {"name" : ("hd","&Boards Print"), "cmd" : fte.setting_print_bd_cmd},
                {"name" : ("hd","B&oards No Print"), "cmd" : fte.setting_print_bd_no_cmd},

                {"name" : ("hd","&Move Display"), "cmd" : fte.setting_move_display_cmd},
                {"name" : ("hd","Mo&ve &No Display"), "cmd" : fte.setting_move_display_no_cmd},

                {"name" : ("hd","&Final Position Display"), "cmd" : fte.setting_final_position_display_cmd},
                {"name" : ("hd","F&inal Position No Display"), "cmd" : fte.setting_final_position_display_no_cmd},

                {"name" : ("hd","F&EN Print"), "cmd" : fte.setting_print_fen_cmd},
                {"name" : ("hd","FEN No &Print"), "cmd" : fte.setting_print_fen_no_cmd},
                
                {"name" : ("hd","&Loop Interval"), "cmd" : fte.setting_loop_interval_cmd},
            
                {"name" : ("hd","&Stop on error"), "cmd" : fte.setting_stop_on_error_cmd},
                {"name" : ("hd","NO S&top on error"), "cmd" : fte.setting_no_stop_on_error_cmd},
               ],
            "game" :
                [
                {"name" : "Help", "cmd" : fte.game_help_cmd},
                {"name" : "New Game", "cmd" : fte.new_window_cmd},
                {"name" : "Enter FEN", "cmd" : fte.enter_fen_cmd},
                {"name" : "Goto Move", "cmd" : fte.goto_move_cmd},
                {"name" : "Print FEN", "cmd" : fte.print_fen_cmd},
                {"name" : "P&rint Game", "cmd" : fte.print_game_cmd},
                ],
            "enter moves" :
                [
                {"name" : "Help", "cmd" : fte.enter_moves_help_cmd},
                {"name" : "Enter Moves", "cmd" : fte.enter_moves_cmd},
                ],
            "auxiliary" :
                [
                {"name" : "Trace", "cmd" : fte.trace_menu},
                ],
            
        }
        
        self.frame.SetMenuBar(menubar)
        self.menus_cmd_menu_item = {}   # by menu short cut by cmd short cut
                                        # m[menu_sc][menu_item_sc] = cmd
        
        for menu_name in menu_name_list:
            menu_settings = menus_settings[menu_name]
            menu_heading = menu_settings["heading"]
            if "&" not in menu_heading:
                menu_heading = "&" + menu_heading
            menu_sci = menu_heading.find("&")
            menu_sc = menu_heading[menu_sci+1].lower()
            if menu_sc in self.menus_cmd_menu_item:     # Is shortcut in use ?
                raise Exception(f"Duplicate menu shortcut {menu_sc} for"
                        f" menu {menu_heading}")
            else:
                menu_items_scs = self.menus_cmd_menu_item[menu_sc] = {}
            menu = wx.Menu()
            menubar.Append(menu,  menu_heading)
            menu_items = menus_items[menu_name]
            for menu_item_specs in menu_items:
                if "sep" in menu_item_specs:
                    menu_item = menu.Append(wx.ID_SEPARATOR)
                else:
                    menu_cmd = menu_item_specs["cmd"]
                    name_heading = menu_item_specs["name"]
                    if isinstance(name_heading,str):
                        menu_item_heading = menu_item_name = name_heading
                    elif len(name_heading)==1:
                        menu_item_name = menu_item_heading = name_heading[0]
                    elif len(name_heading) == 2:
                        menu_item_name = name_heading[0]
                        menu_item_heading = name_heading[1]
                    if "&" not in menu_item_heading:
                        menu_item_heading = "&" + menu_item_heading
                    menui_sci = menu_item_heading.find("&")
                    menui_sc = menu_item_heading[menui_sci+1].lower()
                    if menui_sc in menu_items_scs:
                        raise Exception(f"Duplicate menu {menu_heading} item {menu_item_heading}"
                                        f" \nshortcut {menui_sc}"
                                f" \nshortcuts in use {list(menu_items_scs)}")
                    else:
                        menu_items_scs[menui_sc] = menu_cmd
   
                    menu_item = menu.Append(wx.ID_ANY, menu_item_heading)
                self.frame.Bind(wx.EVT_MENU, menu_cmd, menu_item)

    def get_menu_cmd(self, menu_sc, mi_sc):
        """ get menu cmd
        :menu_cs: menu shortcut case insensitive
        :mi_cs: menu item shortcut case insensitive
        :returns: menu cmd, if none - None
        """
        menu_sc = menu_sc.lower()
        if menu_sc not in self.menus_cmd_menu_item:
            return None # no menu shortcut
        mcmis = self.menus_cmd_menu_item[menu_sc]
        if mi_sc not in mcmis:
            return None
        
        return mcmis[mi_sc]

    def get_menu_scs(self):
        """ Get list of menu short cuts
        :returns: list of menu shortcuts
        """
        menu_scs = list(self.menus_cmd_menu_item)
        return menu_scs

    def get_menu_item_scs(self, menu_sc):
        """ Get list of menu item short cuts
        :menu_sc: menu shortcut
        :returns: list of menu itme shortcuts
        """
        if menu_sc not in self.menus_cmd_menu_item:
            return None
        
        menu_items = self.menus_cmd_menu_item[menu_sc]
        return list(menu_items) 
              
        
    def file_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.file_menu.add_command(label=label, command=command,
                                   underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                           underline=underline)

        self.file_dispatch[menu_de.shortcut] = menu_de

    
    def TBD(self, _=None):
        SlTrace.lg("To be developed")

    def LogFile(self, _=None):
        SlTrace.lg("Show LogFile")

    def PropertiesFile(self, _=None):
        SlTrace.lg("Show PropertiesFile")
                
    def file_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.file_dispatch:
            raise Exception(f"file option:{short_cut} not recognized")
        menu_de = self.file_dispatch[short_cut]
        menu_de.command()

    def File_Open_tbd(self):
        print("File_Open_menu to be determined")

    def File_Save_tbd(self):
        print("File_Save_menu to be determined")


    def settings_help_cmd(self, _=None):
        """ Help for settings
        """
        """ Help - list command (Alt-s) commands
        """
        help_str = """
        Help - list settings commands (Alt-s) commands
        h - say this help message
        """
        ###stuff ...
        self.speak_text(help_str)

    """ Game support package
    """

    def game_help_cmd(self, _=None):
        """ Help for Alt-g commands
        """
        """ Help - list command (Alt-m) commands
        """
        help_str = """
        Help - list magnify commands (Alt-m) commands
        N - new game window
        e - enter FEN for new game
        g - go to current game's move number
        p - print FEN for current position
        r - print current full game
        """
        self.speak_text(help_str)

    """ End of Magnify support
    """

    """ Scanning support package
    """

    """ Scanning menu commands  """

    def scan_help_cmd(self, _=None):
        """ Help for Alt-s commands
        """
        """ Help - list command (Alt-s) commands
        """
        help_str = """
        H - list scanning commands (Alt-s) commands
        f - scan ie play games found in files within the selected directory
        """
        self.speak_text(help_str)

    def scan_files_cmd(self, _=None):
        print("TBD")

    """
    Trace support
    """

    def trace_menu(self, _=None):
        TraceControlWindow()

    """
    Links to front end 
    """
    
    """
    General
    """

    def erase_pos_history(self, _=None):
        self.fte.erase_pos_history()

    def speak_text(self, msg, dup_stdout=True,
                   msg_type=None,
                   rate=None, volume=None):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :msg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9
            
        """
        self.fte.speak_text(msg=msg, msg_type=msg_type,
                            dup_stdout=dup_stdout,
                            rate=rate, volume=volume)

    """
     File links
      most local
    """

    def pgm_exit(self, _=None):
        self.fte.pgm_exit()


    """
    ############################################################
                       Links to fte (then to adw)
    ############################################################
    """


if __name__ == "__main__":
    import sys
    from unittest.mock import MagicMock
    
    class CgdFake(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def exit(self):
            SlTrace.lg("adw.exit()")
            sys.exit()
        
        def get_ix_min(self):
            return 100
                  
    app = wx.App()
    frame = wx.Frame(None)
    cgd = CgdFake()
    menus = CgdMenus(cgd, frame=frame)

    men_scs = menus.get_menu_scs()
    SlTrace.lg(f"Menus: {men_scs}")
    for men_sc in men_scs:
        SlTrace.lg(f"menu {men_sc}")    
        menu_item_scs = menus.get_menu_item_scs(men_sc)    
        SlTrace.lg(f"menu {men_sc} items: {menu_item_scs}")

    SlTrace.lg("Calling each function")
    for men_sc in men_scs:
        SlTrace.lg(f"menu {men_sc}")    
        men_item_scs = menus.get_menu_item_scs(men_sc)
        for menui_sc in men_item_scs:    
            cmd_command = menus.get_menu_cmd(men_sc, menui_sc)
            SlTrace.lg(f"Menu:{men_sc} Item:{menui_sc}", "menu")
            if men_sc == "f" and menui_sc.lower() == "x":
                SlTrace.lg(f"Skipping Menu:{men_sc} Item:{menui_sc}")
                continue
            cmd_command()
            
        
        
