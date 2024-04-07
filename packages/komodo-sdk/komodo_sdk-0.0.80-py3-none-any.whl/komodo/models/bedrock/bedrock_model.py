from komodo.models.bedrock.bedrock_claude import bedrock_claude_invoke
from komodo.models.bedrock.bedrock_cohere import bedrock_cohere_invoke
from komodo.models.bedrock.bedrock_titan import bedrock_titan_invoke
from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.model_response import ModelResponse
from komodo.shared.utils.sentry_utils import sentry_trace


@sentry_trace
def bedrock_assistant_response(request: ModelRequest) -> ModelResponse:
    prompt = request.prepare_detailed_prompt()
    return call_model(prompt, request.agent.model)


def call_model(prompt, model) -> ModelResponse:
    try:
        print("Invoking model: " + model)
        if "titan" in model:
            return bedrock_titan_invoke(prompt, model)
        elif "claude" in model:
            return bedrock_claude_invoke(prompt, model)
        elif "cohere" in model:
            return bedrock_cohere_invoke(prompt, model)
        else:
            print("Error invoking model: " + model + " Defaulting to cohere.")
            return bedrock_cohere_invoke(prompt)

    except Exception as e:
        print("Error during invoke: " + str(e))
        output = "Sorry, I am having trouble processing your request. Please try again."
        return ModelResponse(model=model, status="failed", output=output, text=output)
