import chess

def square(e4: str) -> chess.Square:
  """Like `chess.parse_square`, but ~1.8x faster (because it doesn't check and assumes `e4` is a valid string square)"""
  try:
    e, n = e4
    file = ord(e) - ord('a')
    rank = int(n)-1
    return chess.square(file, rank)
  except Exception as e:
    import logging
    logging.getLogger().error(f"Exception parsing square '{e4}'", e)
    return chess.parse_square(uci)

def uci(e2e4: str) -> chess.Move:
  """Like `chess.Move.from_uci` but ~50% faster"""
  try:
    e2 = e2e4[:2]
    e4 = e2e4[2:4]
    promotion = chess.PIECE_SYMBOLS.index(e2e4[4]) if len(e2e4) == 5 else None
    return chess.Move(square(e2), square(e4), promotion=promotion)
  except Exception as e:
    import logging
    logging.getLogger().error(f"Exception parsing uci '{e2e4}'", e)
    return chess.Move.from_uci(e2e4)