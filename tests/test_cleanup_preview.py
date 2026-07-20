from __future__ import annotations

from log_cleaner.cleanup import cleanup_logs, delete_log_files


def test_delete_uses_exact_previewed_candidates(tmp_path):
    previewed_log = tmp_path / "previewed.log"
    previewed_log.write_text("previewed", encoding="utf-8")

    preview = cleanup_logs(tmp_path)

    new_log = tmp_path / "created-after-preview.log"
    new_log.write_text("new", encoding="utf-8")

    report = delete_log_files(
        preview.target_dir,
        [candidate.path for candidate in preview.candidates],
    )

    assert report.deleted == (previewed_log.resolve(),)
    assert not previewed_log.exists()
    assert new_log.exists()
