import tkinter as tk
from tkinter import scrolledtext
from Log import Log
from FileManager import FileManager


def main():
    root = tk.Tk()
    root.title("Log Cleaner")
    root.configure(padx=10, pady=10)

    log = Log(FileManager.select_file())

    root.focus_force()

    label_contains = tk.Label(
        root, text=f"File '{log.name}' contains '{len(log.lines)}' lines."
    )
    label_contains.grid(row=0, column=1)

    tk.Label(root, text="Expression to search: ").grid(row=2)
    field_expression = tk.Entry(root)
    field_expression.grid(row=2, column=1)
    count_matches = tk.Label(root, text="Finded: 0")
    count_matches.grid(row=3)
    text_widget = scrolledtext.ScrolledText(root, width=100, height=50)
    text_widget.grid(row=4, column=0, columnspan=2)

    tk.Button(
        root,
        text="Search",
        command=lambda: search_and_show(
            log, field_expression, text_widget, count_matches
        ),
    ).grid(row=2, column=2, sticky=tk.W, pady=4)

    tk.Button(
        root,
        text="Copy to Clipboard",
        command=lambda: root.clipboard_append(text_widget.get("1.0", tk.END)),
    ).grid(row=4, column=2, pady=4)

    root.mainloop()


def search_and_show(log, expression, text_widget, label):
    matches = log.search_by_expression(expression.get())

    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, "\n".join(matches))

    label.config(text=f"Finded: {len(matches)}")


if __name__ == "__main__":
    main()
