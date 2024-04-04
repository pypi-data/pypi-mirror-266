from .styles import Castle, Check, Mate, PawnCapture, PieceCapture
from .map import castle, check, mate, pawn_capture, piece_capture, CapturedPiece
from .classify import is_castle, is_check, is_mate, is_pawn_capture, is_piece_capture, \
  king_effect, motion, KingEffect, Motion
from .apply import style, style_effects, style_motions, Styles, KingEffects, Motions