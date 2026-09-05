# castle_match.py   31Aug2026  crs
"""
Why not match(r"(.*)(O-O|O-O-O)$", move_spec)  ???
"""
import re

# Simple example of
# parsing move, dividing it into  two parts:
# everythig else, particulsr end part
def match_and_sep(pat, st):
    """ split into everything, part
    :pat: full pattern including ellse, part
    :mv: move specification xtring
    """
    match = re.match(pat, st)
    if match:
        print(f"{st=} {pat=} {match.groups()=}")
    else:
        print(f"{st=} {pat=} {match.groups()=}")

mv = "Rhe8+"
desc = (f"{mv=}: Rook on h file moves"
        "to square e8 with check")
print(desc)
match_and_sep(r"^(.*)([+#])$", mv)

print("Now for the castle part")
mv = "O-O-O"
desc = (f"{mv=}: Castle on queen side")
match_and_sep(pat="^(.*)$", st=mv)

print("Oh - | evaluates left to right ...")
pat = "(O-O|O-O-O)"
print(f"Using {pat=} with re.search")
search = re.search(pat, mv)
print(search.groups())
pat = "(O-O-O|O-O)"
print(f"Using {pat=} with re.search")
search = re.search(pat, mv)
print(search.groups())

print("...But if you have $ at the end")
pat = "(O-O|O-O-O)$"
print(f"Using {pat=} with re.search")
search = re.search(pat, mv)
print(search.groups())
print(f" because {pat=} is matched greedily")

print(" ... Back to the original task")
print("Lets try lazy capturing")
desc = (f"{mv=}: Castle on queen side")
lazy_pat = "^(.*?)(O-O|O-O-O)$"
print(f"Using {lazy_pat=}")
match_and_sep(pat=lazy_pat, st=mv)

print("greedy leading capture (.*)")
greedy_pat = "^(.*)(O-O|O-O-O)$"
print(f"Using {greedy_pat=}")
match_and_sep(pat=greedy_pat, st=mv)

print("\nPossibly breaking into multiple matches")
king_pat="O-O"
full_king_pat = f"^(.*)({king_pat})$"
queen_pat="O-O-O"
full_queen_pat = f"^(.*)({queen_pat})$"
for mv in ["O-O-O", "O-O", "e4", "erroneous stuff before O-O"]:
    print(f"{mv=}")
    if re.match(pattern=full_queen_pat, string=mv):     # Longest first
        match_and_sep(pat=full_queen_pat, st=mv)
    elif re.match(pattern=full_king_pat, string=mv):
        match_and_sep(pat=full_king_pat, st=mv)
    else:
        print(f"{mv=} is no castle")