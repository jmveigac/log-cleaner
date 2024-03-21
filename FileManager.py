import tkinter as tk
from tkinter import filedialog


class FileManager:
    def __init__(self):
        pass

    @staticmethod
    def select_file():
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All files", "*.*"),
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
            ]
        )
        return file_path
