from pathlib import Path


class FileWriterHelper():

    def __init__(self, path, filename, mode):
        self.path = Path(path)
        self.filename = filename
        self.mode = mode

    def write_to_file(self, data, exists_behavior="overwrite"):
        file_path = self.path / f"{self.filename}"
        if exists_behavior == "skip" and file_path.exists():
            print(f"File {file_path} already exists. Skipping.")
            return file_path

        if exists_behavior == "rename":
            i = 1
            while file_path.exists():
                file_path = self.path / f"{self.filename}.{i}"
                i += 1

        with open(file_path, self.mode) as file:
            file.write(data)

        return file_path
