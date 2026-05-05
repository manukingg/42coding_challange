from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_challenge_dir(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if (candidate / "test_solution.py").is_file():
            return candidate
    return None


def clean_pycache(root: Path) -> None:
    for pycache_dir in root.rglob("__pycache__"):
        for child in pycache_dir.iterdir():
            child.unlink()
        pycache_dir.rmdir()


def main() -> int:
    current_dir = Path.cwd().resolve()
    challenge_dir = find_challenge_dir(current_dir)

    if challenge_dir is None:
        print(
            "grademe must be run from inside a challenge directory "
            "(for example: challenges/easy/two_sum).",
            file=sys.stderr,
        )
        return 1

    test_file = challenge_dir / "test_solution.py"
    print(f"Running tests for {challenge_dir.relative_to(Path.cwd().anchor or challenge_dir)}")

    try:
        result = subprocess.run([sys.executable, "-m", "pytest", str(test_file)])
        return result.returncode
    finally:
        clean_pycache(challenge_dir)


if __name__ == "__main__":
    raise SystemExit(main())
