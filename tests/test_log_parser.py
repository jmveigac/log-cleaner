from __future__ import annotations

import pytest

from log_cleaner.log_parser import InvalidSearchPattern, LogDocument


def test_groups_timestamped_entries_with_continuation_lines(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "[2026-07-20 10:00:00] INFO Started\n"
        "context line\n"
        "[2026-07-20 10:00:01] ERROR Request failed\n"
        "Traceback: boom\n",
        encoding="utf-8",
    )

    document = LogDocument.from_path(log_file)

    assert len(document.entries) == 2
    assert "context line" in document.entries[0]
    assert "Traceback: boom" in document.entries[1]
    assert document.summary.entries == 2
    assert document.summary.errors == 1
    assert document.summary.warnings == 0


def test_plain_text_logs_are_searchable_line_by_line(tmp_path):
    log_file = tmp_path / "plain.txt"
    log_file.write_text("alpha\nbeta warning\ngamma error\n", encoding="utf-8")

    document = LogDocument.from_path(log_file)

    assert document.entries == ["alpha", "beta warning", "gamma error"]
    assert document.search("WARNING") == ["beta warning"]
    assert document.summary.errors == 1
    assert document.summary.warnings == 1


def test_plain_text_search_treats_special_characters_as_literals(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("request [42] failed\nrequest 42 passed\n", encoding="utf-8")
    document = LogDocument.from_path(log_file)

    assert document.search("[42]") == ["request [42] failed"]


def test_regex_and_case_sensitive_search(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("ERROR code=500\nerror code=404\n", encoding="utf-8")
    document = LogDocument.from_path(log_file)

    assert document.search(r"code=5\d\d", regex=True) == ["ERROR code=500"]
    assert document.search("ERROR", case_sensitive=True) == ["ERROR code=500"]


def test_invalid_regex_is_reported(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("hello\n", encoding="utf-8")
    document = LogDocument.from_path(log_file)

    with pytest.raises(InvalidSearchPattern):
        document.search("[", regex=True)
