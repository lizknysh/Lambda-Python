import json


def lambda_handler(event, context):
    student_name = event.get("student_name", "Unknown")
    marks = event.get("marks", 0)

    # Notification message
    message = (
        f"Notification: {student_name} "
        f"received a mark of {marks}."
    )

    # Prints notification message to CloudWatch Logs
    print(message)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message
        })
    }