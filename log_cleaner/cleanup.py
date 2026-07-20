"""Safe log-file cleanup helpers and command-line entry point."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class UnsafePathError(ValueError):
    """Raised when a cleanup candidate escapes the selected target directory."""


@dataclass(frozen=True, slots=True)
class CleanupCandidate:
    path: Path
    size_bytes: int


@dataclass(frozen=True, slots=True)
class CleanupReport:
    target_dir: Path
    candidates: tuple[CleanupCandidate, ...]
    deleted: tuple[Path, ...]
    errors: tuple[str, ...]
    dry_run: bool


def validate_candidate(target_dir: str | Path, candidate: str | Path) -> Path:
    """Resolve a candidate and reject paths outside the target directory."""
    root = Path(target_dir).expanduser().resolve(strict=True)
    resolved = Path(candidate).expanduser().resolve(strict=True)

    if not root.is_dir():
        raise ValueError(f"Cleanup target is not a directory: {root}")
    if not resolved.is_relative_to(root):
        raise UnsafePathError(f"Path is outside cleanup target: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Cleanup candidate is not a file: {resolved}")
    if resolved.suffix.lower() != ".log":
        raise ValueError(f"Cleanup candidate is not a .log file: {resolved}")

    return resolved


def discover_log_files(target_dir: str | Path) -> tuple[CleanupCandidate, ...]:
    """Find .log files recursively while rejecting symlinks that escape the target."""
    root = Path(target_dir).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Cleanup target is not a directory: {root}")

    candidates: list[CleanupCandidate] = []
    for path in sorted(root.rglob("*.log")):
        resolved = validate_candidate(root, path)
        candidates.append(CleanupCandidate(resolved, resolved.stat().st_size))

    return tuple(candidates)


def delete_log_files(
    target_dir: str | Path,
    candidate_paths: Sequence[str | Path],
) -> CleanupReport:
    """Delete exactly the supplied candidates after revalidating every path."""
    root = Path(target_dir).expanduser().resolve(strict=True)
    deleted: list[Path] = []
    errors: list[str] = []
    candidates: list[CleanupCandidate] = []

    for candidate_path in candidate_paths:
        try:
            safe_path = validate_candidate(root, candidate_path)
            candidates.append(CleanupCandidate(safe_path, safe_path.stat().st_size))
            safe_path.unlink()
            deleted.append(safe_path)
        except (OSError, ValueError) as exc:
            errors.append(f"{candidate_path}: {exc}")

    return CleanupReport(root, tuple(candidates), tuple(deleted), tuple(errors), False)


def cleanup_logs(target_dir: str | Path, *, delete: bool = False) -> CleanupReport:
    """Preview matching logs by default, deleting only when delete=True is explicit."""
    root = Path(target_dir).expanduser().resolve(strict=True)
    candidates = discover_log_files(root)

    if not delete:
        return CleanupReport(root, candidates, (), (), True)

    return delete_log_files(root, [candidate.path for candidate in candidates])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview or delete .log files under a target directory.",
    )
    parser.add_argument("--target", required=True, help="Directory to scan recursively.")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete matching .log files. Without this flag, only preview them.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        report = cleanup_logs(args.target, delete=args.delete)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}")
        return 2

    mode = "DELETE" if args.delete else "DRY-RUN"
    print(f"[{mode}] Target: {report.target_dir}")
    for candidate in report.candidates:
        print(candidate.path)

    if report.dry_run:
        print(f"Would affect {len(report.candidates)} file(s). Nothing was deleted.")
    else:
        print(f"Deleted {len(report.deleted)} file(s).")

    for error in report.errors:
        print(f"Error: {error}")

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
