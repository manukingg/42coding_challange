import ctypes
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parent
SOLUTION_FILE = CHALLENGE_DIR / "solution.c"


@pytest.fixture(scope="session")
def compiled_filter_prime_numbers() -> ctypes.CDLL:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.fail("`gcc` is required to run C challenge tests but was not found in PATH.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        library_path = Path(tmp_dir) / "libfilter_prime_numbers.so"
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
        library.filter_prime_numbers.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        library.filter_prime_numbers.restype = ctypes.POINTER(ctypes.c_int)
        yield library


def run_filter_primes(
    compiled_filter_prime_numbers: ctypes.CDLL, nums: list[int]
) -> object:
    nums_array = (ctypes.c_int * max(1, len(nums)))(*nums) if nums else (ctypes.c_int * 1)()
    return compiled_filter_prime_numbers.filter_prime_numbers(nums_array, len(nums))


def read_result_values(result_ptr: object) -> list[int]:
    if not result_ptr:
        return []

    values: list[int] = []
    index = 0

    while True:
        value = result_ptr[index]
        if value == -1:
            break
        values.append(value)
        index += 1

    return values


def assert_valid_filter_primes(nums: list[int], expected: list[int], result_ptr: object) -> None:
    result = read_result_values(result_ptr)
    assert result == expected, f"Expected {expected!r}, got {result!r}"


@pytest.mark.parametrize(
    ("nums", "expected"),
    [
        ([1, 2, 3, 4, 5, 6], [2, 3, 5]),
        ([8, 9, 10, 12], []),
        ([11, 4, 13, 15, 17], [11, 13, 17]),
        ([2, 2, 2, 4], [2, 2, 2]),
        ([-5, -3, -2, 0, 1, 2], [2]),
        ([29, 30, 31, 32, 33, 37], [29, 31, 37]),
        ([0, 1], []),
        ([97], [97]),
        ([14, 15, 16, 17, 18, 19], [17, 19]),
        ([3, 5, 7, 11], [3, 5, 7, 11]),
        ([20, 21, 22, 23, 24, 25, 26, 27, 28, 29], [23, 29]),
        ([2, 4, 3, 9, 5, 15, 7], [2, 3, 5, 7]),
    ],
    ids=[
        "mixed-small-values",
        "no-primes",
        "primes-in-middle",
        "duplicate-primes",
        "negatives-zero-one",
        "larger-primes",
        "only-zero-and-one",
        "single-prime",
        "two-primes-late",
        "all-primes",
        "sparse-primes",
        "preserve-input-order",
    ],
)
def test_filter_primes(
    compiled_filter_prime_numbers: ctypes.CDLL,
    nums: list[int],
    expected: list[int],
) -> None:
    result_ptr = run_filter_primes(compiled_filter_prime_numbers, nums)
    assert_valid_filter_primes(nums, expected, result_ptr)


def test_filter_primes_handles_empty_input(
    compiled_filter_prime_numbers: ctypes.CDLL,
) -> None:
    result_ptr = run_filter_primes(compiled_filter_prime_numbers, [])
    assert_valid_filter_primes([], [], result_ptr)


def test_filter_primes_keeps_duplicate_prime_values(
    compiled_filter_prime_numbers: ctypes.CDLL,
) -> None:
    nums = [5, 5, 4, 5, 6, 5]
    expected = [5, 5, 5, 5]

    result_ptr = run_filter_primes(compiled_filter_prime_numbers, nums)

    assert_valid_filter_primes(nums, expected, result_ptr)
