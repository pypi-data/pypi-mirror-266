import json

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn="https://7f56b597fdc625977aa4ef8246037219@o4506367192858624.ingest.sentry.io/4506367195283456",
    integrations=[
        AwsLambdaIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0
)


def shared_handler(event, context, router):
    print(context)
    fn_name = context.function_name
    with sentry_sdk.start_transaction(op="lambda_handler", name=fn_name):
        with sentry_sdk.start_span(op="lambda_handler", description=fn_name):
            # raise Exception(sentry_sdk.VERSION)
            # print(sentry_sdk.get_current_span())
            result = router(event, context, fn_name)
            if result:
                return result

            print("No relevant function found. Ignoring.")
            print(event)

            return {
                'statusCode': 200,
                'body': json.dumps("No relevant function found. Ignoring event. Sentry version: " + sentry_sdk.VERSION)
            }
