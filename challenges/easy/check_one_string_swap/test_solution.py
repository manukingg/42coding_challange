import ctypes
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parent
SOLUTION_FILE = CHALLENGE_DIR / "solution.c"


@pytest.fixture(scope="session")
def compiled_check_one_string_swap() -> ctypes.CDLL:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.fail("`gcc` is required to run C challenge tests but was not found in PATH.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        library_path = Path(tmp_dir) / "libcheck_one_string_swap.so"
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
        library.areAlmostEqual.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        library.areAlmostEqual.restype = ctypes.c_bool
        yield library


def run_are_almost_equal(
    compiled_check_one_string_swap: ctypes.CDLL,
    s1: str,
    s2: str,
) -> bool:
    s1_bytes = s1.encode("utf-8")
    s2_bytes = s2.encode("utf-8")
    return bool(
        compiled_check_one_string_swap.areAlmostEqual(
            ctypes.c_char_p(s1_bytes), ctypes.c_char_p(s2_bytes)
        )
    )


@pytest.mark.parametrize(
    ("s1", "s2", "expected"),
    [
        ("bank", "kanb", True),
        ("attack", "defend", False),
        ("kelb", "kelb", True),
        ("abcd", "dcba", False),
        ("abcd", "abdc", True),
        ("aa", "aa", True),
        ("ab", "ba", True),
        ("ab", "ab", True),
        ("abcd", "abcf", False),
        ("qwer", "qewr", True),
        ("aaaaaaabc", "aaaaaaacb", True),
        ("abcdef", "abcdeg", False),
    ],
    ids=[
        "official-example-1",
        "official-example-2",
        "official-example-3",
        "too-many-mismatches",
        "single-swap-fixes-order",
        "all-same-characters",
        "swap-two-character-string",
        "already-equal-short",
        "single-mismatch-impossible",
        "swap-middle-characters",
        "duplicate-characters",
        "last-character-different",
    ],
)
def test_are_almost_equal(
    compiled_check_one_string_swap: ctypes.CDLL,
    s1: str,
    s2: str,
    expected: bool,
) -> None:
    result = run_are_almost_equal(compiled_check_one_string_swap, s1, s2)
    assert result is expected, f"Expected {expected} for s1={s1!r}, s2={s2!r}, got {result}"


def test_are_almost_equal_is_symmetric(
    compiled_check_one_string_swap: ctypes.CDLL,
) -> None:
    s1 = "converse"
    s2 = "convesre"

    forward = run_are_almost_equal(compiled_check_one_string_swap, s1, s2)
    backward = run_are_almost_equal(compiled_check_one_string_swap, s2, s1)

    assert forward is True, f"Expected True for s1={s1!r}, s2={s2!r}, got {forward}"
    assert backward is True, f"Expected True for s1={s2!r}, s2={s1!r}, got {backward}"


def test_are_almost_equal_rejects_three_mismatches(
    compiled_check_one_string_swap: ctypes.CDLL,
) -> None:
    s1 = "abcde"
    s2 = "aecdb"

    result = run_are_almost_equal(compiled_check_one_string_swap, s1, s2)

    assert result is False, f"Expected False for s1={s1!r}, s2={s2!r}, got {result}"
