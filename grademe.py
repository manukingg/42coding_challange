from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TIME_LIMIT_SECONDS = 2.0
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


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
    test_results: list[tuple[str, str]] = []
    failed_tests: list[str] = []

    for raw_line in output.splitlines():
        line = raw_line.rstrip()

        if "::" not in line:
            continue

        normalized_name = line.split("::", 1)[1].strip()

        if " PASSED" in line:
            test_name = normalized_name.split(" PASSED", 1)[0].strip()
            test_results.append((test_name, "Accepted"))
            continue

        if " FAILED" in line:
            test_name = normalized_name.split(" FAILED", 1)[0].strip()
            test_results.append((test_name, "Wrong Answer"))
            failed_tests.append(test_name)
            continue

        if " ERROR" in line:
            test_name = normalized_name.split(" ERROR", 1)[0].strip()
            test_results.append((test_name, "Runtime Error"))
            failed_tests.append(test_name)

    if not test_results:
        return "Test results:\n\n- all tests: Failed"

    report_lines = ["Test results:", ""]
    for test_name, status in test_results:
        report_lines.append(f"- {test_name}: {status}")

    if failed_tests:
        report_lines.append("")
        report_lines.append("Failed tests:")
        for failed_test in dict.fromkeys(failed_tests):
            report_lines.append(f"- {failed_test}")

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


def colorize_status(status: str) -> str:
    if status == "Accepted":
        return f"{GREEN}{status}{RESET}"

    return f"{RED}{status}{RESET}"


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
                [sys.executable, "-m", "pytest", "-vv", "--tb=short", str(test_file)],
                capture_output=True,
                text=True,
                timeout=TIME_LIMIT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            timeout_output = (exc.stdout or "") + (exc.stderr or "")
            report = "Test results:\n\n"
            report += f"- all tests: Time Limit Exceeded\n\n"
            report += f"Time limit: {TIME_LIMIT_SECONDS:.1f} seconds"
            if timeout_output.strip():
                report += "\n\nCaptured output:\n" + timeout_output.strip()
            traceback_file.write_text(report + "\n")
            print(
                f"{colorize_status('Time Limit Exceeded')}. "
                f"Details written to {traceback_file.name}."
            )
            return 1

        output = result.stdout + result.stderr
        if result.returncode == 0:
            if traceback_file.exists():
                traceback_file.unlink()
            print(f"{colorize_status('Accepted')}.")
        else:
            status = classify_failure(result.returncode, output)
            report_body = build_failure_report(output)
            if report_body.strip() == "Test results:\n\n- all tests: Failed":
                report = f"Test results:\n\n- all tests: {status}\n"
            else:
                report = report_body + "\n"
            traceback_file.write_text(report)
            print(f"{colorize_status(status)}. Details written to {traceback_file.name}.")
        return result.returncode
    finally:
        clean_pycache(challenge_dir)


if __name__ == "__main__":
    raise SystemExit(main())
