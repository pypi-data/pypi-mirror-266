from pydantic import BaseModel
from .styles import Check, Mate, Castle, PawnCapture, PieceCapture
from .classify import is_castle, is_check, is_mate, is_pawn_capture, is_piece_capture
from .map import castle, check, mate, pawn_capture, piece_capture, CapturedPiece

class KingEffects(BaseModel):
  check: Check | None = None
  mate: Mate | None = None

class Motions(BaseModel):
  castle: Castle | None = None
  pawn_capture: PawnCapture | None = None
  piece_capture: PieceCapture | None = None

class Styles(KingEffects, Motions):
  ...

def style_motions(san: str, motions: Motions, captured_piece: CapturedPiece | None = None) -> str:
  if is_pawn_capture(san):
    return pawn_capture(san, motions.pawn_capture or 'dxe4', captured_piece)
  elif is_piece_capture(san):
    return piece_capture(san, motions.piece_capture or 'Nxe4', captured_piece)
  elif is_castle(san):
    return castle(san, motions.castle or 'O-O')
  else:
    return san
  
def style_effects(san: str, effects: KingEffects) -> str:
  if is_check(san):
    return check(san, effects.check or 'NONE')
  elif is_mate(san):
    return mate(san, effects.mate or 'NONE')
  else:
    return san
  
def style(san: str, styles: Styles, captured_piece: CapturedPiece | None = None) -> str:
  return style_effects(style_motions(san, styles, captured_piece), styles)