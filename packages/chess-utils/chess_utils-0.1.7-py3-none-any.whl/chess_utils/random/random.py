from typing import Generator
import random
import chess

def move(board: chess.Board, rng = random.Random()) -> chess.Move | None:
  """A random legal move on the given position"""
  moves = list(board.legal_moves)
  if len(moves) == 0:
    return None
  idx = rng.randint(0, len(moves)-1)
  return moves[idx]

def line(position: chess.Board | str = chess.STARTING_FEN, max_depth: int = None, rng = random.Random()) -> Generator[chess.Move, None, chess.Board]:
  """A possibly-infinite line of legal moves, starting at `fen`"""
  board = chess.Board(position) if isinstance(position, str) else position
  mv = move(board)
  while mv is not None and (max_depth is None or board.ply() < max_depth):
    board.push(mv)
    yield mv
    mv = move(board, rng)
  return board

    
def position(fen: str = chess.STARTING_FEN, max_depth: int = 64, rng = random.Random()) -> chess.Board:
  """A random position at `max_depth` from `fen`"""
  board = chess.Board(fen)
  depth = rng.randint(0, max_depth)
  list(line(board, depth, rng))
  return board