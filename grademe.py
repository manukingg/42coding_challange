from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TIME_LIMIT_SECONDS = 2.0


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


def classify_failure(returncode: int, output: str) -> str:
    lowered = output.lower()

    if "failed to compile solution.c" in lowered:
        return "Compile Error"

    if returncode < 0:
        return "Runtime Error"

    if "segmentation fault" in lowered:
        return "Runtime Error"

    if "function must not mutate input list" in output:
        return "Wrong Answer"

    if "expected returnsize=2" in output:
        return "Wrong Answer"

    if "function returned null" in lowered:
        return "Wrong Answer"

    if "indices must point to two different elements" in lowered:
        return "Wrong Answer"

    if "out of range for nums=" in lowered:
        return "Wrong Answer"

    if "expected " in lowered or "assert" in lowered:
        return "Wrong Answer"

    return "Failed"


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
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "--tb=short", str(test_file)],
                capture_output=True,
                text=True,
                timeout=TIME_LIMIT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            timeout_output = (exc.stdout or "") + (exc.stderr or "")
            report = "Time Limit Exceeded\n\n"
            report += f"The tests did not finish within {TIME_LIMIT_SECONDS:.1f} seconds."
            if timeout_output.strip():
                report += "\n\nCaptured output:\n" + timeout_output.strip()
            traceback_file.write_text(report + "\n")
            print(f"Time Limit Exceeded. Details written to {traceback_file.name}.")
            return 1

        output = result.stdout + result.stderr
        if result.returncode == 0:
            if traceback_file.exists():
                traceback_file.unlink()
            print("Accepted.")
        else:
            status = classify_failure(result.returncode, output)
            report = f"{status}\n\n{build_failure_report(output)}\n"
            traceback_file.write_text(report)
            print(f"{status}. Details written to {traceback_file.name}.")
        return result.returncode
    finally:
        clean_pycache(challenge_dir)


if __name__ == "__main__":
    raise SystemExit(main())
