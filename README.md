# Coding Challenge

Python coding challenge environment built around `uv`.

## Setup

1. Install `uv`: https://docs.astral.sh/uv/
2. Sync the environment:

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
- `solution.py`: starter file students edit
- `test_solution.py`: automated checks

## Current Challenges

- `easy/two_sum`
