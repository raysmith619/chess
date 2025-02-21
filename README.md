# Chess notes
## Introduction
I started this work to explore working with chess in the programming world.  My intention was not to compeate
with the major chess programms available. My inspiration was my friend John's Java Script program to display some simple
chess checkmate examples.  I'm still humbled by the fact that his whole program is executable directly from my email!
My first progress was the display of chessboard positions.  The input consists of the, incomplete, FEN chess notation.  Showing that
"lazyness is the mother of invention", I added support for a few pieces on the board, e.g., ':Kc1Qe1kh7 w' for white king at c1,
white queen at e1, black king at h7 with white to move.

## Goals
My intention is to develop some tools to interpret, execute, and display chess games/situations.  While not striving to produce
chess machinery, I hope to experiment a lot.  With the potential of producing serious chess machinery
with resonable display capabilities, I hope to separate display from execution.  I hope to provide support for the blind,
similar to my work in 



### Some views
Current display code uses Python's tkinter module.  In the future I plan to migrate
to wxPython, mainly because wxPython is more compatible with todays screen readers
such as JAWS and NVDIA.  My guess is that tkinter predates the modern APIs that aid
screen readers and other accessibility code which benefits the blind.
#### Chess Board Display
![Simple Chess Display](Docs/simple_chess_board_wp.png)

## Chess Attributes Views
Although the game of chess is intertwined with different aspects we
can divide to conquer.   The following divisions have been helpful to me.

### Notation - Computer input and output
It is often helpful to facilitate the input and output of chess moves and positions.
We will restrict ourselves to what is termed algebraic notation.
* squares: <lowercase letter a-h
   denoting file (column) 1-8 from left to right from white's view>
   <digit 1-8 denoting rank (row) from bottom to top fom white's view>
** a1 - white square at left, lower corner of board from white's view
** h8 - white square at right, upper corner of board from whites view
* piece in square: letter k,q,r,b,n,p for black king,queen,rook,knight,pawn and 
                          K,Q,R,B,N,P for white king,queen,rook,knight,pawn
  e.g, Ka1 - white king at square a1
* chess move: <Upper case piece K,Q,R,B,N,P><destination square>
  e.g, Kf1 - king moves to f1.
* chess move abreviations:
  specification is usually abreviated: In pawn moves the 
# Notation self test
# Chess piece movement testing

# resource_lib
## Common files / support for other projects
Contains files used to support other projects.
Provides logging, tracing, properties support.


## Brief listing of document files (Docs directory)
- Program_Logging_Tracing.pptx PowerPoint presentation about Logging/Tracing demonstrating the classes SlTrace and TraceControlWindow
## Brief listing of source files (src directory) with purpose.
- select_error.py General local, to our program/game, error class
- select_trace.py class SlTrace
  * trace/logging package
  * derived from smTrace.java (ours)
  * properties file support
