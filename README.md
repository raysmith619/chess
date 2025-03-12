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

## Chess Attributes / Views
Although the game of chess is intertwined with different aspects we
can divide to conquer.   The following divisions have been helpful to me.

### Chess Notation Review - Record of the game
Chess notation is important because, using it we can present and preserve the complete
history of the game.  In a relatively few characters, we can see exactly
how the great chess grandmaster Alexander Alekhine defeted Paul Saladin Leonhardt
on July 23 1910.  Before we review the popular algebraic notation below, remind ourselves
of other notations such as the Descriptive notation (e.g NB3 - knight to biship 3,
Nf3 in Algebraic).  Note, possibly the most concise notation, may be Telegraph
in which each move is represented by four digits which specify the origin square file and rank
with the first two digits and the destination square with the second two digits.  A much more
extensive list and description of chess notation can be found other places, e.g. Wikipedia: https://en.wikipedia.org/wiki/Chess_notation#:~:text=Some%20special%20methods%20of%20notation,into%20a%20composite%20Latin%20word.

#### Algebraic Notation
It is often helpful to facilitate the input and output of chess moves and positions.
We will restrict ourselves to what is termed algebraic notation.
* squares: <lowercase letter a-h
   denoting file (column) 1-8 from left to right from white's view>
   <digit 1-8 denoting rank (row) from bottom to top fom white's view>
   - a1 - white square at left, lower corner of board from white's view
   - h8 - white square at right, upper corner of board from whites view
* piece in square:
  - letter k,q,r,b,n,p for black king,queen,rook,knight,pawn
  -        K,Q,R,B,N,P for white king,queen,rook,knight,pawn
    - Ka1 - white king at square a1
    - ka1 - black king at square a1
* chess move: <Upper case piece K,Q,R,B,N,P><destination square>
  - Kf1 - king moves to f1. (color is determined by who (white or black) is movine
* chess move abreviations: specification is usually abreviated
  - In pawn moves the the explicit piece letter is omitted
  - The orig square is omitted and determined by what piece(s) can move to
    the destination.
  - If more than one piece of the specified type and
    current color can move to the destination, file/rank specifications,
    following the Piece letter are used.

#### Move Notation Parsing
Our primary interest
is in the process of interpreting the abreviations and determining the exact move
specification.  Algebraic notation, unlike Long Algebraic
has a number of abbreviations which provide significant space savings. This is
important because the notation is used constantly in chess play, by chess players
writing down every move.
My description below is a compromise.  My hope is to present to two
audiences, the chess player with little or no programming knowledge and the programmer
with little or now chess knowledge.  I appologize for going over areas that the
reader knowledge or experience exceeds my own.
##### What's in a move
A chess move changes the game state.  In general this state involves the movement of
a chess piece from an origin square to a destination square, possibly involving a capture,
or check/mate or game result.
###### move information
   - Piece (e.g King, Queen, Pawn)
   - Original square (e.g. e1)
   - Destination square
   - Special move (e.g., castle)
   - Optional information (could be infered, but nice to see)
      - capture
      - check / checkmate
      - game result (e.g., 1-0 white win)

###### Our parsing attack
   - Two parts
        - Look at specification alone, with little or no board information
        - Take initial results, combine with board information to complete parsing
   - Notation alone
      - Peal specification like an onion
      - start from right end, removing parts if/when found
         - gather game information off right end
         - Check if check(+), or checkmate(#)
         - Check for special moves, castle (O-O,O-O-O) - done if so
         - Gather destination square
              - file+rank   (e.g., e4)
              - file        (e.g., e:d)
      - starting from left
           - gather piece  (e.g. Knight(N) from Nf3)
                - if no piece, assume pawn move (e.g., e4)
           - collect piece modifier to disambiguate from possibles, e.g., Nbd7
      - After specification parsing we generally know the following:
         - Game result
         - check/checkmate
         - capture
      The previous results could be inferred by the complete parsing + board info
         - Piece type (not including whose move)
         - Destination square or file
         - Special move
    
   - Complete parsing, using board information
   In general the parsing at this point completes the determination of the following:
      - piece(s) to be moved
      - origin square(s) - castle has two
      - destination square(s)
   Parsing steps, using board information: 
        - if castle, complete castle parsing: board info: whose move
        - Complete piece determination: board info: whose move        
        - Complete parsing destination square: resolve file-only spec
        - Complete parsing origin square: board info: what pieces in what squares,
          can move/capture to destination sq
        


##### Programming composition
Because chess move notation is so visible in the process of playing and displaying
chess we have placed our notational move parsing in a class **ChessMoveNotation**.
The primary functions used in parsing a move specification are **decode_spec_parts**
and **decode_complete**.  The function **decode_spec_parts** parses out what can be done with little or no knowledge of the board status  The function **decode_complete** takes the
results of **decode_spec_parts**, plus board knowledge and completes the move spec
parsing.

#### Testing
As part of self testing the chess_move_notation.py file, we produce listings of the various
parts of the process.
##### Just notation parts partial listing
```
move  1:  notation CMN: Nf3  white type:n dest_sq:f3
           notation CMN: Nf6  black type:n dest_sq:f6
 move  2:  notation CMN: c4  white type:p dest_sq:c4
           notation CMN: g6  black type:p dest_sq:g6
 move  3:  notation CMN: Nc3  white type:n dest_sq:c3
           notation CMN: Bg7  black type:b dest_sq:g7
 move  4:  notation CMN: d4  white type:p dest_sq:d4
           notation CMN: O-O  black castle king side dest_sq:None
 move  5:  notation CMN: Bf4  white type:b dest_sq:f4
           notation CMN: d5  black type:p dest_sq:d5
 move  6:  notation CMN: Qb3  white type:q dest_sq:b3
           notation CMN: dxc4  black orig_sq_file:d dest_sq:c4 capture
 move  7:  notation CMN: Qxc4  white type:q dest_sq:c4 capture

```
##### Including partial parse plus using board inforamtion
```
 move  1:  notation CMN: Nf3  white type:n dest_sq:f3
 move  1:  +bd info CMN: Nf3  white N orig_sq:g1 dest_sq:f3
           notation CMN: Nf6  black type:n dest_sq:f6
           +bd info CMN: Nf6  black n orig_sq:g8 dest_sq:f6
 move  2:  notation CMN: c4  white type:p dest_sq:c4
 move  2:  +bd info CMN: c4  white P orig_sq:c2 dest_sq:c4
           notation CMN: g6  black type:p dest_sq:g6
           +bd info CMN: g6  black p orig_sq:g7 dest_sq:g6
 move  3:  notation CMN: Nc3  white type:n dest_sq:c3
 move  3:  +bd info CMN: Nc3  white N orig_sq:b1 dest_sq:c3
           notation CMN: Bg7  black type:b dest_sq:g7
           +bd info CMN: Bg7  black b orig_sq:f8 dest_sq:g7
 move  4:  notation CMN: d4  white type:p dest_sq:d4
 move  4:  +bd info CMN: d4  white P orig_sq:d2 dest_sq:d4
           notation CMN: O-O  black castle king side dest_sq:None
           +bd info CMN: O-O  black castle king side orig_sq:e8 dest_sq:g8
 move  5:  notation CMN: Bf4  white type:b dest_sq:f4
 move  5:  +bd info CMN: Bf4  white B orig_sq:c1 dest_sq:f4
           notation CMN: d5  black type:p dest_sq:d5
           +bd info CMN: d5  black p orig_sq:d7 dest_sq:d5
 move  6:  notation CMN: Qb3  white type:q dest_sq:b3
 move  6:  +bd info CMN: Qb3  white Q orig_sq:d1 dest_sq:b3
           notation CMN: dxc4  black orig_sq_file:d dest_sq:c4 capture
           +bd info CMN: dxc4  black p orig_sq:d5 dest_sq:c4 capture
 move  7:  notation CMN: Qxc4  white type:q dest_sq:c4 capture
 move  7:  +bd info CMN: Qxc4  white Q orig_sq:b3 dest_sq:c4 capture
           notation CMN: c6  black type:p dest_sq:c6
           +bd info CMN: c6  black p orig_sq:c7 dest_sq:c6
 move  8:  notation CMN: e4  white type:p dest_sq:e4
 move  8:  +bd info CMN: e4  white P orig_sq:e2 dest_sq:e4
           notation CMN: Nbd7  black type:n dest_sq:d7
           +bd info CMN: Nbd7  black n orig_sq:b8 dest_sq:d7
```
##### Just the completed move parsing state
```
 move  1:  +bd info CMN: Nf3  white N orig_sq:g1 dest_sq:f3
           +bd info CMN: Nf6  black n orig_sq:g8 dest_sq:f6
 move  2:  +bd info CMN: c4  white P orig_sq:c2 dest_sq:c4
           +bd info CMN: g6  black p orig_sq:g7 dest_sq:g6
 move  3:  +bd info CMN: Nc3  white N orig_sq:b1 dest_sq:c3
           +bd info CMN: Bg7  black b orig_sq:f8 dest_sq:g7
 move  4:  +bd info CMN: d4  white P orig_sq:d2 dest_sq:d4
           +bd info CMN: O-O  black castle king side orig_sq:e8 dest_sq:g8
 move  5:  +bd info CMN: Bf4  white B orig_sq:c1 dest_sq:f4
           +bd info CMN: d5  black p orig_sq:d7 dest_sq:d5
 move  6:  +bd info CMN: Qb3  white Q orig_sq:d1 dest_sq:b3
           +bd info CMN: dxc4  black p orig_sq:d5 dest_sq:c4 capture
 move  7:  +bd info CMN: Qxc4  white Q orig_sq:b3 dest_sq:c4 capture
           +bd info CMN: c6  black p orig_sq:c7 dest_sq:c6
 move  8:  +bd info CMN: e4  white P orig_sq:e2 dest_sq:e4
           +bd info CMN: Nbd7  black n orig_sq:b8 dest_sq:d7
```

### Board display
We provide a graphical chess board display, seen above, using python's tkinter module.
for implementation.
While many chess players will desire a graphic display of the chess board, many
times we prefer a faster, more compact, display.  We provide a printed display, currently
targeted to the blind, to create embossed Braille.  Note that the Braille software we know of
compresses multiple spaces into a single space.  To avoid that compression, with the accompanied
loss of geometry, we use characters quote('), back-quote(`),
and comma(,) which Braille into "space-like", single dot representations.  If time and energy permits, we
plan to provide an alternate printable format for the sighted viewers.
##### Board representations for a fiew moves
```
After Move: 1 white Nf3
8: [ r] [ n] [ b] [ q] [ k] [ b] [ n] [ r]
7: [ p] [ p] [ p] [ p] [ p] [ p] [ p] [ p]
6: ```` '''' ```` '''' ```` '''' ```` ''''
5: '''' ```` '''' ```` '''' ```` '''' ````
4: ```` '''' ```` '''' ```` '''' ```` ''''
3: '''' ```` '''' ```` '''' [.n] '''' ````
2: [.p] [.p] [.p] [.p] [.p] [.p] [.p] [.p]
1: [.r] [.n] [.b] [.q] [.k] [.b] '''' [.r]
------------------------------------------
 , , a ,, b ,, c ,, d ,, e ,, f ,, g ,, h ,

After Move: 1 black Nf6
8: [ r] [ n] [ b] [ q] [ k] [ b] ```` [ r]
7: [ p] [ p] [ p] [ p] [ p] [ p] [ p] [ p]
6: ```` '''' ```` '''' ```` [ n] ```` ''''
5: '''' ```` '''' ```` '''' ```` '''' ````
4: ```` '''' ```` '''' ```` '''' ```` ''''
3: '''' ```` '''' ```` '''' [.n] '''' ````
2: [.p] [.p] [.p] [.p] [.p] [.p] [.p] [.p]
1: [.r] [.n] [.b] [.q] [.k] [.b] '''' [.r]
------------------------------------------
 , , a ,, b ,, c ,, d ,, e ,, f ,, g ,, h ,

After Move: 2 white c4
8: [ r] [ n] [ b] [ q] [ k] [ b] ```` [ r]
7: [ p] [ p] [ p] [ p] [ p] [ p] [ p] [ p]
6: ```` '''' ```` '''' ```` [ n] ```` ''''
5: '''' ```` '''' ```` '''' ```` '''' ````
4: ```` '''' [.p] '''' ```` '''' ```` ''''
3: '''' ```` '''' ```` '''' [.n] '''' ````
2: [.p] [.p] ```` [.p] [.p] [.p] [.p] [.p]
1: [.r] [.n] [.b] [.q] [.k] [.b] '''' [.r]
------------------------------------------
 , , a ,, b ,, c ,, d ,, e ,, f ,, g ,, h ,

After Move: 2 black g6
8: [ r] [ n] [ b] [ q] [ k] [ b] ```` [ r]
7: [ p] [ p] [ p] [ p] [ p] [ p] '''' [ p]
6: ```` '''' ```` '''' ```` [ n] [ p] ''''
5: '''' ```` '''' ```` '''' ```` '''' ````
4: ```` '''' [.p] '''' ```` '''' ```` ''''
3: '''' ```` '''' ```` '''' [.n] '''' ````
2: [.p] [.p] ```` [.p] [.p] [.p] [.p] [.p]
1: [.r] [.n] [.b] [.q] [.k] [.b] '''' [.r]
------------------------------------------
 , , a ,, b ,, c ,, d ,, e ,, f ,, g ,, h ,

...

After Move: 41 white Kc1
8: ```` [.q] ```` '''' ```` '''' ```` ''''
7: '''' ```` '''' ```` '''' [ p] [ k] ````
6: ```` '''' [ p] '''' ```` '''' [ p] ''''
5: '''' [ p] '''' ```` [.n] ```` '''' [ p]
4: ```` [ b] ```` '''' ```` '''' ```` [.p]
3: '''' [ b] [ n] ```` '''' ```` '''' ````
2: [ r] '''' ```` '''' ```` '''' [.p] ''''
1: '''' ```` [.k] ```` '''' ```` '''' ````
------------------------------------------
 , , a ,, b ,, c ,, d ,, e ,, f ,, g ,, h ,

After Move: 41 black Rc2# 0-1
8: ```` [.q] ```` '''' ```` '''' ```` ''''
7: '''' ```` '''' ```` '''' [ p] [ k] ````
6: ```` '''' [ p] '''' ```` '''' [ p] ''''
5: '''' [ p] '''' ```` [.n] ```` '''' [ p]
4: ```` [ b] ```` '''' ```` '''' ```` [.p]
3: '''' [ b] [ n] ```` '''' ```` '''' ````
2: ```` '''' [ r] '''' ```` '''' [.p] ''''
1: '''' ```` [.k] ```` '''' ```` '''' ````
------------------------------------------
 , , a ,, b ,, c ,, d ,, e ,, f ,, g ,, h ,
 
```
##### Latest attempt for printable board of the sighted
Sadly the file and pasted versions of the output do not reflect
the same spaceing shown in the live printed output.  Work will
continue.
```
8: ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜ 
7: ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟ 
6: □  :  □  :  □  :  □  : 
5: :  □  :  □  :  □  :  □ 
4: □  :  □  :  □  :  □  : 
3: :  □  :  □  :  □  :  □ 
2: ♙  ♙  ♙  ♙  ♙  ♙  ♙  ♙ 
1: ♖  ♘  ♗  ♕  ♔  ♗  ♘  ♖ 
--------------------------
   a  b  c  d  e  f  g  h

8: □  :  □  :  □  :  □  : 
7: :  □  :  □  :  □  :  ♚ 
6: □  :  □  :  □  :  □  : 
5: :  □  :  □  :  □  :  □ 
4: □  :  □  :  □  :  □  : 
3: :  □  :  □  :  □  :  □ 
2: □  :  □  :  □  :  □  : 
1: :  □  ♔  □  ♕  □  :  □ 
--------------------------
   a  b  c  d  e  f  g  h

```
###  Board physics
The board contents and opperation should be distinct from the display because
in chess, one often needs to have insight about board positions that never
occurr or are displayed.  For example one might want to know all the possible
moves a piece can make, so as to pick the most advantageous one.
We place most of this operation in a class **Chessboard**, residing in chessboard.py.
A partial list of contents for this class includes initial piece setup,
the current board pieces/locations, which pieces have moved, history of moves to
support "undo" or aid in checking for *en passant*. Some things such as the board size, number of rows
and columns, is set to facilitate the possiblility of chess variants or other games.

#### Piece Movement
As a subsection of "Board Physics" we consider chess piece movement.  We encapsulate
this in the class **ChessPieceMovement**, contained in chess_piece_movement.py.  This
class's most visible function is **get_move_to_sqs**, which returns all the squares
to which a particular piece may move, including any possible captures.  Note that
as in other partitioned systems, this function often has to refer to external
objects such as the Chessboard.
##### Plan for piece movement specificaiton
Our attempt is to provide a concise specification of permissible piece movement, that
is for a specified piece on a specified square, the complete list of squares to which
that piece may move on the current move.  In general we specify,for each piece type, a list of possible directions, change in x(horizonal squares) plus change in y(vertical squares).
The direction changes for black are reversed for the y direction.  As an optimization, because all the
non-pawn direction
lists are symetric (for every entry (x,y) there is a (x,-y), we just add an extra list for the black pawns.
We just choose the black pawn list for black pawns.
Each piece type has
a number of repitions:
  - king, queen, rook, biship: number of row/column in board
  - king, knight: 1
  - pawn:
    - first move: 2 only in dirs labeled "move"
    - after: 1
  - special: king has extra moves possible with castling
- modifications:
Note that these direction repitions are modified by board conditions such as:
  - direction repition is "stopped" at board edge. 
  - direction repition is "stopped" by a piece in the path, keeping the occupied square
 if of the opponent, rejecting the occupied square of own color.

The following small code section impliments the similarity between the moves of king, queen, rook
and bishop.  In particular, the direction list for the queen is created by adding
the direction list for the rook and the bishop.  The direction list for the king
equals that of the queen but the repition for the king is 1.
```
    piece_type_dir_d["q"] =  piece_type_dir_d["r"] + piece_type_dir_d["b"]
    piece_type_dir_d["k"] = piece_type_dir_d["q"] # only one sq
```

Most of the chess piece move ideas mentioned above are implemented in the larger code segment below.
#### code from chess_piece_movement.py
```
class ChessPieceMovement:

    """
    Piece movement
    The following determines the possible piece movement.
    In general, a piece's possible movement is specified by:
        1. list of directions each of the form (x,y,special)
            x is change in file(column)
            y is change in rank(row) (as viewed by white)
            special: "move" - use only if a move
                    "capture" - use only if a capture
        2. repition, number of times which the direction change
           can be applied.
            The number of repititions depends on piece type.
                In the case of pawns: 2 for first move, else 1
                In case of knight: 1
                Others: number of rows or columns
    by piece or piece capture, if different than move
    arranged in clockwise, starting by up/to right
    NOTE: change is in the "forward" direction, negated for black
           As, except for pawns, the lists are symetric in y for
           content - For efficiency/clarity, we provide
           a black pawn list "p-black" which replicates the "p"
           entry with y negated
    As for dir "capture" entries, these entries take effect if
    and only if their use can effect a capture, i.e., the
    destination square is occupied by an opponent.
    EP capture is effect, if the previous opponent move is a
    2-square pawn move jumping the capture square. 
    """      
    piece_type_dir_d = {
        # lists of tuples
        #   PAIR: (X,Y) or TRIPLE: (x,y,"capture"/"move")
        #   "capture" only if move is a capture
        #   "move" only move is not capture
        #   default: move, if empty or capture if not empty
        # pawn:
        #       rep: first move 1, else 2
        "p" : [(0,1,"move"),
               (-1,1, "capture"), (1,1,"capture")],
        # black pawn MUST equal "p" with y entries negated
        "p-black" : [(0,-1,"move"),
            (-1,-1, "capture"), (1,-1,"capture")],
        
        "n" : [(1,2), (2,1), (2,-1), (1,-2),
               (-1,-2), (-2,-1), (-2,1), (-1,2)],
        "b" : [(1,1), (1,-1), (-1,-1), (-1,1)],
        "r" : [(0,1), (1,0), (0,-1), (-1,0)],
    }
    piece_type_dir_d["q"] =  piece_type_dir_d["r"] + piece_type_dir_d["b"]
    piece_type_dir_d["k"] = piece_type_dir_d["q"] # only one sq

```

# File Summary
  - chess_board_display - Chessb - oardDisplay - provides a graphical view of the chessboard
  - chessboard.py - Chessboard - provides support of chess state manipulations
  - chess_save_unit.py - ChessSaveUnit - contents indicating a chess move, with the primary
  supporting undo
  - chess_move.py - ChessMove - support the process of making one chess move
  - chess_piece_movement - ChessPieceMovement - contains knowledge on how pieces move
  - chess_move_notation.py - ChessMoveNotation - facilitates parsing chess move specifications

## Brief listing of document files (Docs directory)
- display .png files
- extended listing / log files 
## resource_lib
### Common files / support for other projects
Contains files used to support other projects.
Provides logging, tracing, properties support.


### Brief listing of source files (src directory) with purpose.
- select_error.py General local, to our program/game, error class
- select_trace.py class SlTrace
  * trace/logging package
  * derived from smTrace.java (ours)
  * properties file support
