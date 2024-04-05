from typing import Iterable, TextIO
import chess.pgn
import haskellian.either as E

def read_all(pgn: TextIO) -> Iterable[chess.pgn.Game | None]:
  """Read all games from a PGN file"""
  while (game := chess.pgn.read_game(pgn)) is not None:
      yield game