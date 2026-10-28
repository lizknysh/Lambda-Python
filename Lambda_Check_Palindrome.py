def lambda_handler(event, context):
    text = event["text"]

    text = text.lower()
    
    if text == text[::-1]:
        result = True
    else:
        result = False

    return {
        "text": event["text"],
        "is_palindrome": result
    }