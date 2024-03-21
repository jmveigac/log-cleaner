import os
import re


class Log:
    def __init__(self, path_file):
        self.name = os.path.basename(path_file)
        self.path_file = path_file
        self.lines = []
        self.error = []
        self.info = []
        self.__count_unique_entries()

    def __count_unique_entries(self):
        try:
            with open(self.path_file, "r") as log_file:
                lines = log_file.readlines()

            current_entry = ""
            for line in lines:
                if re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", line):
                    if current_entry:
                        self.lines.append(current_entry.strip())
                    current_entry = line
                else:
                    current_entry += line

            if current_entry:
                self.lines.append(current_entry.strip())

        except FileNotFoundError:
            print(f"Error: Log file '{self.path_file}' not found.")
            return 0

    def search_by_expression(self, expression):
        records = [line for line in self.lines if re.search(expression, line)]
        return records
