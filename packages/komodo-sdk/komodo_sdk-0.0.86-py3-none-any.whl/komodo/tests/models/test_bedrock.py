import json

import boto3
import pytest

from komodo.models.bedrock.bedrock_model import call_model

TEST_PROMPT = """
### Identity
Act as a writer for a medium blog post with a funny side.

### Objective
Write a medium blog post on how to use Amazon Bedrock 
to write an article on how to use Bedrock.

### Response Format
Respond in HTML format
"""


def test_bedrock_list_models():
    client = boto3.client('bedrock')
    response = client.list_foundation_models()
    models = response['modelSummaries']
    for model in models:
        print(json.dumps(model, indent=2))
        print()

    # byProvider = 'string',
    # byCustomizationType = 'FINE_TUNING' | 'CONTINUED_PRE_TRAINING',
    # byOutputModality = 'TEXT' | 'IMAGE' | 'EMBEDDING',
    # byInferenceType = 'ON_DEMAND' | 'PROVISIONED'
    print(response)


def test_bedrock_list_text_models():
    client = boto3.client('bedrock')
    response = client.list_foundation_models(byOutputModality='TEXT')
    models = response['modelSummaries']
    print(models[0].keys())
    for model in models:
        print(json.dumps(model, indent=2))
        print()


@pytest.mark.skip(reason="This test takes a long time to run")
def test_mail_assistant_cohere():
    response = call_model(TEST_PROMPT, 'cohere.command-text-v14')
    print(response.text)


@pytest.mark.skip(reason="This test takes a long time to run")
def test_mail_assistant_claude():
    response = call_model(TEST_PROMPT, 'anthropic.claude-v2:1')
    print(response.text)


@pytest.mark.skip(reason="This test takes a long time to run")
def test_mail_assistant_titan_take2():
    response = call_model(TEST_PROMPT, 'amazon.titan-text-express-v1')
    print(response.text)


@pytest.mark.skip(reason="This test takes a long time to run")
def test_mail_assistant_titan_take3():
    response = call_model(TEST_PROMPT, 'amazon.titan-tg1-large')
    print(response.text)
