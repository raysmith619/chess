#test_chess_bd_fen.py    20Mar2025  crs, Author
""" Test Forsyth-Edwards Notation (FEN)
string parsing and production
"""
import os
from select_trace import SlTrace

import chessboard as chb

SlTrace.lg("Standard Initial Board Setup")
cb = chb.Chessboard()   # Standard startup 
cb_str = cb.board_to_fen_str()
SlTrace.lg(cb_str)
if (err:=cb.fen_setup(cb_str)):
    SlTrace.lg(f"Error: {err}")
cb_str2 = cb.board_to_fen_str()
SlTrace.lg(cb_str2)
if cb_str2 != cb_str:
    SlTrace.lg("Error: NO Match")

SlTrace.lg("Empty Board Setup")
cb = chb.Chessboard(standard_setup=False)   # Empty board
cb_str = cb.board_to_fen_str()
SlTrace.lg(cb_str)
if (err:=cb.fen_setup(cb_str)):
    SlTrace.lg(f"Error: {err}")
cb_str2 = cb.board_to_fen_str()
SlTrace.lg(cb_str2)
if cb_str2 != cb_str:
    SlTrace.lg("Error: NO Match")
