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
        library.filterPrimes.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        library.filterPrimes.restype = ctypes.POINTER(ctypes.c_int)
        yield library


def run_filter_primes(
    compiled_filter_prime_numbers: ctypes.CDLL, nums: list[int]
) -> tuple[object, int]:
    nums_array = (ctypes.c_int * max(1, len(nums)))(*nums) if nums else (ctypes.c_int * 1)()
    return_size = ctypes.c_int(0)
    result_ptr = compiled_filter_prime_numbers.filterPrimes(
        nums_array, len(nums), ctypes.byref(return_size)
    )
    return result_ptr, return_size.value


def assert_valid_filter_primes(
    nums: list[int], expected: list[int], result_ptr: object, return_size: int
) -> None:
    assert return_size == len(
        expected
    ), f"Expected returnSize={len(expected)}, got returnSize={return_size}"

    if return_size == 0:
        return

    assert result_ptr, "Function returned NULL even though primes were expected"
    result = [result_ptr[index] for index in range(return_size)]
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
    result_ptr, return_size = run_filter_primes(compiled_filter_prime_numbers, nums)
    assert_valid_filter_primes(nums, expected, result_ptr, return_size)


def test_filter_primes_handles_empty_input(
    compiled_filter_prime_numbers: ctypes.CDLL,
) -> None:
    result_ptr, return_size = run_filter_primes(compiled_filter_prime_numbers, [])
    assert_valid_filter_primes([], [], result_ptr, return_size)


def test_filter_primes_keeps_duplicate_prime_values(
    compiled_filter_prime_numbers: ctypes.CDLL,
) -> None:
    nums = [5, 5, 4, 5, 6, 5]
    expected = [5, 5, 5, 5]

    result_ptr, return_size = run_filter_primes(compiled_filter_prime_numbers, nums)

    assert_valid_filter_primes(nums, expected, result_ptr, return_size)
