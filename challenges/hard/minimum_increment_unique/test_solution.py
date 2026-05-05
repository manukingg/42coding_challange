import ctypes
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parent
SOLUTION_FILE = CHALLENGE_DIR / "solution.c"


@pytest.fixture(scope="session")
def compiled_minimum_increment_unique() -> ctypes.CDLL:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.fail("`gcc` is required to run C challenge tests but was not found in PATH.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        library_path = Path(tmp_dir) / "libminimum_increment_unique.so"
        command = [
            gcc,
            "-shared",
            "-fPIC",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-O2",
            str(SOLUTION_FILE),
            "-o",
            str(library_path),
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            stdout = completed.stdout.strip()
            compiler_output = "\n".join(part for part in [stdout, stderr] if part)
            pytest.fail(f"Failed to compile solution.c\n\n{compiler_output}")

        library = ctypes.CDLL(str(library_path))
        library.minIncrementForUnique.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
        ]
        library.minIncrementForUnique.restype = ctypes.c_int
        yield library


def run_min_increment_for_unique(
    compiled_minimum_increment_unique: ctypes.CDLL,
    nums: list[int],
) -> tuple[int, list[int]]:
    nums_array = (ctypes.c_int * len(nums))(*nums)
    result = compiled_minimum_increment_unique.minIncrementForUnique(
        nums_array,
        len(nums),
    )
    return result, list(nums_array)


@pytest.mark.parametrize(
    ("nums", "expected"),
    [
        ([1, 2, 2], 1),
        ([3, 2, 1, 2, 1, 7], 6),
        ([0, 2, 2], 1),
        ([1, 1, 1], 3),
        ([1, 1, 2, 2], 4),
        ([0, 0, 0, 0], 6),
        ([-1, -1, 2], 1),
        ([5, 5, 5, 5, 5], 10),
        ([1, 3, 5, 7], 0),
        ([2, 2, 2, 3, 3, 4], 8),
        ([10, 10, 11, 11, 12, 12], 9),
        ([-3, -3, -2, -2, -1], 4),
    ],
    ids=[
        "official-example-1",
        "official-example-2",
        "single-duplicate",
        "all-same-three-values",
        "two-pairs",
        "all-zeroes",
        "includes-negative-values",
        "all-same-five-values",
        "already-unique",
        "clustered-duplicates",
        "staggered-duplicates",
        "negative-cluster",
    ],
)
def test_min_increment_for_unique(
    compiled_minimum_increment_unique: ctypes.CDLL,
    nums: list[int],
    expected: int,
) -> None:
    result, _ = run_min_increment_for_unique(compiled_minimum_increment_unique, nums)
    assert result == expected, f"Expected {expected} for nums={nums!r}, got {result}"


def test_min_increment_for_unique_handles_empty_array(
    compiled_minimum_increment_unique: ctypes.CDLL,
) -> None:
    result, _ = run_min_increment_for_unique(compiled_minimum_increment_unique, [])
    assert result == 0, f"Expected 0 for empty array, got {result}"


def test_min_increment_for_unique_result_matches_mutated_array(
    compiled_minimum_increment_unique: ctypes.CDLL,
) -> None:
    nums = [2, 2, 3, 3]
    expected_moves = 4

    result, mutated = run_min_increment_for_unique(compiled_minimum_increment_unique, nums)

    assert result == expected_moves, f"Expected {expected_moves} for nums={nums!r}, got {result}"
    assert len(mutated) == len(nums), "The function must keep the array length unchanged"


def test_min_increment_for_unique_large_duplicate_block(
    compiled_minimum_increment_unique: ctypes.CDLL,
) -> None:
    nums = [4, 4, 4, 4, 4, 4]
    expected_moves = 15

    result, _ = run_min_increment_for_unique(compiled_minimum_increment_unique, nums)

    assert result == expected_moves, f"Expected {expected_moves} for nums={nums!r}, got {result}"
