def lambda_handler(event, context): 

    student_name = event.get("student_name", "Unknown") 
    marks = event.get("marks", 0) 

    if not isinstance(marks, (int, float)) or not 0 <= marks <= 100: 
        raise ValueError("marks must be a number between 0 and 100") 
    
    grade = "A" if marks >= 80 else "B" if marks >= 60 else "C" if marks >= 40 else "F" 
    
    return { 
        "student_name": student_name, 
        "marks": marks, 
        "grade": grade, 
        "message": "Student processed successfully" 
    } 