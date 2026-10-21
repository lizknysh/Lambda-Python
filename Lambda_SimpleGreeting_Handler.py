import json

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    name = params.get("name", "student")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": f"Hello, {name}!"
        })
    }
