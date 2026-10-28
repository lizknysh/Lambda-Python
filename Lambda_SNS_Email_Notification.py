import json
import boto3

# SNS topic ARN
TOPIC_ARN = "arn:aws:sns:us-east-1:646418206778:lambda-email-alerts"

# Initialize SNS client in the same region as the topic
sns = boto3.client("sns", region_name="us-east-1")


def lambda_handler(event, context):
    subject = event.get("subject", "Lambda SNS Test Email")
    message = event.get(
        "message",
        "Hello! This email was published by AWS Lambda through SNS."
    )

    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=message
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "result": "Published to SNS",
            "messageId": response["MessageId"]
        })
    }