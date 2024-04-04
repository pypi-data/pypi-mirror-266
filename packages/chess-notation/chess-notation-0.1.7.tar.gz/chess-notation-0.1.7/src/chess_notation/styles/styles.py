from typing import Literal

Check = Literal["NONE", "CHECK"]
Mate = Literal["NONE", "SHARP", "DOUBLE_CHECK"]
Castle = Literal["OO", "O-O"]
PawnCapture = Literal["de", "dxe", "de4", "dxe4", "xe4", "PxN"]
PieceCapture = Literal["Ne4", "Nxe4", "NxN"]
