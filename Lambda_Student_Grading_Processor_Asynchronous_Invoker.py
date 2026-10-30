import json
import os

import boto3

# Create Lambda client
lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    payload = {
        "student_name": event.get("student_name", "Unknown"),
        "marks": event.get("marks", 0),
    }

    # Invoke processor Lambda function asynchronously
    response = lambda_client.invoke(
        FunctionName=os.environ["PROCESSOR_FUNCTION"],
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8")
    )

    return {
        "statusCode": 202,
        "body": "Invocation accepted"
    }