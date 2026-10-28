def lambda_handler(event, context):
    text = event["text"]
    
    return {
        "original": text,
        "reversed": text[::-1]
    }