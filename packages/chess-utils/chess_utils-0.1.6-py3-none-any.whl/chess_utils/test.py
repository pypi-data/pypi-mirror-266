import os
base = os.path.dirname(__file__)

try:
  import pytest
  if __name__ == '__main__':
    pytest.main([base, '--verbose'])
except ImportError:
  print(f"Error: can't run tests without the `test` extras. Run `pip install {base}[test]` to install")