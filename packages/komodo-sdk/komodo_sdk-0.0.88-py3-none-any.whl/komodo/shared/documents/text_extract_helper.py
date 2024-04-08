import os
import shutil
from pathlib import Path

from komodo.shared.documents.text_extract import extract_text_from_path
from komodo.shared.utils.digest import get_file_digest_short


class TextExtractHelper:

    def __init__(self, path, cache_path=None, recache=False):
        self.path = Path(path)
        self.cache_path = Path(cache_path) if cache_path else None
        self.recache = recache
        self.text = None
        if cache_path:
            digest = get_file_digest_short(path)
            self.cache_folder = Path(cache_path) / digest
            os.makedirs(self.cache_folder, exist_ok=True)

    def extract_text(self):
        if self.cache_path:
            if not self.recache:
                if cached_text := self.get_cached_extracted_text():
                    print("Using cached text for: " + str(self.path))
                    return cached_text

            text = self.extract_and_cache()
            return text
        else:
            return extract_text_from_path(self.path)

    def original_path(self):
        return self.cache_folder / os.path.basename(self.path)

    def extracted_path(self):
        return self.cache_folder / "extracted.txt"

    def extract_and_cache(self):
        shutil.copy(self.path, self.original_path())
        text = extract_text_from_path(self.path)
        if text:
            with open(self.extracted_path(), "w") as f:
                f.write(text)
        return text

    def get_cached_extracted_text(self):
        try:
            if os.path.exists(self.cache_folder):
                with open(self.extracted_path()) as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading cached text from {self.cache_folder}: {e}")
        return None


if __name__ == "__main__":
    # Example usage:
    # helper = TextExtractHelper(path="/path/to/your/file", cache_path="/path/to/your/cache")
    # text = helper.extract_text()
    # print(text)
    helper = TextExtractHelper(path="/Users/komodo/dev/komodo-sdk/pdf2html/data/sample.pdf")
    text = helper.extract_text()
    print(text)

    helper = TextExtractHelper(path="/Users/komodo/dev/komodo-sdk/pdf2html/data/sample.html")
    text = helper.extract_text()
    print(text)
