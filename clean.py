from __future__ import annotations

from pathlib import Path


def clean_pycache(root: Path) -> int:
    removed = 0

    for pycache_dir in root.rglob("__pycache__"):
        for child in pycache_dir.iterdir():
            child.unlink()
        pycache_dir.rmdir()
        removed += 1

    return removed


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    removed = clean_pycache(repo_root)
    print(f"Removed {removed} __pycache__ director{'y' if removed == 1 else 'ies'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
