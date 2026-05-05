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


def build_failure_report(output: str) -> str:
    failed_tests: list[str] = []
    reasons: list[str] = []

    for raw_line in output.splitlines():
        line = raw_line.rstrip()

        if line.startswith("FAILED "):
            failed_test = line[len("FAILED ") :].split(" - ", 1)[0].strip()
            if failed_test and failed_test not in failed_tests:
                failed_tests.append(failed_test)
            continue

        if line.startswith("ERROR "):
            error_name = line[len("ERROR ") :].strip()
            if error_name and error_name not in failed_tests:
                failed_tests.append(error_name)
            continue

        if line.startswith("E       "):
            reason = line[len("E       ") :].strip()
            if reason and reason not in reasons:
                reasons.append(reason)

    if not failed_tests and not reasons:
        return output.strip() or "Tests failed, but no detailed failure message was captured."

    report_lines = ["Tests failed."]

    if failed_tests:
        report_lines.append("")
        report_lines.append("Failed tests:")
        for failed_test in failed_tests:
            report_lines.append(f"- {failed_test}")

    if reasons:
        report_lines.append("")
        report_lines.append("Why it failed:")
        for reason in reasons:
            report_lines.append(f"- {reason}")

    return "\n".join(report_lines)


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
    traceback_file = current_dir / f"{challenge_dir.name}_traceback"

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=short", str(test_file)],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            if traceback_file.exists():
                traceback_file.unlink()
            print("Solution succeeded.")
        else:
            traceback_file.write_text(build_failure_report(output) + "\n")
            print(f"Solution failed. Traceback written to {traceback_file.name}.")
        return result.returncode
    finally:
        clean_pycache(challenge_dir)


if __name__ == "__main__":
    raise SystemExit(main())
