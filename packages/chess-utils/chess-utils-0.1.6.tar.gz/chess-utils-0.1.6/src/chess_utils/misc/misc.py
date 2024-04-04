from typing import Literal
import chess

def unchecked_san(board: chess.Board, move: chess.Move) -> str:
  """Like `board.san(move)` but doesn't include check/mate symbols (about 10x faster)"""
  return board._algebraic_without_suffix(move)

def fen_after(move: chess.Move, board: chess.Board) -> str:
    """FEN after `move` made in `board`"""
    board.push(move)
    succ_fen = board.fen()
    board.pop()
    return succ_fen
  
CapturablePiece = Literal['P', 'N', 'B', 'R', 'Q']

def captured_piece(board: chess.Board, move: chess.Move) -> CapturablePiece | None:
  """The piece captured by `move` on `board` (or `None`)"""
  type = board.piece_type_at(move.to_square)
  return type and chess.piece_symbol(type).upper()