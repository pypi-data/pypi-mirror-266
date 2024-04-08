import json

from komodo.config import PlatformConfig
from komodo.core.tools.files.directory_reader import DirectoryReader
from komodo.core.tools.files.file_reader import FileReader
from komodo.core.tools.files.file_writer import FileWriter
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_user import KomodoUser
from komodo.models.framework.agent_runner import AgentRunner


class PdfGeneratorAgent(KomodoAgent):
    shortcode = "pdf_generator"
    name = "PDF Generartor"
    purpose = "Generate PDF documents including tables."
    instructions = "You are a PDF Generator Agent. " \
                   "You will be given a folder with data files. " \
                   "You must generate a PDF document with the data. " \
                   "You must use the provided tools to generate the PDF. " \
                   "Do not use any external sources."

    def __init__(self, directory_path):
        super().__init__(
            shortcode=self.shortcode,
            name=self.name,
            purpose=self.purpose,
            instructions=self.instructions)

        self.directory_path = directory_path

        self.add_tool(FileReader())
        self.add_tool(FileWriter())

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.extend(super().generate_context(prompt))

        files = DirectoryReader().action({'folder': self.directory_path})
        context.add("Files Available", json.dumps(files))
        return context


if __name__ == "__main__":
    config = PlatformConfig()
    agent = PdfGeneratorAgent(config.shared())
    runtime = KomodoRuntime(agent=agent, config=config, user=KomodoUser.default())
    runner = AgentRunner(runtime)
    runner.run(
        "Generate a PDF document with the data located in drpraegars_sow.txt file. Read in raw format, decode into text, apply rich markdown formatting and then use the markdown to generate the PDF.")
