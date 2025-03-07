#list_box.py
import tkinter as tk
from tkinter import messagebox
def add_task():
    task = tk.Entry.get()
    if task:
        tk.listbox.insert(tk.END, task)
        tk.entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "You must enter a task!")
app = tk.Tk()

app.title("Accessible To-Do List")
label =  tk.Label(app, text="Task entry")
label.pack()
entry = tk.Entry(app)
entry.pack(pady=10)
entry.focus_set()
add_button = tk.Button(app, text="Add Task", command=add_task)
add_button.pack(pady=10)
listbox = tk.Listbox(app)
listbox.pack(pady=10)
app.mainloop()
