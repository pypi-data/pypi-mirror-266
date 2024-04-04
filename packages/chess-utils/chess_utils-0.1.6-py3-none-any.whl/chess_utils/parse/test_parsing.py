from hypothesis import given, strategies as st
import chess
from .parse import square, uci as parse_uci

@given(st.sampled_from(chess.SQUARE_NAMES))
def test_square(e4: str):
  assert square(e4) == chess.parse_square(e4)
  
@given(st.sampled_from(chess.SQUARE_NAMES), st.sampled_from(chess.SQUARE_NAMES))
def test_uci(e2: str, e4: str):
  uci = f'{e2}{e4}'
  try:
    assert parse_uci(uci) == chess.Move.from_uci(uci)
  except chess.InvalidMoveError:
    ...