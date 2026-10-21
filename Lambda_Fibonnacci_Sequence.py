def lambda_handler(event, context):
    n = int(event.get("n", 3))
 
    if n < 1 or n > 100:
        return {"error": "Enter a number between 1 and 100"}
 
    a = 0
    b = 1
    count = 0
    total = 0
    series = []
 
    while count < n:
        series.append(a)
        total = total + a
 
        next_number = a + b
        a = b
        b = next_number
 
        count = count + 1
 
    return {
        "terms": n,
        "series": series,
        "sum": total
    }