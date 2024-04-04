from typing import Literal
from pydantic import BaseModel

class FEN(BaseModel):
  position: str
  turn: Literal['w', 'b']
  castling: str
  passant: str
  plyClock: int
  fullMoves: int

def parse(fen: str) -> FEN:
  position, turn, castling, passant, plyClock, fullMoves = fen.split(' ')
  return FEN(position=position, turn=turn, castling=castling, passant=passant, plyClock=plyClock, fullMoves=fullMoves)

def position_idx(fen: str | FEN) -> int:
  fen_obj = parse(fen) if isinstance(fen, str) else fen
  return 2*(fen_obj.fullMoves-1) + (0 if fen_obj.turn == 'w' else 1)