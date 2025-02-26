#exam_menu_list.py
import tkinter as tk

mw = tk.Tk()

variable = tk.StringVar(mw)
variable.set("one") # default value

w = tk.OptionMenu(mw, variable, "one", "two", "three")
w.pack()

tk.mainloop()