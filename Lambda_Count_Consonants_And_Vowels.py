def lambda_handler(event, context):
    text = event["text"]
    
    vowels = 0
    consonants = 0

    for letter in text:
        if letter.lower() in "aeiou":
            vowels += 1
        elif letter.lower() in "bcdfghjklmnpqrstvwxyz":
            consonants += 1

    return {
        'vowels': vowels,
        'consonants': consonants
    }