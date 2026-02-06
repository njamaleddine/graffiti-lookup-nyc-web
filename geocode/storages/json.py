import json
import os


class JsonFile:
    def __init__(self, file_name: str, default_data=None):
        self.file_name = file_name
        self.default_data = default_data if default_data is not None else {}

    def load(self):
        if os.path.exists(self.file_name):
            with open(self.file_name) as file:
                return json.load(file)
        return self.default_data

    def save(self, data):
        with open(self.file_name, "w") as file:
            json.dump(data, file, indent=2)
