import json

from komodo.models.bedrock.bedrock import invoke_text_model
from komodo.models.framework.model_response import ModelResponse
from komodo.shared.utils.sentry_utils import sentry_trace


# https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-text.html
@sentry_trace
def bedrock_titan_invoke(prompt, model='amazon.titan-tg1-large') -> ModelResponse:
    body = json.dumps({
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 3000
        }
    })

    response = invoke_text_model(body, model=model)
    model_output = json.loads(response.get('body').read())
    text = model_output['results'][0]['outputText']
    return ModelResponse(model=model, status="completed", output=model_output, text=text)
