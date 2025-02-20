#test_chess_bd_get_move_to_sqs.py   15Feb2025  crs
"""
Chess Testing File - verify chessboard.py get_move_to_sqs function
"""
import os
from select_trace import SlTrace

import chessboard as cbd
import chess_piece_movement as cpm

SlTrace.clearFlags()
SlTrace.setFlags("tests,test_strings,found_sqs")
SlTrace.lg(f"\n\nTesting Starting")
cb = cbd.Chessboard()
cm = cpm.ChessPieceMovement(cb)

cm.do_test(desc="Simple test on blank board, with bishop in a1 corner")
Ba1 = cm.get_move_to_sqs('B', orig_sq='a1')
assert('b2' in Ba1)
assert('h8' in Ba1)
try:
    assert('a2' in Ba1)
    print(f" assert('a2' in Ba1') should fail - a2 is not in {Ba1}")
except:
    pass

cm.do_test(desc="Check if only the following squares are found")
for sq in ['b2','c3','d4','e5','f6','g7','h8']:
    del(Ba1[sq])
try:
    assert(len(Ba1) == 0)
except:
    err = f"Unexpected sqs in Ba1:[{Ba1}]"
    SlTrace.lg(err)
    raise Exception(err)

cm.do_test(desc="Check if oponent piece is included and stops scan")
cm.clear_board()
cm.place_piece('q', 'c3')
B_a1_q = cm.get_move_to_sqs('B', orig_sq='a1')
cm.assert_sqs(sqs=B_a1_q, sq_only="b2 c3")

cm.do_test(desc="Check if our piece is not included and stops scan")
cm.clear_board()
cm.place_piece('Q', 'c3')
B_a1_Q = cm.get_move_to_sqs('B', orig_sq='a1')
cm.assert_sqs(sqs=B_a1_Q, sq_only="b2")

cm.do_test(desc="Check b in a8")
cm.clear_board()
b_a8 = cm.get_move_to_sqs('b', orig_sq='a8')
cm.assert_sqs(sqs=b_a8, sq_only="b7 c6 d5 e4 f3 g2 h1")

cm.do_test(desc="Check b in h8")
cm.clear_board()
B_h8 = cm.get_move_to_sqs('B', orig_sq='h8')
cm.assert_sqs(sqs=B_h8, sq_in="g7 f6 e5 d4 c3 b2 a1", sq_out="h8")

cm.do_test(desc2="  add r at f6")
cm.place_piece("r", "f6")
B_h8_r = cm.get_move_to_sqs('B', orig_sq='h8')
cm.assert_sqs(sqs=B_h8_r, sq_only="g7 f6", sq_out="h8 e5 d4 c3 b2 a1")


cm.do_test(desc="Check B in h1")
cm.clear_board()
ba8 = cm.get_move_to_sqs('B', orig_sq='h1')
cm.assert_sqs(sqs=ba8, sq_in="a8 b7 c6 d5 e4 f3 g2", sq_out="h1")

cm.do_test(desc2="   add P at e4")
cm.place_piece("N", "e4")

cm.do_test(desc="Check r in a1")
cm.clear_board()
ra1 = cm.get_move_to_sqs('r', 'a1')
cm.assert_sqs(sqs=ra1, sq_only="a2,a3,a4,a5,a6,a7,a8 b1,c1,d1,e1,f1,g1,h1")

cm.do_test(desc2="    add p a3 P c1")
cm.place_piece('p', 'a3')
cm.place_piece('P', 'c1')
ra1 = cm.get_move_to_sqs('r', 'a1')
cm.assert_sqs(sqs=ra1, sq_in="a2 b1 c1", sq_out="a3 d2")


cm.do_test(desc="Check P in e2")
cm.clear_board()
P_e2 = cm.get_move_to_sqs('P', 'e2')
cm.assert_sqs(sqs=P_e2, sq_only="e3 e4")

cm.do_test(desc2="    add p d3 P f3")
cm.place_piece('p', 'd3')
cm.place_piece('P', 'f3')
P_e2 = cm.get_move_to_sqs('P', 'e2')
cm.assert_sqs(sqs=P_e2, sq_only="e3 e4 d3")

cm.do_test(desc2="    add P e4 - our blocking")
cm.place_piece('P', 'e4')
P_e2_x = cm.get_move_to_sqs('P', 'e2')
cm.assert_sqs(sqs=P_e2_x, sq_only="e3 d3")

cm.do_test(desc2="    add p e4 - opponent blocking")
cm.place_piece('p', 'e4')
P_e2_y = cm.get_move_to_sqs('P', 'e2')
cm.assert_sqs(sqs=P_e2_y, sq_only="e3 d3")

cm.do_test(desc="Check N in a1")
cm.clear_board()
N_a1 = cm.get_move_to_sqs('N', 'a1')
cm.assert_sqs(sqs=N_a1, sq_only="b3 c2")

cm.do_test(desc2="    add pb3 Pc2")
cm.place_piece('p', 'b3')
cm.place_piece('P', 'c2')
P_e2_x = cm.get_move_to_sqs('N', 'a1')
cm.assert_sqs(sqs=P_e2_x, sq_only="b3")

cm.do_test(desc="Check N in c3")
cm.clear_board()
N_c3 = cm.get_move_to_sqs('N', 'c3')
cm.assert_sqs(sqs=N_c3, sq_only="a2 a4 b5 d5 e4 e2 d1 b1")

cm.do_test(desc="Check N in d4")
cm.clear_board()
N_d4 = cm.get_move_to_sqs('N', 'd4')
cm.assert_sqs(sqs=N_d4, sq_only="c6 e6 f5 f3 e2 c2 b3 b5")

cm.do_test(desc="Check N in e5")
cm.clear_board()
N_e5 = cm.get_move_to_sqs('N', 'e5')
cm.assert_sqs(sqs=N_e5, sq_only="f7 g6 g4 f3 d3 c4 c6 d7")

cm.do_test(desc="Check N in f6")
cm.clear_board()
N_f6 = cm.get_move_to_sqs('N', 'f6')
cm.assert_sqs(sqs=N_f6, sq_only="g8 h7 h5 g4 e4 d5 d7 e8")

cm.do_test(desc="Check N in g7")
cm.clear_board()
N_g7 = cm.get_move_to_sqs('N', 'g7')
cm.assert_sqs(sqs=N_g7, sq_only="h5 f5 e6 e8")

cm.do_test(desc="Check N in h8")
cm.clear_board()
N_h8 = cm.get_move_to_sqs('N', 'h8')
cm.assert_sqs(sqs=N_h8, sq_only="g6 f7")


#cm.do_test(desc="force error")
#cm.assert_sqs(sqs=ba8, sq_in="a1", sq_out="h1 e4 d5 c6 b7 a8", desc="force error")


SlTrace.lg(f"\nEnd test in {os.path.basename(__file__)}")
assert_test_count = cm.get_assert_test_count()
cm.do_test(desc=f"Number of tests: {assert_test_count}")
assert_fail_count = cm.get_assert_fail_count()
if assert_fail_count > 0:
    err_count_str = f"{assert_fail_count} FAIL"
    if assert_fail_count % 2 == 0:
        err_count_str += "S"
    SlTrace.lg(err_count_str)
else:
    SlTrace.lg("NO FAILS")

SlTrace.lg()