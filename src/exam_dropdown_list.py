#exam_dropdown_list.py

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Dropdown Listbox Example")

# Data for the dropdown list
options = ["Option 1", "Option 2", "Option 3", "Option 4"]

# Variable to store the selected option
selected_option = tk.StringVar()
selected_option.set(options[0])  # Set the default selected option

# Create the Combobox widget
dropdown = ttk.Combobox(root, textvariable=selected_option, values=options)
dropdown.pack(pady=20)

# Function to display the selected option
def show_selection():
    print("Selected option:", selected_option.get())

# Button to trigger the display function
select_button = tk.Button(root, text="Show Selection", command=show_selection)
select_button.pack()

root.mainloop()