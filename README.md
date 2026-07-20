# Log Cleaner

Log Cleaner is a small Windows desktop utility for reviewing log files before troubleshooting an incident. It groups multiline log entries, filters them by text or regular expression, highlights useful counts, and lets you copy or export the filtered result. A separate cleanup view can preview old `.log` files and delete them only after an explicit opt-in and confirmation.

Current application version: **1.0.0**.

## Features

- Open `.log`, `.txt`, or other text-based files from the desktop interface.
- Group timestamped entries such as `[2026-07-20 10:00:00]` together with their continuation lines and stack traces.
- Fall back to line-by-line analysis for logs without the timestamp format above.
- Filter by plain text or regular expression, with optional case-sensitive matching.
- Show entry, error, and warning counts before filtering.
- Copy filtered entries to the clipboard or export them to a text file.
- Preview `.log` files recursively before cleanup.
- Reject cleanup paths outside the selected target directory.
- Require explicit delete mode and a confirmation before removing files.
- Display the application version in the window and package a versioned Windows executable.

## Run the Windows executable

GitHub Actions builds a Windows x64 executable after the `Check` and `Test` jobs pass. Open a successful workflow run and download the `log-cleaner-windows-x64` artifact. The executable filename includes the application version, for example:

```text
log-cleaner-v1.0.0-windows-x64.exe
```

The same version is shown in the application title bar and footer.

## Analyze a log

1. Start Log Cleaner.
2. Open the **Analyze logs** tab.
3. Select a log or text file with **Open log**.
4. Enter text in **Filter entries** and press Enter or select **Search**.
5. Enable **Regex** only when the search value should be interpreted as a regular expression.
6. Use **Copy** or **Export results** when you need the filtered entries elsewhere.

Plain-text searches treat characters such as `[`, `(`, and `*` literally. Invalid regular expressions are reported instead of crashing the application.

## Safe log cleanup

Cleanup is intentionally separate from log analysis. The selected input is a **directory**, and only files ending in `.log` below that directory are considered.

In the desktop application:

1. Open **Clean up logs**.
2. Choose the target directory.
3. Select **Preview cleanup**. This is a dry-run and does not delete anything.
4. Review every listed path.
5. Enable **Delete mode** only when the preview is correct.
6. Select **Delete listed logs** and confirm the destructive action.

The cleanup implementation resolves every candidate path and rejects a file if it is outside the selected target directory. Deletion errors are reported clearly and do not hide successful or failed operations.

### Command-line dry-run

The cleanup logic can also be exercised directly from Python. The safe default is a dry-run:

```powershell
python -m log_cleaner.cleanup --target "C:\path\to\logs"
```

The command prints every `.log` file that would be affected and finishes without deleting files.

Actual deletion requires the explicit `--delete` flag:

```powershell
python -m log_cleaner.cleanup --target "C:\path\to\logs" --delete
```

Treat `--delete` as destructive. There is no recycle-bin or undo step in the command-line cleanup path.

## Local development

Requirements:

- Python 3.14.6
- Tkinter, included with the standard CPython Windows installation

Create an environment and install the pinned development dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Run the desktop application:

```powershell
python main.py
```

Run the same validation used by CI:

```powershell
ruff check .
ruff format --check .
python -m pytest
pyinstaller --clean --noconfirm log-cleaner.spec
```

The local PyInstaller output is written to `dist\log-cleaner.exe`. GitHub Actions renames the packaged artifact to include the application version.

## Manual cleanup safety checks

Before relying on a new cleanup build, these manual cases complement the automated tests:

1. Select a directory containing `.log` and `.txt` files. Preview must list only `.log` files and must not modify either file type.
2. Select a directory with nested folders. Preview must include nested `.log` files.
3. Preview a directory, leave **Delete mode** disabled, and verify that deletion cannot be triggered.
4. Enable **Delete mode**, cancel the confirmation dialog, and verify that all files remain.
5. Confirm deletion in a disposable test directory and verify that `.log` files are removed while non-log files remain.
6. Attempt to validate a candidate outside the selected target directory and verify that it is rejected.
7. Test a directory where a log cannot be deleted because of permissions and verify that the error is surfaced clearly.

## Project quality and packaging

Pull requests targeting `master` run three GitHub Actions jobs:

- **Check**: Ruff linting and formatting validation on Python 3.14.6.
- **Test**: pytest coverage for parsing, filtering, dry-run behavior, explicit deletion, path safety, and error reporting.
- **Build Windows EXE**: PyInstaller packaging on Windows x64 after the check and test jobs pass, followed by artifact upload.

Dependabot keeps the pinned Python development tools and GitHub Actions dependencies under review.
