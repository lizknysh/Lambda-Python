def lambda_handler(event, context):
    text = event["text"]

    words = text.split()
    longest_word = max(words, key=len)

    return {
        "longest_word": longest_word
    }