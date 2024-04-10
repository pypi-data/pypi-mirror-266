import os

from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.documents.text_extract import extract_text_from_path


class SampleTool(KomodoTool):
    name = "File Reader"
    purpose = "Reads data files and returns contents as base64 encoded string. You must decode the results."
    shortcode = "sample_tool"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of file to read"
                    },
                    "start": {
                        "type": "integer",
                        "description": "Start position in file"
                    },
                    "bytes": {
                        "type": "integer",
                        "description": "Number of bytes to read. Defaults to 2048."
                    }
                },
                "required": ["filename", "function_call"]
            }
        }
    }

    def __init__(self, path):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)
        self.path = path

    def action(self, args):
        try:
            path = os.path.join(self.path, args["filename"])
            start = args.get("start", 0)
            bytes = args.get("bytes", 2048)
            contents = extract_text_from_path(path)
            return contents[start:start + bytes]
        except Exception:
            return "Failed to read file: " + args["filename"]


def hello_world(contents: str):
    return "Hello World! Length: " + str(len(contents))


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    tool = SampleTool(PlatformConfig().komodo_hello_path)
    print(tool.definition)
    print(tool.action({"filename": "hello.txt", "function_call": "hello_world"}))
