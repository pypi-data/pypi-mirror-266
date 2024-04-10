from komodo.framework.komodo_tool import KomodoTool


class KomodoToolRegistry:
    REGISTRY = {}

    @classmethod
    def add_komodo_tool(cls, tool: KomodoTool):
        cls.REGISTRY[tool.shortcode] = tool

    @classmethod
    def register(cls, tool: KomodoTool):
        cls.add_komodo_tool(tool)

    @classmethod
    def get_tool_by_shortcode(cls, shortcode: str) -> KomodoTool:
        return cls.REGISTRY.get(shortcode)

    @classmethod
    def find_tool_by_shortcode(cls, shortcode: str, tools) -> KomodoTool:
        for t in tools or []:
            if isinstance(t, str) and t == shortcode:
                return cls.get_tool_by_shortcode(t)
            elif isinstance(t, KomodoTool) and t.shortcode == shortcode:
                return t
        return None

    @classmethod
    def get_tools(cls, tools) -> [KomodoTool]:
        result = []
        missing = []
        for t in tools or []:
            if isinstance(t, str):
                result.append(cls.get_tool_by_shortcode(t))
            elif isinstance(t, KomodoTool):
                result.append(t)
            else:
                missing.append(t)
        for sc in missing:
            print(f"Requested tool {sc} not found in registry")
        return result

    @classmethod
    def get_definitions(cls, tools):
        definitions = []
        for t in tools or []:
            if isinstance(t, str):
                definitions.append(KomodoToolRegistry.get_tool_by_shortcode(t).definition)
            elif isinstance(t, dict) and 'definition' in t:
                definitions.append(t['definition'])
            elif isinstance(t, KomodoTool):
                definitions.append(t.definition)
            else:
                raise ValueError(f"Invalid tool: {t}")
        return definitions
