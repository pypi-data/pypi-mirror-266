import json

from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from pydantic import ValidationError


class StreamingToolCallBuilder:
    def __init__(self):
        self.tool_call_accumulator = ""  # Accumulator for JSON fragments of tool call arguments
        self.tool_call_id = None  # Current tool call ID
        self.function_name = None
        self.tool_calls = []

    def process(self, delta_tool_calls):
        for tc in delta_tool_calls:
            if tc.id:  # New tool call detected here
                self.tool_call_id = tc.id
                self.tool_call_accumulator = ""

            if tc.function.name:
                self.function_name = tc.function.name

            self.tool_call_accumulator += tc.function.arguments if tc.function.arguments else ""
            try:
                json.loads(self.tool_call_accumulator)
                fn = Function(name=self.function_name, arguments=self.tool_call_accumulator)
                self.tool_calls.append(
                    ChatCompletionMessageToolCall(id=self.tool_call_id, function=fn, type='function'))
            except json.JSONDecodeError:
                pass
            except ValidationError as ve:
                print(ve)
                pass

    def get_tool_calls(self):
        return self.tool_calls
