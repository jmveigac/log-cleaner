"""Tkinter desktop interface for Log Cleaner."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from log_cleaner.cleanup import CleanupReport, cleanup_logs, delete_log_files
from log_cleaner.log_parser import InvalidSearchPattern, LogDocument
from log_cleaner.version import __version__

BACKGROUND = "#0b1220"
SURFACE = "#111827"
SURFACE_ALT = "#172033"
BORDER = "#263247"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"
ACCENT_ACTIVE = "#0ea5e9"
DANGER = "#ef4444"
DANGER_ACTIVE = "#dc2626"


class LogCleanerApp:
    """Desktop application shell."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.document: LogDocument | None = None
        self.current_results: list[str] = []
        self.cleanup_report: CleanupReport | None = None

        self.file_path = tk.StringVar(value="No log selected")
        self.search_query = tk.StringVar()
        self.regex_enabled = tk.BooleanVar(value=False)
        self.case_sensitive = tk.BooleanVar(value=False)
        self.entries_value = tk.StringVar(value="0")
        self.errors_value = tk.StringVar(value="0")
        self.warnings_value = tk.StringVar(value="0")
        self.matches_value = tk.StringVar(value="0 matches")
        self.analysis_status = tk.StringVar(value="Open a log file to start analyzing.")

        self.cleanup_path = tk.StringVar(value="No folder selected")
        self.cleanup_status = tk.StringVar(
            value="Preview is read-only. Deletion is always an explicit second step."
        )
        self.delete_enabled = tk.BooleanVar(value=False)

        self._configure_window()
        self._configure_styles()
        self._build_layout()

    def _configure_window(self) -> None:
        self.root.title(f"Log Cleaner v{__version__}")
        self.root.geometry("1180x780")
        self.root.minsize(960, 640)
        self.root.configure(background=BACKGROUND)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=BACKGROUND)
        style.configure("Surface.TFrame", background=SURFACE)
        style.configure("Card.TFrame", background=SURFACE_ALT)
        style.configure("TLabel", background=BACKGROUND, foreground=TEXT)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Surface.TLabel", background=SURFACE, foreground=MUTED)
        style.configure(
            "SurfaceTitle.TLabel",
            background=SURFACE,
            foreground=TEXT,
            font=("Segoe UI Semibold", 12),
        )
        style.configure(
            "Title.TLabel",
            font=("Segoe UI Semibold", 20),
            foreground=TEXT,
        )
        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
            foreground=MUTED,
        )
        style.configure(
            "Version.TLabel",
            background=SURFACE_ALT,
            foreground=ACCENT,
            padding=(10, 4),
            font=("Segoe UI Semibold", 9),
        )
        style.configure(
            "Metric.TLabel",
            background=SURFACE_ALT,
            foreground=TEXT,
            font=("Segoe UI Semibold", 18),
        )
        style.configure(
            "MetricCaption.TLabel",
            background=SURFACE_ALT,
            foreground=MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground=BACKGROUND,
            borderwidth=0,
            padding=(14, 8),
            font=("Segoe UI Semibold", 9),
        )
        style.map("Accent.TButton", background=[("active", ACCENT_ACTIVE)])
        style.configure(
            "Danger.TButton",
            background=DANGER,
            foreground="white",
            borderwidth=0,
            padding=(14, 8),
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "Danger.TButton",
            background=[("active", DANGER_ACTIVE), ("disabled", SURFACE_ALT)],
            foreground=[("disabled", MUTED)],
        )
        style.configure(
            "TButton",
            background=SURFACE_ALT,
            foreground=TEXT,
            borderwidth=0,
            padding=(12, 7),
        )
        style.map("TButton", background=[("active", BORDER)])
        style.configure(
            "TEntry",
            fieldbackground=SURFACE_ALT,
            foreground=TEXT,
            insertcolor=TEXT,
            bordercolor=BORDER,
            padding=7,
        )
        style.configure("TCheckbutton", background=BACKGROUND, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", BACKGROUND)])
        style.configure("TNotebook", background=BACKGROUND, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=SURFACE,
            foreground=MUTED,
            padding=(16, 9),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", SURFACE_ALT)],
            foreground=[("selected", TEXT)],
        )
        style.configure(
            "Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=SURFACE_ALT,
            foreground=TEXT,
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", ACCENT_ACTIVE)])

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill=tk.BOTH, expand=True)
        self._build_header(container)

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(14, 10))
        analyzer_tab = ttk.Frame(notebook, padding=16)
        cleanup_tab = ttk.Frame(notebook, padding=16)
        notebook.add(analyzer_tab, text="Analyze logs")
        notebook.add(cleanup_tab, text="Clean up logs")
        self._build_analyzer_tab(analyzer_tab)
        self._build_cleanup_tab(cleanup_tab)

        footer = ttk.Frame(container)
        footer.pack(fill=tk.X)
        ttk.Label(
            footer,
            text="Log Cleaner · focused log analysis and safe cleanup",
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)
        ttk.Label(
            footer,
            text=f"Version {__version__}",
            style="Muted.TLabel",
        ).pack(side=tk.RIGHT)

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent)
        header.pack(fill=tk.X)
        title_area = ttk.Frame(header)
        title_area.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(title_area, text="Log Cleaner", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            title_area,
            text=f"v{__version__}",
            style="Version.TLabel",
        ).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Label(
            header,
            text="Inspect first. Filter quickly. Delete only when you mean it.",
            style="Subtitle.TLabel",
        ).pack(side=tk.RIGHT)

    def _build_analyzer_tab(self, parent: ttk.Frame) -> None:
        file_row = ttk.Frame(parent)
        file_row.pack(fill=tk.X)
        ttk.Label(file_row, text="Log file", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Entry(file_row, textvariable=self.file_path, state="readonly").pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=10,
        )
        ttk.Button(
            file_row,
            text="Open log",
            style="Accent.TButton",
            command=self._select_log,
        ).pack(side=tk.RIGHT)

        metrics = ttk.Frame(parent)
        metrics.pack(fill=tk.X, pady=14)
        self._metric_card(metrics, "Entries", self.entries_value).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 8),
        )
        self._metric_card(metrics, "Errors", self.errors_value).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=4,
        )
        self._metric_card(metrics, "Warnings", self.warnings_value).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(8, 0),
        )

        search_panel = ttk.Frame(parent, style="Surface.TFrame", padding=12)
        search_panel.pack(fill=tk.X)
        ttk.Label(
            search_panel,
            text="Filter entries",
            style="SurfaceTitle.TLabel",
        ).grid(row=0, column=0, sticky=tk.W)
        search_entry = ttk.Entry(search_panel, textvariable=self.search_query)
        search_entry.grid(row=1, column=0, sticky=tk.EW, pady=(6, 0))
        search_entry.bind("<Return>", lambda _event: self._run_search())
        ttk.Checkbutton(
            search_panel,
            text="Regex",
            variable=self.regex_enabled,
        ).grid(row=1, column=1, padx=(10, 0))
        ttk.Checkbutton(
            search_panel,
            text="Case sensitive",
            variable=self.case_sensitive,
        ).grid(row=1, column=2, padx=(10, 0))
        ttk.Button(
            search_panel,
            text="Search",
            style="Accent.TButton",
            command=self._run_search,
        ).grid(row=1, column=3, padx=(10, 0))
        ttk.Button(search_panel, text="Reset", command=self._reset_search).grid(
            row=1,
            column=4,
            padx=(8, 0),
        )
        search_panel.columnconfigure(0, weight=1)

        result_header = ttk.Frame(parent)
        result_header.pack(fill=tk.X, pady=(14, 6))
        ttk.Label(
            result_header,
            textvariable=self.matches_value,
            foreground=ACCENT,
        ).pack(side=tk.LEFT)
        ttk.Button(
            result_header,
            text="Export results",
            command=self._export_results,
        ).pack(side=tk.RIGHT)
        ttk.Button(
            result_header,
            text="Copy",
            command=self._copy_results,
        ).pack(side=tk.RIGHT, padx=(0, 8))

        self.results_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            background="#060b14",
            foreground="#dbeafe",
            insertbackground=TEXT,
            selectbackground=ACCENT_ACTIVE,
            relief=tk.FLAT,
            borderwidth=0,
            padx=14,
            pady=12,
            font=("Consolas", 10),
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.configure(state=tk.DISABLED)
        ttk.Label(
            parent,
            textvariable=self.analysis_status,
            style="Muted.TLabel",
        ).pack(fill=tk.X, pady=(8, 0))

    def _build_cleanup_tab(self, parent: ttk.Frame) -> None:
        notice = ttk.Frame(parent, style="Surface.TFrame", padding=14)
        notice.pack(fill=tk.X)
        ttk.Label(notice, text="Safe cleanup", style="SurfaceTitle.TLabel").pack(anchor=tk.W)
        ttk.Label(
            notice,
            text=(
                "Preview scans only .log files below the selected folder. "
                "Deletion stays disabled until you explicitly enable it and confirm."
            ),
            style="Surface.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        folder_row = ttk.Frame(parent)
        folder_row.pack(fill=tk.X, pady=14)
        ttk.Entry(folder_row, textvariable=self.cleanup_path, state="readonly").pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
        )
        ttk.Button(
            folder_row,
            text="Choose folder",
            command=self._select_cleanup_folder,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            folder_row,
            text="Preview cleanup",
            style="Accent.TButton",
            command=self._preview_cleanup,
        ).pack(side=tk.LEFT, padx=(8, 0))

        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.cleanup_tree = ttk.Treeview(
            table_frame,
            columns=("path", "size"),
            show="headings",
        )
        self.cleanup_tree.heading("path", text="Log file")
        self.cleanup_tree.heading("size", text="Size")
        self.cleanup_tree.column("path", anchor=tk.W, width=760)
        self.cleanup_tree.column("size", anchor=tk.E, width=120, stretch=False)
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.cleanup_tree.yview,
        )
        self.cleanup_tree.configure(yscrollcommand=scrollbar.set)
        self.cleanup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        action_row = ttk.Frame(parent)
        action_row.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(
            action_row,
            textvariable=self.cleanup_status,
            style="Muted.TLabel",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Checkbutton(
            action_row,
            text="Enable delete mode",
            variable=self.delete_enabled,
            command=self._toggle_delete_button,
        ).pack(side=tk.RIGHT, padx=(12, 8))
        self.delete_button = ttk.Button(
            action_row,
            text="Delete listed logs",
            style="Danger.TButton",
            command=self._delete_logs,
            state=tk.DISABLED,
        )
        self.delete_button.pack(side=tk.RIGHT)

    def _metric_card(
        self,
        parent: ttk.Frame,
        caption: str,
        variable: tk.StringVar,
    ) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=(16, 12))
        ttk.Label(card, textvariable=variable, style="Metric.TLabel").pack(anchor=tk.W)
        ttk.Label(card, text=caption, style="MetricCaption.TLabel").pack(anchor=tk.W)
        return card

    def _select_log(self) -> None:
        selected = filedialog.askopenfilename(
            title="Open log file",
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not selected:
            return

        try:
            self.document = LogDocument.from_path(selected)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Unable to open log", str(exc))
            return

        self.file_path.set(str(self.document.path))
        summary = self.document.summary
        self.entries_value.set(str(summary.entries))
        self.errors_value.set(str(summary.errors))
        self.warnings_value.set(str(summary.warnings))
        self.search_query.set("")
        self.current_results = list(self.document.entries)
        self._render_results()
        self.analysis_status.set(
            f"Loaded {self.document.name} · {human_size(summary.size_bytes)}"
        )

    def _run_search(self) -> None:
        if self.document is None:
            messagebox.showinfo("No log selected", "Open a log file before searching.")
            return

        try:
            self.current_results = self.document.search(
                self.search_query.get(),
                regex=self.regex_enabled.get(),
                case_sensitive=self.case_sensitive.get(),
            )
        except InvalidSearchPattern as exc:
            messagebox.showerror("Invalid regular expression", str(exc))
            return

        self._render_results()
        self.analysis_status.set(
            f"Showing {len(self.current_results)} of {len(self.document.entries)} entries."
        )

    def _reset_search(self) -> None:
        self.search_query.set("")
        self.regex_enabled.set(False)
        self.case_sensitive.set(False)
        if self.document is None:
            return
        self.current_results = list(self.document.entries)
        self._render_results()
        self.analysis_status.set(f"Showing all entries from {self.document.name}.")

    def _render_results(self) -> None:
        self.matches_value.set(f"{len(self.current_results)} matches")
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "\n\n".join(self.current_results))
        self.results_text.configure(state=tk.DISABLED)

    def _copy_results(self) -> None:
        if not self.current_results:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append("\n\n".join(self.current_results))
        self.analysis_status.set("Filtered results copied to the clipboard.")

    def _export_results(self) -> None:
        if not self.current_results:
            messagebox.showinfo("Nothing to export", "There are no results to export.")
            return

        path = filedialog.asksaveasfilename(
            title="Export filtered log entries",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            Path(path).write_text(
                "\n\n".join(self.current_results),
                encoding="utf-8",
            )
        except OSError as exc:
            messagebox.showerror("Unable to export results", str(exc))
            return

        self.analysis_status.set(f"Exported results to {path}.")

    def _select_cleanup_folder(self) -> None:
        selected = filedialog.askdirectory(title="Select log cleanup folder")
        if not selected:
            return
        self.cleanup_path.set(selected)
        self.cleanup_report = None
        self.delete_enabled.set(False)
        self._toggle_delete_button()
        self._clear_cleanup_tree()
        self.cleanup_status.set("Folder selected. Run Preview cleanup before deleting.")

    def _preview_cleanup(self) -> None:
        target = self.cleanup_path.get()
        if target == "No folder selected":
            messagebox.showinfo("No folder selected", "Choose a folder to scan first.")
            return

        try:
            self.cleanup_report = cleanup_logs(target, delete=False)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Cleanup preview failed", str(exc))
            return

        self._show_cleanup_report(self.cleanup_report)
        count = len(self.cleanup_report.candidates)
        self.cleanup_status.set(
            f"Dry-run complete: {count} .log file(s) would be affected. Nothing deleted."
        )

    def _delete_logs(self) -> None:
        if not self.delete_enabled.get():
            return
        if self.cleanup_report is None:
            messagebox.showinfo("Preview required", "Run Preview cleanup before deleting.")
            return

        preview = self.cleanup_report
        count = len(preview.candidates)
        if count == 0:
            messagebox.showinfo("Nothing to delete", "The preview found no .log files.")
            return

        confirmed = messagebox.askyesno(
            "Confirm log deletion",
            (
                f"Permanently delete the {count} previewed .log file(s) under:\n"
                f"{preview.target_dir}\n\nThis cannot be undone."
            ),
            icon="warning",
        )
        if not confirmed:
            return

        report = delete_log_files(
            preview.target_dir,
            [candidate.path for candidate in preview.candidates],
        )
        self.cleanup_report = report
        self.delete_enabled.set(False)
        self._toggle_delete_button()
        self._clear_cleanup_tree()

        if report.errors:
            messagebox.showwarning(
                "Cleanup finished with errors",
                "\n".join(report.errors),
            )
        self.cleanup_status.set(
            f"Deleted {len(report.deleted)} file(s); {len(report.errors)} error(s)."
        )

    def _show_cleanup_report(self, report: CleanupReport) -> None:
        self._clear_cleanup_tree()
        for candidate in report.candidates:
            self.cleanup_tree.insert(
                "",
                tk.END,
                values=(str(candidate.path), human_size(candidate.size_bytes)),
            )

    def _clear_cleanup_tree(self) -> None:
        for item in self.cleanup_tree.get_children():
            self.cleanup_tree.delete(item)

    def _toggle_delete_button(self) -> None:
        state = tk.NORMAL if self.delete_enabled.get() else tk.DISABLED
        self.delete_button.configure(state=state)


def human_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size_bytes} B"


def launch() -> None:
    root = tk.Tk()
    LogCleanerApp(root)
    root.mainloop()
