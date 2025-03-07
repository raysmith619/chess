#chess_error.py  05Mar2025  crs, Author

class ChessError(Exception):
    def __init__(msg):
        raise Exception(msg)
    