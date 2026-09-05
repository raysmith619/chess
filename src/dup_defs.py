# dup_defs.py   04Sep2026  crs
""" Find duplicate function definitions in a Python file. 
"""
import re
import sys
'''
if len(sys.argv) < 2:
    file_path = input("Enter the path to the Python file: ")
else:
    file_path = sys.argv[1]
'''
file_path = (r"C:\Users\raysm\vscode\chess\src"
            r"\wx_chess_canvas_panel.py")

def find_duplicate_defs(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    defs = {}
    for i, line in enumerate(lines):
        match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
        if match:
            func_name = match.group(1)
            if func_name in defs:
                print(f"Duplicate found for function '{func_name}' at lines {defs[func_name]} and {i+1}")
            else:
                defs[func_name] = i+1
find_duplicate_defs(file_path)
