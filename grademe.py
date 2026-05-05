from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_challenge_dir(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if (candidate / "test_solution.py").is_file():
            return candidate
    return None


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

    result = subprocess.run([sys.executable, "-m", "pytest", str(test_file)])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
