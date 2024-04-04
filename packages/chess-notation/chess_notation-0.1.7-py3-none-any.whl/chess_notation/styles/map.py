from typing import Literal
from .styles import Check, Mate, Castle, PawnCapture, PieceCapture

CapturedPiece = Literal['P', 'N', 'B', 'R', 'Q']

def check(san: str, style: Check) -> str:
    match style:
        case 'NONE':
            return san.removesuffix("+")
        case 'CHECK':
            return san

def mate(san: str, style: Mate) -> str:
    match style:
        case 'NONE':
            return san.removesuffix("#")
        case 'SHARP':
            return san
        case 'DOUBLE_CHECK':
            return san.replace("#", "++")

def castle(san: str, style: Castle) -> str:
    match style:
        case 'OO':
            return san.replace("-", "")
        case 'O-O':
            return san

def pawn_capture(
    san: str,
    style: PawnCapture,
    captured_piece: CapturedPiece | None = None,
    pawn: str = "P"
) -> str:
    """Apply pawn capture `style`
    - If `style == PawnCatpure.PxN` but `captured_piece is None`, `san` will be returned as is
    """
    [d, x, e, n, *tail] = san
    rest = "".join(tail)
    match style:
        case 'de':
            return f"{d}{e}{rest}"
        case 'dxe':
            return f"{d}x{e}{rest}"
        case 'de4':
            return f"{d}{e}{n}{rest}"
        case 'dxe4':
            return san
        case 'xe4':
            return f"x{e}{n}{rest}"
        case 'PxN' if captured_piece is not None:
            return f"{pawn}x{str(captured_piece).upper()}{rest}"
        case _:
            return san
        
def piece_capture(san: str, style: PieceCapture, captured_piece: CapturedPiece | None):
    """Apply piece capture `style`
    - If `style == PieceCatpure.NxN` but `captured_piece is None`, `san` will be returned as is
    """
    match style:
        case 'Ne4':
            return san.replace("x", "")
        case 'Nxe4':
            return san
        case 'NxN' if captured_piece is not None:
            # Nxd4 => NxP, but also Nexd4 => NexP (to disambiguate)
            if san[1] == "x": # no disambiguation
                [N, x, d, n, *tail] = san
                rest = "".join(tail)
                return f"{N}x{str(captured_piece).upper()}{rest}"
            else:
                [N, e, x, d, n, *tail] = san
                rest = "".join(tail)
                return f"{N}{e}x{str(captured_piece).upper()}{rest}"
        case _:
            return san
        