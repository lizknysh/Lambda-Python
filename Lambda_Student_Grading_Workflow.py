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

    # Invoke processor Lambda function synchronously
    processor_response = lambda_client.invoke(
        FunctionName=os.environ["PROCESSOR_FUNCTION"],
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    # Check for processor errors
    if processor_response.get("FunctionError"):
        error_payload = json.loads(
            processor_response["Payload"].read().decode("utf-8")
        )
        raise RuntimeError(
            f"Processor failed: {error_payload}"
        )

    # Read and convert processor response into a Python dictionary
    processor_result = json.loads(
        processor_response["Payload"].read().decode("utf-8")
    )

    # Invoke notification Lambda function asynchronously
    lambda_client.invoke(
        FunctionName=os.environ["NOTIFICATION_FUNCTION"],
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    return {
        "statusCode": 200,
        "body": processor_result,
    }