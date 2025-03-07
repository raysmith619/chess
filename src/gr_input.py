# gr_input.py   12Aug2021   crs, Catch Return/ENTRY
#               07Mar2019   crs Author
"""
Prompt User and accept input
"""
import tkinter as tk       # Get all tkinter via tk.
from select_trace import SlTrace

def gr_input(prompt="Enter", mw=None, default=None):
    """ Get input from user
    :mw: master widget
        default: create
    :default: default value
    """
    global entry_text
    if mw is None:
        mw = tk.Tk()
        mw.withdraw()
    input_window = tk.Toplevel(mw)
    
    entry_var = tk.StringVar(input_window, default)  # Holds the entry text
    entry_text = None               # Set if OK
   
    def ok_cmd():
        """ Function called  upon "OK" button
        """
        global entry_text
        entry_text = entry_var.get()    # Retrieve
        SlTrace.lg(f"{entry_text = }")
        input_window.quit()                       # Exit tk mainloop
        
    def return_process(event):
        ###print("Processing <Return>")
        ok_cmd()
        
    label = tk.Label(input_window, text=prompt)    # Create Label with prompt
    label.pack(side=tk.LEFT)

    entry = tk.Entry(input_window,
                     textvariable=entry_var, bd=3) # Create Entry space on right
    entry.bind("<Return>", return_process)  # Catch <Return>
    entry.pack(side=tk.LEFT)

    button = tk.Button(input_window, text="OK",
                       command=ok_cmd, fg="blue", bg="light gray")
    button.pack(side=tk.RIGHT)
    input_window.mainloop()                   # Loop till quit
    input_window.destroy()                    # cleanup
    return entry_text 

"""
Testing Code which only gets run if this file is
executed by itself
"""
if __name__ == '__main__':
    from gr_input import gr_input
    inp = gr_input("Enter Number:")
    print(inp, " Entered")



