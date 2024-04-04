from typing import Literal
from . import Check, Mate, Castle, PawnCapture, PieceCapture

def is_check(san: str) -> bool:
    return "+" in san

def is_mate(san: str) -> bool:
    return "#" in san

def is_pawn_capture(san: str) -> bool:
    return "x" in san and not san[0].isupper()

def is_piece_capture(san: str) -> bool:
    return "x" in san and san[0].isupper()

def is_castle(san: str) -> bool:
    return "-" in san

KingEffect = Literal['mate', 'check']

def king_effect(san_move: str) -> KingEffect | None:
    """Effect a move has on the enemy king: check, mate or none"""
    if is_mate(san_move):
        return 'mate'
    elif is_check(san_move):
        return 'check'

Motion = Literal['castle', 'piece-capture', 'pawn-capture']

def motion(san_move: str) -> Motion | None:
    """Type of motion of a move: castle, piece capture, pawn capture or normal"""
    if is_castle(san_move):
        return 'castle'
    elif is_pawn_capture(san_move):
        return 'pawn-capture'
    elif is_piece_capture(san_move):
        return 'piece-capture'