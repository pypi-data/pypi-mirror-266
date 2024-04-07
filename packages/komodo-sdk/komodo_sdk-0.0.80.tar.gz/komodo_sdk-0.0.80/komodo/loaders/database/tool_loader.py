from komodo.framework.komodo_tool import KomodoTool
from komodo.framework.komodo_tool_registry import KomodoToolRegistry
from komodo.store.tool_store import ToolStore


class ToolLoader:

    @classmethod
    def load(cls, shortcode) -> KomodoTool:
        tool = ToolStore().retrieve_tool(shortcode)
        print(tool)
        t = KomodoToolRegistry.get_tool_by_shortcode(shortcode)
        t.name = tool.name
        t.purpose = tool.purpose
        return t
