"""Log loading, grouping, summarizing, and search helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ENTRY_START_PATTERN = re.compile(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")
ERROR_PATTERN = re.compile(r"\b(error|fatal|critical|exception|traceback)\b", re.IGNORECASE)
WARNING_PATTERN = re.compile(r"\b(warn|warning)\b", re.IGNORECASE)


class InvalidSearchPattern(ValueError):
    """Raised when a regular expression cannot be compiled."""


@dataclass(frozen=True, slots=True)
class LogSummary:
    """High-level information about a loaded log file."""

    entries: int
    errors: int
    warnings: int
    size_bytes: int


class LogDocument:
    """Loaded log file represented as grouped entries."""

    def __init__(self, path: Path, entries: list[str], size_bytes: int) -> None:
        self.path = path
        self.entries = entries
        self.size_bytes = size_bytes

    @classmethod
    def from_path(cls, path: str | Path) -> LogDocument:
        """Load a log or text file from disk."""
        resolved_path = Path(path).expanduser().resolve(strict=True)
        if not resolved_path.is_file():
            raise ValueError(f"Expected a file, got: {resolved_path}")

        content = resolved_path.read_text(encoding="utf-8-sig", errors="replace")
        entries = _group_entries(content.splitlines())
        return cls(resolved_path, entries, resolved_path.stat().st_size)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def summary(self) -> LogSummary:
        errors = sum(bool(ERROR_PATTERN.search(entry)) for entry in self.entries)
        warnings = sum(bool(WARNING_PATTERN.search(entry)) for entry in self.entries)
        return LogSummary(
            entries=len(self.entries),
            errors=errors,
            warnings=warnings,
            size_bytes=self.size_bytes,
        )

    def search(
        self,
        query: str,
        *,
        regex: bool = False,
        case_sensitive: bool = False,
    ) -> list[str]:
        """Return entries matching a text query or regular expression."""
        normalized_query = query.strip()
        if not normalized_query:
            return list(self.entries)

        flags = 0 if case_sensitive else re.IGNORECASE
        pattern_text = normalized_query if regex else re.escape(normalized_query)

        try:
            pattern = re.compile(pattern_text, flags)
        except re.error as exc:
            raise InvalidSearchPattern(str(exc)) from exc

        return [entry for entry in self.entries if pattern.search(entry)]


def _group_entries(lines: list[str]) -> list[str]:
    """Group timestamped entries, falling back to one non-empty entry per line."""
    if not any(ENTRY_START_PATTERN.match(line) for line in lines):
        return [line.strip() for line in lines if line.strip()]

    entries: list[str] = []
    current: list[str] = []

    for line in lines:
        if ENTRY_START_PATTERN.match(line) and current:
            entries.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        value = "\n".join(current).strip()
        if value:
            entries.append(value)

    return entries
