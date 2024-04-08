from pathlib import Path


class KomodoContext:
    def __init__(self):
        self.data = []

    def __str__(self):
        return str(self.data)

    def add(self, tag, content):
        self.data.append((tag, content))
        return self

    def extend(self, context):
        self.data.extend(context.data)
        return self

    def add_dict(self, values):
        for key, value in values.items():
            self.add(key, value)
        return self

    def add_file(self, file):
        path = Path(file)
        self.add(path.name, path.read_text())
        return self

    def reset(self):
        self.data = []
