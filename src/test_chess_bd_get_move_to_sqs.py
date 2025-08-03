#test_chess_bd_get_move_to_sqs.py   15Feb2025  crs
"""
Chess Testing File - verify chessboard.py get_move_to_sqs function
"""
import os
from select_trace import SlTrace

import chessboard as cbd
import chess_piece_movement as cpm

# avoiding quotes, another source of typos
r='r'; n='n'; b='b'; q='q'; k='k'; p='p'
a8='a8'; b8='b8'; c8='c8'; d8='d8'; e8='e8'; f8='f8'; g8='g8'; h8='h8'
a7='a7'; b7='b7'; c7='c7'; d7='d7'; e7='e7'; f7='f7'; g7='g7'; h7='h7'
a6='a6'; b6='b6'; c6='c6'; d6='d6'; e6='e6'; f6='f6'; g6='g6'; h6='h6'
a5='a5'; b5='b5'; c5='c5'; d5='d5'; e5='e5'; f5='f5'; g5='g5'; h5='h5'
a4='a4'; b4='b4'; c4='c4'; d4='d4'; e4='e4'; f4='f4'; g4='g4'; h4='h4'
a3='a3'; b3='b3'; c3='c3'; d3='d3'; e3='e3'; f3='f3'; g3='g3'; h3='h3'
a2='a2'; b2='b2'; c2='c2'; d2='d2'; e2='e2'; f2='f2'; g2='g2'; h2='h2'
a1='a1'; b1='b1'; c1='c1'; d1='d1'; e1='e1'; f1='f1'; g1='g1'; h1='h1'
R='R'; N='N'; B='B'; Q='Q'; K='K'; P='P'

SlTrace.clearFlags()
SlTrace.setFlags("tests,test_strings,found_sqs")
SlTrace.lg(f"\n\nTesting Starting")
cb = cbd.Chessboard()
cm = cpm.ChessPieceMovement(cb)

cm.do_test(desc="Check on queen-side castle")
cm.clear_board()
cm.place_piece(R, a1)
cm.place_piece(P,a4)
cm.place_piece(K, e1)
Ke1Ra1 = cm.get_move_to_sqs('K', orig_sq=e1)
cm.assert_sqs(sqs=Ke1Ra1, sq_only=(d1,d2, e2,f2,f1, c1))    # incl castle
cm.do_test(desc2="Check queen's rook on castle") 
Ra1Ke1 = cm.get_move_to_sqs('R', orig_sq=a1)
cm.assert_sqs(sqs=Ra1Ke1, sq_only=(a2,a3, b1,c1,d1))

cm.do_test(desc="Validate piece placement")
cm.clear_board()
cm.place_pieces("Ke1,Rh1, rd4,rg3")
###cm.do_test(desc="-erroneous assert rg4")
###cm.assert_pieces("Ke1,Rh1, rd4,rg3, rg4")
cm.assert_pieces("Ke1,Rh1, rd4,rg3")

cm.do_test(desc2="-remove g3")
cm.remove_piece(g3)
cm.assert_pieces("Ke1,Rh1, rd4")

cm.do_test(desc="Check for passing over check")
cm.clear_board()
cm.place_pieces("Ke1,Rh1, rd4,rf3")
Ke1rd4rg3 = cm.get_move_to_sqs('K', orig_sq=e1)
cm.assert_sqs(Ke1rd4rg3, e2)

cm.do_test(desc="Check castle queenside ending in check")
cm.clear_board()
cm.place_pieces("Ke1,Ra1, rc5")
Ke1Ra1rc5 = cm.get_move_to_sqs('K', orig_sq=e1)
cm.assert_sqs(Ke1Ra1rc5, (d1,d2,e2,f1,f2))

cm.do_test(desc="Check castle king passing through check")
cm.clear_board()
cm.place_pieces("Ke1,Ra1, rd3")
Ke1Ra1rc5 = cm.get_move_to_sqs('K', orig_sq=e1)
cm.assert_sqs(Ke1Ra1rc5, (e2,f1,f2))

cm.do_test(desc="Check castle king starting in check")
cm.clear_board()
cm.place_pieces("Ke1,Ra1, re3")
Ke1Ra1rc5 = cm.get_move_to_sqs('K', orig_sq=e1)
cm.assert_sqs(Ke1Ra1rc5, (d1,d2,f1,f2))

cm.do_test(desc="Simple test on blank board, with bishop in a1 corner")
cm.clear_board()
cm.place_piece(B,a1)
Ba1 = cm.get_move_to_sqs('B', orig_sq='a1')
cm.assert_sqs(Ba1, sq_only=(b2,c3,d4,e5,f6,g7,h8))

cm.do_test(desc="Check if opponent piece is included and stops scan")
cm.clear_board()
cm.place_pieces("Ba1, qc3")
B_a1_q = cm.get_move_to_sqs('B', orig_sq='a1')
cm.assert_sqs(sqs=B_a1_q, sq_only="b2 c3")

cm.do_test(desc="Check if our piece is not included and stops scan")
cm.clear_board()
cm.place_pieces("Ba1")
cm.place_piece('Q', 'c3')
B_a1_Q = cm.get_move_to_sqs('B', orig_sq='a1')
cm.assert_sqs(sqs=B_a1_Q, sq_only="b2")

cm.do_test(desc="Check b in a8")
cm.clear_board()
cm.place_pieces("ba8")
cm.place_pieces("ba8")
b_a8 = cm.get_move_to_sqs('b', orig_sq='a8')
cm.assert_sqs(sqs=b_a8, sq_only="b7 c6 d5 e4 f3 g2 h1")

cm.do_test(desc="Check B in h8")
cm.clear_board()
cm.place_pieces("Bh8")
B_h8 = cm.get_move_to_sqs('B', orig_sq='h8')
cm.assert_sqs(sqs=B_h8, sq_in="g7 f6 e5 d4 c3 b2 a1", sq_out="h8")

cm.do_test(desc2="  add r at f6")
cm.place_piece("r", "f6")
B_h8_r = cm.get_move_to_sqs('B', orig_sq='h8')
cm.assert_sqs(sqs=B_h8_r, sq_only="g7 f6", sq_out="h8 e5 d4 c3 b2 a1")


cm.do_test(desc="Check B in h1")
cm.clear_board()
cm.place_pieces("Bh1")
Bh1 = cm.get_move_to_sqs('B', orig_sq='h1')
cm.assert_sqs(sqs=Bh1, sq_only="a8 b7 c6 d5 e4 f3 g2")

cm.do_test(desc2="   add P at e4")
cm.place_piece("N", "e4")
Bh1_Ne4 = cm.get_move_to_sqs('B', orig_sq='h1')
cm.assert_sqs(sqs=Bh1_Ne4, sq_only="g2 f3")    


cm.do_test(desc="Check Q in a1")
cm.clear_board()
cm.place_pieces("Qa1")
Qa1 = cm.get_move_to_sqs('Q', 'a1')
cm.assert_sqs(sqs=Qa1, sq_only="""
    a2,a3,a4,a5,a6,a7,a8
    b2,c3,d4,e5,f6,g7,h8
    b1,c1,d1,e1,f1,g1,h1""")


cm.do_test(desc="Check r in a1")
cm.clear_board()
cm.place_pieces("ra1")
ra1 = cm.get_move_to_sqs('r', 'a1')
cm.assert_sqs(sqs=ra1, sq_only="a2,a3,a4,a5,a6,a7,a8 b1,c1,d1,e1,f1,g1,h1")

cm.do_test(desc2="    add p a3 P c1")
cm.place_piece('p', 'a3')
cm.place_piece('P', 'c1')
ra1 = cm.get_move_to_sqs('r', 'a1')
cm.assert_sqs(sqs=ra1, sq_only="a2 b1 c1")


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

cm.do_test(desc="Check P in g2")
cm.clear_board()
cm.place_pieces("Pg2")
P_g2 = cm.get_move_to_sqs('P', 'g2')
cm.assert_sqs(sqs=P_g2, sq_only="g3 g4")


cm.do_test(desc="Check P in g2,h2")
cm.clear_board()
cm.place_pieces("Pg2,Ph2")
P_e2 = cm.get_move_to_sqs('P', 'g2')
cm.assert_sqs(sqs=P_e2, sq_only="g3 g4")

cm.do_test(desc="Check P in g2  p in f3 h3")
cm.clear_board()
cm.place_pieces("Pg2,Ph2, pf3, ph3")
P_e2 = cm.get_move_to_sqs('P', 'g2')
cm.assert_sqs(sqs=P_e2, sq_only="f3 g3 g4 h3")


cm.do_test(desc="Check N in a1")
cm.clear_board()
N_a1 = cm.get_move_to_sqs('N', 'a1', add_piece=True)
cm.assert_sqs(sqs=N_a1, sq_only="b3 c2")

cm.do_test(desc2="    add pb3 Pc2")
cm.place_piece('p', 'b3')
cm.place_piece('P', 'c2')
P_e2_x = cm.get_move_to_sqs('N', 'a1', add_piece=True)
cm.assert_sqs(sqs=P_e2_x, sq_only="b3")

cm.do_test(desc="Check N in c3")
cm.clear_board()
N_c3 = cm.get_move_to_sqs('N', 'c3', add_piece=True)
cm.assert_sqs(sqs=N_c3, sq_only="a2 a4 b5 d5 e4 e2 d1 b1")

cm.do_test(desc="Check N in d4")
cm.clear_board()
N_d4 = cm.get_move_to_sqs('N', 'd4', add_piece=True)
cm.assert_sqs(sqs=N_d4, sq_only="c6 e6 f5 f3 e2 c2 b3 b5")

cm.do_test(desc="Check N in e5")
cm.clear_board()
N_e5 = cm.get_move_to_sqs('N', 'e5', add_piece=True)
cm.assert_sqs(sqs=N_e5, sq_only="f7 g6 g4 f3 d3 c4 c6 d7")

cm.do_test(desc="Check N in f6")
cm.clear_board()
N_f6 = cm.get_move_to_sqs('N', 'f6', add_piece=True)
cm.assert_sqs(sqs=N_f6, sq_only="g8 h7 h5 g4 e4 d5 d7 e8")

cm.do_test(desc="Check N in g7")
cm.clear_board()
N_g7 = cm.get_move_to_sqs('N', 'g7', add_piece=True)
cm.assert_sqs(sqs=N_g7, sq_only="h5 f5 e6 e8")

cm.do_test(desc="Check N in h8")
cm.clear_board()
N_h8 = cm.get_move_to_sqs('N', 'h8', add_piece=True)
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
    SlTrace.lg(f"First fail: {cm.get_assert_first_fail()}")
else:
    SlTrace.lg("NO FAILS")

