#chess_error.py  05Mar2025  crs, Author

class ChessError(Exception):
    def __init__(self, msg):
        raise Exception(msg)
    