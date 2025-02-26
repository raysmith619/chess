#exam_menu_list_ok.py

import tkinter as tk

OPTIONS = [
"Jan",
"Feb",
"Mar"
] #etc

master = tk.Tk()

variable = tk.StringVar(master)
variable.set(OPTIONS[0]) # default value

w = tk.OptionMenu(master, variable, *OPTIONS)
w.pack()

def ok():
    print ("value is:" + variable.get())

button = tk.Button(master, text="OK", command=ok)
button.pack()

tk.mainloop()