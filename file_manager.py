# file_manager.py 
# handles saving and loading simulation results as a fixed-width text file.

import os
from simulation_result import SimulationResult


class FileManager:

    def __init__(self, filename):
        self._filename = filename   # Path of the history txt file

    def get_filename(self):
        return self._filename

    def save_result(self, result):
        # Append one result as a new row.
        # If the file does not exist yet, write the header row first.
        try:
            file_is_new = not os.path.exists(self._filename)
            with open(self._filename, "a", encoding="utf-8") as f:
                if file_is_new:
                    f.write(SimulationResult.text_header() + "\n")
                f.write(result.to_text_row() + "\n")
        except Exception as e:
            raise IOError(f"Could not save the result: {e}")

    def load_results(self, filename=None):
        # Read all results from a file.
        # If no filename is given, the default history file is used.
        # Returns an empty list if the file does not exist yet.
        path = filename if filename else self._filename
        results = []
        if not os.path.exists(path):
            return results
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            raise IOError(f"Could not read the file: {e}")

        # The first line is the header, so the program skips it.
        for line in lines[1:]:
            if line.strip() == "":
                continue
            result = SimulationResult.from_text_row(line)
            # from_text_row returns None for broken rows; skip them.
            if result is not None:
                results.append(result)
        return results

    def clear(self):
        # Delete the history file if it exists.
        try:
            if os.path.exists(self._filename):
                os.remove(self._filename)
        except Exception as e:
            raise IOError(f"Could not clear the history file: {e}")
