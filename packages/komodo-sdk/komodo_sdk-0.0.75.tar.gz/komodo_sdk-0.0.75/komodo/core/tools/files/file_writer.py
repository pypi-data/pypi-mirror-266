from pathlib import Path

from komodo.config import PlatformConfig
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.framework.komodo_user import KomodoUser
from komodo.shared.documents.text_convert_helper import TextConvertHelper


class FileWriter(KomodoTool):
    name = "File Writer"
    purpose = "Write content in supported formats."
    shortcode = "file_writer"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "contents": {
                        "type": "string",
                        "description": "Contents to write."
                    },
                    "filename": {
                        "type": "string",
                        "description": "Name of the target file without path or extension."
                    },
                    "input_format": {
                        "type": "string",
                        "description": "Format of input text. "
                                       "Supported formats: text, markdown, html"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Format of output file."
                                       "Supported values: text, markdown, html, pdf"
                    },
                    "existing_behavior": {
                        "type": "string",
                        "description": "Action to take if the file already exists. "
                                       "Supported values: overwrite, skip, rename. "
                                       "Default: overwrite"
                    }
                },
                "required": ["text", "filename", "input_format", "output_format"]
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    def action(self, args, runtime: KomodoRuntime):
        contents = args.get("contents")
        filename = Path(args.get("filename")).stem
        input_format = args.get("input_format")
        output_format = args.get("output_format")
        existing_behavior = args.get("existing_behavior", "overwrite")

        helper = TextConvertHelper(contents=contents, input_format=input_format)
        contents, extension, mode = helper.convert_to(output_format)

        collection = runtime.downloads_folder
        path = collection.add_file(str(filename) + extension, contents, mode, existing_behavior=existing_behavior)
        return f"File {filename} written successfully. Path: " + str(path)


if __name__ == "__main__":
    tool = FileWriter()
    runtime = KomodoRuntime(config=PlatformConfig(), user=KomodoUser.default())

    print(tool)
    print(tool.action(
        {"contents": "Hello, world!", "filename": "hello", "input_format": "text", "output_format": "pdf"},
        runtime))
