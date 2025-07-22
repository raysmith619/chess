#input_gather.py     23Mar2025  crs, From get_input.py
""" Modeless input entering
Facilitate repetitive input action

"""
import tkinter as tk       # Get all tkinter via tk.
from select_trace import SlTrace

class InputGather:
    def __init__(self, call_with_input,
                 validate=None, mw=None,
                 title=None, entry_label=None,
                 clear_on_use=True,
                 display_id=None,
                 xoff=None, yoff=None):
        """ Input number of times, calling function each entry
        :call_with_input: function to call each entry
        :validate: validate function function to call which
                converts value to valid form
                default: no call
        :mw: toplevel if any
            default: create one
        :title: optional window title
        :entry_label: optional label to left of entry
        :clear_on_use: True - clear entry after use
                default: clear
        :display_id: display id to set display
                default: no display_info sent
        :xoff: upper left corner xoffset
        :yoff: upper left corner yoffset
        """
        self.call_with_input = call_with_input
        self.validate = validate
        self.clear_on_use = clear_on_use
        self.display_id = display_id
        if mw is None:
            mw = tk.Tk()
        self.input_window = tk.Toplevel(mw)
        if title:
            self.input_window.title(title)
        self.is_opened = True
        
        if entry_label:                
            label = tk.Label(self.input_window,
                             text=entry_label)    # Create Label with prompt
            label.pack(side=tk.LEFT)
            
        self.entry_var = tk.StringVar(self.input_window)  # Holds the entry text
        self.entry = tk.Entry(self.input_window,
                        textvariable=self.entry_var, bd=3) # Create Entry space on right
        self.entry.bind("<Return>", self.process_input)  # Catch <Return>
        self.entry.pack(side=tk.LEFT)

        ok_button = tk.Button(self.input_window, text="OK",
                        command=self.process_input, fg="blue", bg="light gray")
        ok_button.pack(side=tk.RIGHT)
        if xoff is not None and yoff is not None:
            self.input_window.geometry(f"+{xoff}+{yoff}")
        
    def process_input(self, e=None):
        """ Process current input string,
        calling self.call_with_input with value
        :e: event, not used here
        """
        entry_text = self.entry_var.get()    # Retrieve
        if self.validate is not None:
            change = self.validate(entry_text)
            if change != entry_text:
                entry_text = change
                self.entry_var.set(change)
        self.call_with_input(entry_text)
        if self.clear_on_use:
            if self.is_opened:
                self.entry.delete(0,tk.END)
        
    def close(self):
        """ close window, freeing resources
        """
        self.is_opened = False
        self.input_window.destroy()                    # cleanup

"""
Testing Code which only gets run if this file is
executed by itself
"""
if __name__ == '__main__':
    
    import tkinter as tk
    
    mw = tk.Tk()
    
    ig = None
    
    def test_input(val):
        SlTrace.lg(f"test_input:{val = }")
        if val.lower() == "quit":
            SlTrace.lg("Quitting")
            ig.close()

    ig = InputGather(mw=mw, call_with_input=test_input,
                     title="InputGather Selftest",
                     entry_label="Please Enter move")
    
    mw.mainloop()

