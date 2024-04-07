import json
import typing

import boto3


def invoke_lambda_function_sync(*, functionName: str = None, payload: typing.Mapping[str, str] = None):
    response = invoke_lambda_function(functionName=functionName, payload=payload, invocationType="RequestResponse")
    result = response["Payload"].read()
    return json.loads(result.decode('utf-8'))


def invoke_lambda_function_async(*, functionName: str = None, payload: typing.Mapping[str, str] = None):
    return invoke_lambda_function(functionName=functionName, payload=payload, invocationType="Event")


def lambda_fetch_secret(key):
    data = invoke_lambda_function_sync(functionName='komodo_secrets', payload={"key": key})
    if 'errorType' in data:
        print("Error: " + str(data))
        return None
    return data['body'][key]


def invoke_lambda_function(*, functionName: str = None, payload: typing.Mapping[str, str] = None,
                           invocationType: str = "RequestResponse"):
    if functionName is None:
        raise Exception('ERROR: functionName parameter cannot be NULL')
    payloadStr = json.dumps(payload)
    payloadBytesArr = bytes(payloadStr, encoding='utf8')
    client = boto3.client('lambda')
    return client.invoke(
        FunctionName=functionName,
        InvocationType=invocationType,  # can be "RequestResponse" or "Event"
        Payload=payloadBytesArr
    )


if __name__ == '__main__':
    payloadObj = {"something": "1111111-222222-333333-bba8-1111111"}
    response = invoke_lambda_function(functionName='openai_get_api_key', payload=payloadObj)
    print(f'response:{response}')
    print(f'response["Payload"]:{response["Payload"]}')

    result = response["Payload"].read()
    data = json.loads(result.decode('utf-8'))
    key = data['body']['api_key']
    print(f'key:{key}')
