from __future__ import annotations

from pathlib import Path

import pytest

from log_cleaner.cleanup import UnsafePathError, cleanup_logs, validate_candidate


def test_cleanup_is_dry_run_by_default(tmp_path):
    log_file = tmp_path / "service.log"
    log_file.write_text("test", encoding="utf-8")
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")

    report = cleanup_logs(tmp_path)

    assert report.dry_run is True
    assert [candidate.path for candidate in report.candidates] == [log_file.resolve()]
    assert report.deleted == ()
    assert log_file.exists()


def test_cleanup_deletes_only_log_files_with_explicit_flag(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    first_log = tmp_path / "first.log"
    second_log = nested / "second.log"
    keep_file = nested / "keep.txt"
    first_log.write_text("one", encoding="utf-8")
    second_log.write_text("two", encoding="utf-8")
    keep_file.write_text("keep", encoding="utf-8")

    report = cleanup_logs(tmp_path, delete=True)

    assert report.dry_run is False
    assert set(report.deleted) == {first_log.resolve(), second_log.resolve()}
    assert report.errors == ()
    assert not first_log.exists()
    assert not second_log.exists()
    assert keep_file.exists()


def test_candidate_outside_target_directory_is_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    outside_log = tmp_path / "outside.log"
    outside_log.write_text("outside", encoding="utf-8")

    with pytest.raises(UnsafePathError):
        validate_candidate(target, outside_log)


def test_non_log_candidate_is_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    text_file = target / "notes.txt"
    text_file.write_text("notes", encoding="utf-8")

    with pytest.raises(ValueError, match=r"not a \.log file"):
        validate_candidate(target, text_file)


def test_cleanup_reports_delete_errors(tmp_path, monkeypatch):
    log_file = tmp_path / "locked.log"
    log_file.write_text("locked", encoding="utf-8")
    original_unlink = Path.unlink

    def failing_unlink(path: Path, *args, **kwargs):
        if path == log_file.resolve():
            raise PermissionError("permission denied")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", failing_unlink)

    report = cleanup_logs(tmp_path, delete=True)

    assert report.deleted == ()
    assert len(report.errors) == 1
    assert "permission denied" in report.errors[0]
    assert log_file.exists()
