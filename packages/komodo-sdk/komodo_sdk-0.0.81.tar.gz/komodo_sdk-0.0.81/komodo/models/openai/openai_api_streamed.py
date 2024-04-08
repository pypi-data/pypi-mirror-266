import traceback

import openai

from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.models import OPENAI_GPT4_MODEL
from komodo.models.openai.openai_api_streamed_tool_call import StreamingToolCallBuilder
from komodo.models.openai.openai_completion import openai_client
from komodo.models.openai.openai_debug import OpenAIProcessDebug, debug_print
from komodo.models.openai.openai_process_actions import OpenAIProcessActions
from komodo.shared.utils.digest import get_num_tokens


def openai_chat_response_streamed(request: ModelRequest):
    client = openai_client()
    model = request.runtime.agent.model

    if collection := request.runtime.selected_collection:
        summary = collection.get_collection_summary_for_user()
        yield debug_print(summary)

    try:
        for token in openai_invoke_streamed(client, request=request):
            yield token

    except openai.BadRequestError as e:
        if e.code == "context_length_exceeded" and model != OPENAI_GPT4_MODEL:
            request.runtime.model = OPENAI_GPT4_MODEL
            yield debug_print("The context length exceeded maximum allowed. Auto-retrying with GPT-4 model.")
            for token in openai_invoke_streamed(client, request=request):
                yield token
        else:
            raise e

    except Exception:
        print(traceback.format_exc())
        yield debug_print(
            "An error occurred while processing the request. "
            "Please try again later and contact support if the issue persists.")


def openai_invoke_streamed(client, *, request: ModelRequest):
    prompt = request.prompt
    params = request.build_openai_params(stream=True)
    debug = OpenAIProcessDebug(request.runtime)

    messages = params['messages'] if 'messages' in params else []
    messages.append({'role': 'user', "content": prompt})

    done = False
    depth = 0
    max_depth = 5
    while not done and depth < max_depth:
        total_input_tokens = sum([get_num_tokens(message['content']) for message in messages])
        debug.debug_input_tokens(total_input_tokens)

        for message in messages:
            tokens = get_num_tokens(message['content'])
            debug.debug_message_tokens(message, tokens)

        # no more tools
        if depth >= max_depth - 1:
            print("Max depth reached. Last response without tools. Upgrading to GPT-4.")
            params['tools'] = []
            params['model'] = OPENAI_GPT4_MODEL

        completion = client.chat.completions.create(**params)
        streamed_role = None
        streamed_output = ""
        tool_call_builder = StreamingToolCallBuilder()
        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta is not None:
                if delta.role is not None and delta.role != streamed_role:
                    streamed_role = delta.role
                if delta.content is not None:
                    streamed_output += delta.content
                    yield delta.content
                if delta.tool_calls is not None:
                    tool_call_builder.process(delta.tool_calls)

        if streamed_output:
            total_output_tokens = get_num_tokens(streamed_output)
            debug.debug_output_tokens(total_output_tokens)

        tool_calls = tool_call_builder.get_tool_calls()
        if tool_calls:
            actions_processor = OpenAIProcessActions(tool_calls, request.runtime)
            yield debug_print("Gathering data...")
            for call in tool_calls:
                yield debug.debug_invoke(call)

            outputs = actions_processor.process_actions_gpt_streaming()
            for output in outputs:
                messages.append(output)

                tokens = get_num_tokens(output['content'])
                debug.debug_tool_tokens(output['name'], tokens)
                yield debug.debug_response(output)

            params['messages'] = messages
            depth += 1
        else:
            done = True
