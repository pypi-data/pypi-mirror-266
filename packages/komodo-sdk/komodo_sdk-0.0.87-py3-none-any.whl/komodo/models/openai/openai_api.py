from komodo.models.framework.chat_message import ChatMessage
from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.model_response import ModelResponse
from komodo.models.openai.openai_completion import openai_client
from komodo.models.openai.openai_process_actions import OpenAIProcessActions


def openai_chat_response(request: ModelRequest) -> ModelResponse:
    return openai_invoke(openai_client(), request=request)


def openai_invoke(client, *, request: ModelRequest) -> ModelResponse:
    prompt = request.prompt
    params = request.build_openai_params(stream=False)

    messages = params['messages'] if 'messages' in params else []
    messages.append(ChatMessage(prompt, role='user'))

    done = False
    depth = 0
    while not done and depth < 5:
        completion = client.chat.completions.create(**params)
        response_message = completion.choices[0].message

        tool_calls = response_message.tool_calls
        if tool_calls:
            actions_processor = OpenAIProcessActions(tool_calls, request.runtime)
            outputs = actions_processor.process_actions_gpt_legacy_api()
            messages.append(response_message)
            for output in outputs:
                messages.append(output)

            depth += 1
        else:
            text = completion.choices[0].message.content
            status = completion.choices[0].finish_reason
            return ModelResponse(model=params['model'], status=status, output=completion, text=text)

    return ModelResponse(model=params['model'], status="error", output=None,
                         text="Error: max depth of tool calls reached")
