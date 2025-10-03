run:
    PYTHONTRACEMALLOC=1 PYTHONASYNCIODEBUG=1 uv run python -m sudoku

test *ARGS:
    uv run pytest {{ARGS}}
