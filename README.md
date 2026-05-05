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

Or, from inside a challenge folder:

```bash
cd challenges/easy/two_sum
uv run grademe
```

On success, `grademe` prints `Accepted.`.
On failure, it prints a short status such as `Wrong Answer.`, `Compile Error.`,
`Runtime Error.`, or `Time Limit Exceeded.` and writes a compact failure report
to a file like `two_sum_traceback` in the current directory. The report is a
simple per-test status list instead of a raw pytest traceback.

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
- `easy/merge_sorted_array`

## Student Workflow

```bash
git clone https://github.com/manukingg/42coding_challange.git
cd 42coding_challange
uv sync
cd challenges/easy/two_sum
uv run grademe
```
