import json
import os

import boto3


lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    # Prepare the payload
    payload = {
        "student_name": event.get("student_name", "Unknown"),
        "marks": event.get("marks", 0),
    }

    # Invoke the processor Lambda function
    response = lambda_client.invoke(
        FunctionName=os.environ["PROCESSOR_FUNCTION"],
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    # Read and decode the response
    result = json.loads(response["Payload"].read().decode("utf-8"))

    # Check for Lambda execution errors
    if response.get("FunctionError"):
        raise RuntimeError(f"MCIT-Processor failed: {result}")

    return {
        "statusCode": 200,
        "body": result,
    }