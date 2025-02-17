#test_chess_bd_get_move_to_sqs.py   15Feb2025  crs
"""
Chess Testing File - verify chessboard.py get_move_to_sqs function
"""
import os
from select_trace import SlTrace

import chessboard as CB

SlTrace.clearFlags()
SlTrace.setFlags("tests,test_strings,found_sqs")
SlTrace.lg(f"\n\nTesting Starting", "tests")
SlTrace.lg("Simple test on blank board, with bishop in a1 corner", "tests")
cb = CB.Chessboard()
Ba1 = cb.get_move_to_sqs('B', orig_sq='a1')
assert('b2' in Ba1)
assert('h8' in Ba1)
try:
    assert('a2' in Ba1)
    print(f" assert('a2' in Ba1') should fail - a2 is not in {Ba1}")
except:
    pass

SlTrace.lg("Check if only the following squares are found", "tests")
for sq in ['b2','c3','d4','e5','f6','g7','h8']:
    del(Ba1[sq])
try:
    assert(len(Ba1) == 0)
except:
    err = f"Unexpected sqs in Ba1:[{Ba1}]"
    SlTrace.lg(err)
    raise Exception(err)

SlTrace.lg("Check if oponent piece is included and stops scan", "tests")
cb.clear_board()
cb.place_piece('q', 'c3')
B_a1_q = cb.get_move_to_sqs('B', orig_sq='a1')
cb.assert_sqs(sqs=B_a1_q, sq_only="b2 c3")

SlTrace.lg("Check if our piece is not included and stops scan", "tests")
cb.clear_board()
cb.place_piece('Q', 'c3')
B_a1_Q = cb.get_move_to_sqs('B', orig_sq='a1')
cb.assert_sqs(sqs=B_a1_Q, sq_only="b2")

SlTrace.lg("Check b in a8", "tests")
cb.clear_board()
b_a8 = cb.get_move_to_sqs('b', orig_sq='a8')
cb.assert_sqs(sqs=b_a8, sq_only="b7 c6 d5 e4 f3 g2 h1")

SlTrace.lg("Check b in h8", "tests")
cb.clear_board()
B_h8 = cb.get_move_to_sqs('B', orig_sq='h8')
cb.assert_sqs(sqs=B_h8, sq_in="g7 f6 e5 d4 c3 b2 a1", sq_out="h8")

SlTrace.lg("  add r at f6", "tests")
cb.place_piece("r", "f6")
B_h8_r = cb.get_move_to_sqs('B', orig_sq='h8')
cb.assert_sqs(sqs=B_h8_r, sq_only="g7 f6", sq_out="h8 e5 d4 c3 b2 a1")


SlTrace.lg("Check B in h1", "tests")
cb.clear_board()
ba8 = cb.get_move_to_sqs('B', orig_sq='h1')
cb.assert_sqs(sqs=ba8, sq_in="a8 b7 c6 d5 e4 f3 g2", sq_out="h1")

SlTrace.lg("   add P at e4", "tests")
cb.place_piece("N", "e4")

SlTrace.lg("Check r in a1", "tests")
cb.clear_board()
ra1 = cb.get_move_to_sqs('r', 'a1')
cb.assert_sqs(sqs=ra1, sq_only="a2,a3,a4,a5,a6,a7,a8 b1,c1,d1,e1,f1,g1,h1")

SlTrace.lg("    add p a3 P c1")
cb.place_piece('p', 'a3')
cb.place_piece('P', 'c1')
ra1 = cb.get_move_to_sqs('r', 'a1')
cb.assert_sqs(sqs=ra1, sq_in="a2 b1 c1", sq_out="a3 d2")


SlTrace.lg("Check P in e2", "tests")
cb.clear_board()
P_e2 = cb.get_move_to_sqs('P', 'e2')
cb.assert_sqs(sqs=P_e2, sq_only="e3 e4")

SlTrace.lg("    add p d3 P f3")
cb.place_piece('p', 'd3')
cb.place_piece('P', 'f3')
P_e2 = cb.get_move_to_sqs('P', 'e2')
cb.assert_sqs(sqs=P_e2, sq_only="e3 e4 d3")

SlTrace.lg("Check N in a1", "tests")
cb.clear_board()
N_a1 = cb.get_move_to_sqs('N', 'a1')
cb.assert_sqs(sqs=N_a1, sq_only="b3 c2")

SlTrace.lg("    add pb3 Pc2")
cb.place_piece('p', 'b3')
cb.place_piece('P', 'c2')
P_e2_x = cb.get_move_to_sqs('N', 'a1')
cb.assert_sqs(sqs=P_e2_x, sq_only="b3")

SlTrace.lg("Check N in c3", "tests")
cb.clear_board()
N_c3 = cb.get_move_to_sqs('N', 'c3')
cb.assert_sqs(sqs=N_c3, sq_only="a2 a4 b5 d5 e4 e2 d1 b1")

SlTrace.lg("Check N in d4", "tests")
cb.clear_board()
N_d4 = cb.get_move_to_sqs('N', 'd4')
cb.assert_sqs(sqs=N_d4, sq_only="c6 e6 f5 f3 e2 c2 b3 b5")

SlTrace.lg("Check N in e5", "tests")
cb.clear_board()
N_e5 = cb.get_move_to_sqs('N', 'e5')
cb.assert_sqs(sqs=N_e5, sq_only="f7 g6 g4 f3 d3 c4 c6 d7")

SlTrace.lg("Check N in f6", "tests")
cb.clear_board()
N_f6 = cb.get_move_to_sqs('N', 'f6')
cb.assert_sqs(sqs=N_f6, sq_only="g8 h7 h5 g4 e4 d5 d7 e8")

SlTrace.lg("Check N in g7", "tests")
cb.clear_board()
N_g7 = cb.get_move_to_sqs('N', 'g7')
cb.assert_sqs(sqs=N_g7, sq_only="h5 f5 e6 e8")

SlTrace.lg("Check N in h8", "tests")
cb.clear_board()
N_h8 = cb.get_move_to_sqs('N', 'h8')
cb.assert_sqs(sqs=N_h8, sq_only="g6 f7")


#SlTrace.lg("force error")
#cb.assert_sqs(sqs=ba8, sq_in="a1", sq_out="h1 e4 d5 c6 b7 a8", desc="force error")


SlTrace.lg(f"\nEnd test in {os.path.basename(__file__)}")
SlTrace.lg(f"Number of tests: {cb.assert_test_count}")
if cb.assert_fail_count > 0:
    err_count_str = f"{cb.assert_fail_count} FAIL"
    if cb.assert_fail_count % 2 == 0:
        err_count_str += "S"
    SlTrace.lg(err_count_str)
else:
    SlTrace.lg("NO FAILS")

SlTrace.lg()