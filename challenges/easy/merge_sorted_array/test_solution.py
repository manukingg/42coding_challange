import ctypes
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parent
SOLUTION_FILE = CHALLENGE_DIR / "solution.c"


@pytest.fixture(scope="session")
def compiled_merge_sorted_array() -> ctypes.CDLL:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.fail("`gcc` is required to run C challenge tests but was not found in PATH.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        library_path = Path(tmp_dir) / "libmerge_sorted_array.so"
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
        library.merge.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
        ]
        library.merge.restype = None
        yield library


def run_merge(
    compiled_merge_sorted_array: ctypes.CDLL,
    nums1: list[int],
    m: int,
    nums2: list[int],
    n: int,
) -> tuple[list[int], list[int]]:
    nums1_array = (ctypes.c_int * len(nums1))(*nums1)
    nums2_array = (ctypes.c_int * max(1, len(nums2)))(*nums2) if nums2 else (ctypes.c_int * 1)()

    compiled_merge_sorted_array.merge(nums1_array, m, nums2_array, n)

    return list(nums1_array), list(nums2_array)[: len(nums2)]


def assert_valid_merge_result(
    result_nums1: list[int],
    original_nums2: list[int],
    result_nums2: list[int],
    expected: list[int],
) -> None:
    assert (
        result_nums1 == expected
    ), f"Expected nums1={expected!r}, got nums1={result_nums1!r}"
    assert (
        result_nums2 == original_nums2
    ), f"Function must not mutate nums2; expected {original_nums2!r}, got {result_nums2!r}"


@pytest.mark.parametrize(
    ("nums1", "m", "nums2", "n", "expected"),
    [
        ([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3, [1, 2, 2, 3, 5, 6]),
        ([1], 1, [], 0, [1]),
        ([0], 0, [1], 1, [1]),
        ([2, 0], 1, [1], 1, [1, 2]),
        ([4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3, [1, 2, 3, 4, 5, 6]),
        ([1, 2, 4, 5, 6, 0], 5, [3], 1, [1, 2, 3, 4, 5, 6]),
        ([1, 0, 0, 0], 1, [2, 3, 4], 3, [1, 2, 3, 4]),
        ([2, 2, 3, 0, 0, 0], 3, [1, 2, 2], 3, [1, 2, 2, 2, 2, 3]),
        ([-3, -1, 2, 0, 0, 0], 3, [-2, 0, 5], 3, [-3, -2, -1, 0, 2, 5]),
        ([0, 0, 0], 0, [2, 5, 6], 3, [2, 5, 6]),
        ([1, 2, 3, 0, 0, 0], 3, [4, 5, 6], 3, [1, 2, 3, 4, 5, 6]),
        ([4, 0, 0, 0], 1, [1, 2, 3], 3, [1, 2, 3, 4]),
    ],
    ids=[
        "official-example-1",
        "official-example-2",
        "official-example-3",
        "insert-before-existing",
        "all-second-array-smaller",
        "insert-in-middle",
        "single-initial-value",
        "duplicate-values",
        "negative-and-positive",
        "first-array-empty",
        "all-second-array-larger",
        "single-large-first-value",
    ],
)
def test_merge_sorted_array(
    compiled_merge_sorted_array: ctypes.CDLL,
    nums1: list[int],
    m: int,
    nums2: list[int],
    n: int,
    expected: list[int],
) -> None:
    original_nums2 = nums2.copy()
    result_nums1, result_nums2 = run_merge(compiled_merge_sorted_array, nums1, m, nums2, n)
    assert_valid_merge_result(result_nums1, original_nums2, result_nums2, expected)


def test_merge_sorted_array_preserves_sorted_order(
    compiled_merge_sorted_array: ctypes.CDLL,
) -> None:
    nums1 = [1, 3, 7, 0, 0, 0, 0]
    nums2 = [2, 4, 5, 6]
    expected = [1, 2, 3, 4, 5, 6, 7]

    result_nums1, result_nums2 = run_merge(
        compiled_merge_sorted_array, nums1, 3, nums2, 4
    )

    assert_valid_merge_result(result_nums1, nums2, result_nums2, expected)


def test_merge_sorted_array_handles_many_duplicates(
    compiled_merge_sorted_array: ctypes.CDLL,
) -> None:
    nums1 = [1, 1, 1, 0, 0, 0]
    nums2 = [1, 1, 1]
    expected = [1, 1, 1, 1, 1, 1]

    result_nums1, result_nums2 = run_merge(
        compiled_merge_sorted_array, nums1, 3, nums2, 3
    )

    assert_valid_merge_result(result_nums1, nums2, result_nums2, expected)
