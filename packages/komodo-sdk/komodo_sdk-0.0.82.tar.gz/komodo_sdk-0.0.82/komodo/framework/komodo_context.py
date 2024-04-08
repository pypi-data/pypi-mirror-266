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

    def add_dict(self, values):
        for key, value in values.items():
            self.add(key, value)

    def reset(self):
        self.data = []
