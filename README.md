# Coding Challenge

C coding challenge environment with a Python-based test runner built around `uv`.

## Setup

1. Install `uv`: https://docs.astral.sh/uv/
2. Make sure `gcc` is installed
3. Sync the environment:

```bash
uv sync
```

## Run Tests

Run all tests:

```bash
uv run pytest
```

Run a single challenge:

```bash
uv run pytest challenges/easy/two_sum/test_solution.py
```

## Structure

```text
challenges/
  easy/
  medium/
  hard/
```

Each challenge folder contains:

- `README.md`: problem statement and examples
- `solution.c`: starter file students edit
- `test_solution.py`: automated checks that compile and validate the C solution

## Current Challenges

- `easy/two_sum`
