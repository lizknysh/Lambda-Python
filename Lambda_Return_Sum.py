def lambda_handler(event, context):
    sum = int(event["a"]) + int(event["b"])

    result = event["alphabet1"] + event["alphabet2"]

    return {
        'sum': str(sum),
        'concatenation': result
    }