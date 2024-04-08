import json

from komodo.models.bedrock.bedrock import invoke_text_model
from komodo.models.framework.model_response import ModelResponse
from komodo.shared.utils.sentry_utils import sentry_trace


#
# cohere.command-text-v14
# cohere.command-light-text-v14
@sentry_trace
def bedrock_cohere_invoke(prompt, model='cohere.command-text-v14') -> ModelResponse:
    body = json.dumps({
        "prompt": prompt,
        "max_tokens": 3000,
        "temperature": 0.75,
        "p": 0.01,
        "k": 0,
    })

    response = invoke_text_model(body, model=model)
    output = json.loads(response.get('body').read())
    text = output['generations'][0]['text']
    return ModelResponse(model=model, status="completed", output=output, text=text)
