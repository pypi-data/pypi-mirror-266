from komodo.models.azure.azure_openai import azure_openai_invoke

TEST_PROMPT = """
### Identity
Act as a writer for a medium blog post with a funny side.

### Objective
Write a medium blog post on how to use Amazon Bedrock 
to write an article on how to use Bedrock.

### Response Format
Respond in HTML format
"""


def test_azure_completion():
    response = azure_openai_invoke(prompt=TEST_PROMPT)
    print(response.text)
