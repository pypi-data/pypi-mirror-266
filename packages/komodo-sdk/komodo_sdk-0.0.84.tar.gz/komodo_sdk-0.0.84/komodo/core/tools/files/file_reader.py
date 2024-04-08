import os
from pathlib import Path

from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.documents.text_extract_helper import TextExtractHelper
from komodo.shared.utils.digest import convert_to_base64


class FileReader(KomodoTool):
    name = "File Reader"
    purpose = "Reads contents of files. Can return extracted text or raw bytes. Use paging params to read large files."
    shortcode = "komodo_file_reader"

    def definition(self, shortcode):
        return {
            "type": "function",
            "function": {
                "name": shortcode,
                "description": self.purpose,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder": {
                            "type": "string",
                            "description": "Path of the folder to list files from."
                        },
                        "filename": {"type": "string", "description": "Name of the file to read"},
                        "page": {"type": "integer", "description": "Page number to read. Default: 1"},
                        "page_size": {"type": "integer", "description": "Size of page. Default: 2000, Max: 100000."},
                        "raw": {"type": "boolean",
                                "description": "If true, returns raw bytes base64 encoded. Default: false."}
                    },
                    "required": ["folder", "filename"]
                },
            }
        }

    def __init__(self):
        shortcode = self.shortcode
        super().__init__(shortcode=shortcode,
                         name=self.name,
                         definition=self.definition(shortcode),
                         action=self.action)

    def action(self, args, runtime: KomodoRuntime):
        folder = Path(args.get('folder'))
        filename = Path(args.get("filename")).name
        collection = runtime.selected_collection or runtime.home_folder
        path = None

        if folder.is_absolute():
            path = Path(folder) / filename
        elif folder.name == collection.path.name:
            path = collection.path / filename

        if not path or not path.exists():
            return f"Could not find folder or filename. folder: {str(folder)}, filename: {str(filename)}"

        try:
            page = args.get("page", 1)
            page_size = min(args.get("page_size", 2000), 100000)
            raw = args.get("raw", False)

            if not raw:
                return self.extract_page_text(path, page, page_size, runtime.config.cache())
            else:
                return self.read_raw_file_section(path, page, page_size)

        except Exception:
            return f"Failed to read file: {Path(filename).name} from {folder}"

    def extract_page_text(self, file_path, target_page, page_size, cache_path):
        # Initialize a helper for text extraction, using the provided path and cache.
        text_helper = TextExtractHelper(file_path, cache_path=cache_path)
        # Extract all text content from the file.
        full_text = text_helper.extract_text()

        # Calculate the total size of the text and the total number of pages.
        total_size = len(full_text)
        total_pages = (total_size // page_size) + 1 if total_size > 0 else 0

        # Handle negative page numbers by wrapping around to the end.
        if target_page < 0:
            target_page = 1 + (total_pages + target_page) % total_pages or 1

        # Calculate the starting byte position for the desired page.
        start_byte = (target_page - 1) * page_size
        # Ensure we do not exceed the total size when calculating the end byte.
        end_byte = start_byte + page_size if target_page < total_pages else total_size

        # Extract the specific page content by slicing the full text.
        page_text = full_text[start_byte:end_byte]

        # Determine the status based on whether we're dealing with a complete or partial file
        status = "complete" if start_byte == 0 and (end_byte - start_byte) >= total_size else "partial file"

        return {
            'contents': page_text,
            'format': 'text',
            'status': status,
            'page': target_page,
            'page_size': page_size,
            'num_pages': total_pages,
            'raw': False,
            'total_size': total_size,
            'notes': 'The contents are extracted text. For original bytes in file, pass raw = True',
        }

    def read_raw_file_section(self, file_path, target_page, page_size):
        # Calculate the total size of the file.
        total_bytes = os.path.getsize(file_path)
        # Determine the total number of pages.
        total_pages = (total_bytes // page_size) + 1 if total_bytes > 0 else 0

        # Adjust for negative page numbers by wrapping around.
        if target_page < 0:
            target_page = 1 + (total_pages + target_page) % total_pages or 1

        # Calculate the starting byte for the target page.
        start_byte = max((target_page - 1) * page_size, 0)
        # Calculate the number of bytes to read, not exceeding the file size.
        bytes_to_read = min(page_size, total_bytes - start_byte)

        # Open the file and seek to the start position of the target page.
        with open(file_path, "rb") as file:
            file.seek(start_byte)
            # Read the specified number of bytes.
            content_bytes = file.read(bytes_to_read)

        # Convert the read bytes to base64 format.
        base64_content = convert_to_base64(content_bytes)

        # Determine if the read operation covers the entire file or just a portion.
        status = "complete" if start_byte == 0 and bytes_to_read >= total_bytes else "partial file"

        # Package the result with relevant metadata.
        result = {
            'contents': base64_content,
            'format': 'base64',
            'page': target_page,
            'page_size': page_size,
            'num_pages': total_pages,
            'raw': True,
            'status': status,
            'total_bytes': total_bytes,
            'notes': 'The contents are base64 encoded. Use a base64 decoder to view the contents, '
                     'or pass raw = False to retrieve extracted text',
        }

        return result


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    config = PlatformConfig()
    runtime = KomodoRuntime(config=config)
    params = {}

    tool = FileReader()
    print(tool.definition)
    print(tool.action({'folder': config.komodo_hello_path, "filename": "hello.txt"}, runtime))

    print(tool.definition)
    print(tool.action({'folder': config.komodo_inflation_path, "filename": "InflationChapter1.pdf",
                       "raw": False, "page": -1, "page_size": 100}, runtime))
