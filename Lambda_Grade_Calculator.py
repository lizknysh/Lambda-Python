def lambda_handler(event, context):
    name = event["name"]
    subject = event["subject"]
    marks = int(event["marks"])

    if marks < 0 or marks > 100:
        return {"Error": "Marks must be between 0 and 100."}

    if marks >= 80:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 60:
        grade = "C"
    elif marks >= 50:
        grade = "D"
    else:
        grade = "F"

    if marks >= 90:
        performance = "Excellent Performance!"
    else:
        performance = ""

    if marks >= 50:
        status = "Pass"
    else:
        status = "Fail"
        
    return {
        "student": name,
        "subject": subject,
        "marks": marks,
        "grade": grade,
        "status": status,
        "performance": performance
    }