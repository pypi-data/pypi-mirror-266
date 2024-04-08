import json

from komodo.models.bedrock.bedrock import invoke_text_model
from komodo.models.framework.model_response import ModelResponse
from komodo.shared.utils.sentry_utils import sentry_trace


#
# cohere.command-text-v14
# cohere.command-light-text-v14
@sentry_trace
def bedrock_claude_invoke(prompt, model='anthropic.claude-v2:1') -> ModelResponse:
    body = json.dumps(
        {
            "prompt": "\n\nHuman:\n" + prompt + "\n\nAssistant:\n",
            "max_tokens_to_sample": 3000,
            "anthropic_version": "bedrock-2023-05-31"
        }
    )

    response = invoke_text_model(body, model=model)
    output = json.loads(response.get('body').read())
    text = output.get("completion")
    return ModelResponse(model=model, status="completed", output=output, text=text)
