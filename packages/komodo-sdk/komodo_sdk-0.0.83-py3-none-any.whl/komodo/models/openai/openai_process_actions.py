import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from time import time

from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function

from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool_registry import KomodoToolRegistry
from komodo.models.framework.chat_metadata import ChatMetaData
from komodo.shared.documents.text_extract import to_clean_text
from komodo.shared.utils.term_colors import print_info, print_error, print_header, print_gray, print_warning
from komodo.shared.utils.timebox import time_print_simple, time_print

TOOLS_TIMEOUT = 60


class OpenAIProcessActions():

    def __init__(self, tool_calls, runtime: KomodoRuntime):
        self.runtime = runtime
        self.tools = runtime.agent.tools if runtime.agent else []
        self.metadata = ChatMetaData(runtime.user, runtime.agent)
        self.tool_calls = self.process_for_parallel_callback(tool_calls)
        self.timeout = TOOLS_TIMEOUT

    def process_actions_gpt_legacy_api(self) -> list:
        outputs = self.get_tools_outputs()
        for output in outputs:
            output['role'] = "tool"
            output['content'] = output['output']
            del output['output']

        print_gray("Outputs: ", json.dumps(outputs, default=vars))
        return outputs

    def process_actions_gpt_streaming(self) -> list:
        outputs = self.get_tools_outputs()
        for output in outputs:
            output['role'] = "function"
            output['content'] = output['output']
            del output['output']

        print_gray("Outputs: ", json.dumps(outputs, default=vars))
        return outputs

    def get_tools_outputs(self):
        parallel = len(self.tool_calls) > 1
        start = time()
        try:
            if parallel:
                return self.get_tools_outputs_parallel()
            else:
                return self.get_tools_outputs_sequential()
        except TimeoutError:
            if parallel:
                print_gray(f'timeout: {self.timeout} waiting time: {time() - start}')
                print_warning("Timed out parallel, trying sequential execution...")
                return self.get_tools_outputs_sequential()

    @time_print_simple
    def get_tools_outputs_sequential(self):
        outputs = []
        for call in self.tool_calls:
            output = self.process_tool_call(call)
            outputs.append(output)
        return outputs

    @time_print_simple
    def get_tools_outputs_parallel(self):
        outputs = list()
        with ThreadPoolExecutor() as executor:
            for output in executor.map(self.process_tool_call, self.tool_calls, timeout=self.timeout):
                outputs.append(output)
        return outputs

    def process_tool_call(self, call):
        message = f"Processing tool call: {call.id} Type: {call.type} Function: {call.function.name} Arguments: {call.function.arguments}"
        print_info(message)
        shortcode = call.function.name
        arguments = call.function.arguments
        tool = KomodoToolRegistry.find_tool_by_shortcode(shortcode, self.tools)
        output = self.generate_tool_output(tool, arguments)
        return {"tool_call_id": call.id, "name": shortcode, "output": output}

    @time_print
    def generate_tool_output(self, tool, arguments):
        if tool:
            print_header("Invoking tool object: " + tool.name)
            if self.runtime.tools_invocation_callback:
                self.runtime.tools_invocation_callback(tool, arguments)

            try:
                args = json.loads(arguments)
                output = str(tool.run(args, self.runtime))
                output = to_clean_text(output)
            except Exception as e:
                print_error(f"Error invoking tool {tool.shortcode}: {e}")
                print_error(traceback.format_exc())
                output = f"Error invoking tool {tool.shortcode}"
        else:
            print_error(f"Requested tool {tool.shortcode} is not available")
            output = f"Requested tool {tool.shortcode} is not available"

        max_output_len = self.metadata.max_function_output_len()
        if len(output) > max_output_len:
            output = output[:max_output_len] + " ... (truncated)"

        if self.runtime.tools_response_callback:
            self.runtime.tools_response_callback(tool, arguments, output)

        return output

    def process_for_parallel_callback(self, tool_calls):
        result = []
        for call in tool_calls:
            if call.function.name == "parallel" or call.function.name == "multi_tool_use.parallel":
                print("Processing parallel tool call from OpenAI")
                arguments = json.loads(call.function.arguments)
                for tool_use in arguments["tool_uses"]:
                    function = tool_use["recipient_name"].split(".")[1]
                    arguments = json.dumps(tool_use["parameters"])
                    call = ChatCompletionMessageToolCall(
                        id="parallel",
                        type="function",
                        function=Function(
                            name=function,
                            arguments=arguments))

                    result.append(call)
            else:
                result.append(call)
        return result


if __name__ == "__main__":
    tool_calls = [
        ChatCompletionMessageToolCall(
            id="call_2EuEj837GZm8VnZdMYScl3Ml",
            type="function",
            function=Function(
                name="multi_tool_use.parallel",
                arguments=json.dumps({
                    "tool_uses": [
                        {
                            "recipient_name": "functions.komodo_file_reader",
                            "parameters": {
                                "folder": "blah"
                            }
                        },

                    ]})))]

    runtime = KomodoRuntime()
    openai_process_actions = OpenAIProcessActions(tool_calls, runtime)
    print(openai_process_actions.process_actions_gpt_legacy_api())
