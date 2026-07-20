from __future__ import annotations

from log_cleaner.cleanup import main


def test_cli_defaults_to_dry_run_and_requires_delete_flag(tmp_path, capsys):
    log_file = tmp_path / "service.log"
    log_file.write_text("test", encoding="utf-8")

    dry_run_exit = main(["--target", str(tmp_path)])
    dry_run_output = capsys.readouterr().out

    assert dry_run_exit == 0
    assert "[DRY-RUN]" in dry_run_output
    assert "Nothing was deleted" in dry_run_output
    assert log_file.exists()

    delete_exit = main(["--target", str(tmp_path), "--delete"])
    delete_output = capsys.readouterr().out

    assert delete_exit == 0
    assert "[DELETE]" in delete_output
    assert "Deleted 1 file(s)" in delete_output
    assert not log_file.exists()
