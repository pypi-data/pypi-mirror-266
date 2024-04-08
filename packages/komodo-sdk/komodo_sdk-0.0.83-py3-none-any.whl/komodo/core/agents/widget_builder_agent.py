from enum import Enum

from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext
from komodo.shared.utils.digest import get_guid_short


class WidgetType(Enum):
    TEXT = "text"
    SUMMARY = "summary"
    TABLE = "table"
    CHART = "chart"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class WidgetBuilderAgent(KomodoAgent):
    shortcode = "widget_builder"
    name = "Widget Builder"
    instructions = "This agent is a widget generator which is used to generate widgets."

    def __init__(self, *, widget_type, **kwargs):
        super().__init__(shortcode=self.shortcode, name=self.name, instructions=self.instructions, **kwargs)
        self.purpose: str = kwargs.get("purpose", "This agent builds intelligent widgets.")
        self.guid: str = kwargs.get("guid", get_guid_short())
        self.widget_type: WidgetType = widget_type if isinstance(widget_type, WidgetType) else WidgetType(widget_type)
        self.audience: str = kwargs.get("audience", "general")
        self.prompt: str = kwargs.get("prompt", "Prompt used to build a widget.")
        self.overlays: [str] = kwargs.get("overlays", [])
        self.contents: str = kwargs.get("contents", "Not generated yet")

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.extend(super().generate_context(prompt))
        context.add_dict({
            "context": "This agent is a widget generator which is used to generate widgets.",
            "guid": self.guid,
            "purpose": self.purpose,
            "output": "json only",
            "widgetType": isinstance(self.widget_type, WidgetType) and self.widget_type.value or str(self.widget_type),
            "audience": self.audience,
            "note1": "Generate data that matches output type and audience.",
            "note2": "Output json must contain audience and widget_type fields.",
            "note3": "Output json must contain contents field which can be used to populate the widget by react component.",
            "note4": "Output json must contain instructions field on how to use the contents to draw the react component.",
            "note5": "For charts, provide instructions for what chart to draw, what data to display, and how to display it."
        })

        for overlay in self.overlays:
            context.add("Overlays to apply to generated result", overlay)

        return context
