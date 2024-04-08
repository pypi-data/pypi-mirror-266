from pathlib import Path


class Globber:

    def __init__(self, path, on_created=None, on_deleted=None):
        self.path = Path(path)
        self.monitored_files = set()
        self.on_created = on_created
        self.on_deleted = on_deleted

    def get_files_recursively_pathlib(self, pattern='*'):
        return [str(file) for file in self.path.rglob(pattern) if file.is_file()]

    def start(self):
        files = self.get_files_recursively_pathlib()
        self.monitored_files = set(files)
        if self.on_created:
            for file in files:
                self.on_created(file)

    def updates(self):
        files = self.get_files_recursively_pathlib()
        new_files = set(files)
        deleted_files = self.monitored_files - new_files
        created_files = new_files - self.monitored_files
        if self.on_created:
            for file in created_files:
                self.on_created(file)
        if self.on_deleted:
            for file in deleted_files:
                self.on_deleted(file)
        self.monitored_files = new_files


if __name__ == "__main__":
    import time
    import os

    globber = Globber(os.path.dirname(__file__), lambda x: print(f"Created: {x}"), lambda x: print(f"Deleted: {x}"))
    globber.start()
    while True:
        print("Checking for updates...")
        globber.updates()
        time.sleep(5)
