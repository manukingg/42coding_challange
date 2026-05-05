import ctypes
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parent
SOLUTION_FILE = CHALLENGE_DIR / "solution.c"


@pytest.fixture(scope="session")
def compiled_two_sum() -> ctypes.CDLL:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.fail("`gcc` is required to run C challenge tests but was not found in PATH.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        library_path = Path(tmp_dir) / "libtwo_sum.so"
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
        library.twoSum.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        library.twoSum.restype = ctypes.POINTER(ctypes.c_int)
        yield library


def run_two_sum(
    compiled_two_sum: ctypes.CDLL, nums: list[int], target: int
) -> tuple[object, int]:
    nums_array = (ctypes.c_int * len(nums))(*nums)
    return_size = ctypes.c_int(0)
    result_ptr = compiled_two_sum.twoSum(
        nums_array, len(nums), target, ctypes.byref(return_size)
    )
    return result_ptr, return_size.value


def assert_valid_two_sum(
    nums: list[int], target: int, result_ptr: object, return_size: int
) -> None:
    assert return_size == 2, f"Expected returnSize=2, got returnSize={return_size}"
    assert result_ptr, "Function returned NULL instead of an array of two indices"

    result = [result_ptr[0], result_ptr[1]]
    left_index, right_index = result

    assert (
        left_index != right_index
    ), f"Indices must point to two different elements, got: {result!r}"
    assert 0 <= left_index < len(
        nums
    ), f"First index {left_index} is out of range for nums={nums!r}"
    assert 0 <= right_index < len(
        nums
    ), f"Second index {right_index} is out of range for nums={nums!r}"

    left_value = nums[left_index]
    right_value = nums[right_index]
    actual_sum = left_value + right_value
    assert actual_sum == target, (
        f"Indices {result!r} point to values {left_value} and {right_value}; "
        f"{left_value} + {right_value} = {actual_sum}, expected {target}"
    )


@pytest.mark.parametrize(
    ("nums", "target"),
    [
        ([2, 7, 11, 15], 9),
        ([3, 2, 4], 6),
        ([3, 3], 6),
        ([-3, 4, 3, 90], 0),
        ([0, 4, 3, 0], 0),
        ([1, 5, 8, 2], 7),
        ([10, -2, 6, 1], 8),
        ([1, 2, 3, 4, 5, 6], 11),
        ([100, 1, 99, 50], 199),
        ([-10, -20, 30, 5], 10),
        ([8, 1, 6, 11, -3], 8),
        ([14, 7, -4, 9, 2], 5),
    ],
    ids=[
        "official-example-1",
        "official-example-2",
        "official-example-3",
        "negative-and-positive",
        "two-zeros",
        "pair-at-ends",
        "includes-negative-value",
        "larger-input",
        "large-values",
        "negative-pair",
        "target-from-middle-values",
        "mixed-sign-values",
    ],
)
def test_two_sum_returns_valid_indices(
    compiled_two_sum: ctypes.CDLL, nums: list[int], target: int
) -> None:
    result_ptr, return_size = run_two_sum(compiled_two_sum, nums, target)
    assert_valid_two_sum(nums, target, result_ptr, return_size)


def test_two_sum_does_not_mutate_input(compiled_two_sum: ctypes.CDLL) -> None:
    nums = [2, 7, 11, 15]
    original = nums.copy()

    run_two_sum(compiled_two_sum, nums, 9)

    assert nums == original, f"Function must not mutate input list; got {nums!r}"


def test_two_sum_prefers_correctness_over_order(
    compiled_two_sum: ctypes.CDLL,
) -> None:
    nums = [1, 9, 5, 7]
    target = 12

    result_ptr, return_size = run_two_sum(compiled_two_sum, nums, target)
    assert_valid_two_sum(nums, target, result_ptr, return_size)
