import base64
import html
from datetime import datetime, timezone
from string import Template
from urllib.parse import parse_qs, urlencode

import boto3

# Uses the Lambda execution role to access DynamoDB.
table = boto3.resource("dynamodb").Table("MCITStudents")


PAGE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <title>MCIT Student Manager</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 40px 16px;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a, #2563eb);
            color: #172033;
        }

        main {
            max-width: 500px;
            margin: auto;
            padding: 30px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }

        h1 {
            margin-top: 0;
        }

        p {
            line-height: 1.5;
        }

        form {
            display: grid;
            gap: 12px;
        }

        label {
            font-weight: bold;
        }

        input,
        button {
            width: 100%;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
        }

        input {
            border: 1px solid #94a3b8;
        }

        button {
            border: none;
            background: #1d4ed8;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #1e40af;
        }

        input:focus-visible,
        button:focus-visible {
            outline: 3px solid #2563eb;
            outline-offset: 3px;
        }

        .message {
            color: #166534;
        }

        .note {
            color: #64748b;
            font-size: 13px;
        }

        hr {
            margin: 24px 0;
            border: none;
            border-top: 1px solid #e2e8f0;
        }
    </style>
</head>

<body>
    <main>
        <h1>MCIT Student Manager</h1>
        <p>Create, find, and update a student record.</p>

        <p class="message" role="status">$message</p>

        <h2>Find a Student</h2>

        <form method="GET" action="/">
            <label for="lookup">Student ID</label>

            <input
                id="lookup"
                name="student_id"
                value="$student_id"
                maxlength="40"
                placeholder="Example: 10001"
                required
            >

            <button type="submit">Load Student</button>
        </form>

        <hr>

        <h2>Student Details</h2>

        <form method="POST" action="/">
            <label for="student-id">Student ID</label>

            <input
                id="student-id"
                name="student_id"
                value="$student_id"
                maxlength="40"
                required
            >

            <label for="name">Full Name</label>

            <input
                id="name"
                name="name"
                value="$name"
                maxlength="100"
                required
            >

            <label for="course">Course</label>

            <input
                id="course"
                name="course"
                value="$course"
                maxlength="100"
                required
            >

            <button type="submit">Save Student</button>
        </form>

        <p class="note">
            A new ID creates a record.
            An existing ID updates that record.
        </p>

        <p class="note">Last updated UTC: $updated_at</p>
    </main>
</body>
</html>
""")


def html_response(body, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
        "body": body,
    }


def lambda_handler(event, context):
    method = (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", "GET")
    )

    if method not in ("GET", "POST"):
        return html_response("Method not allowed.", 405)

    # Save the submitted student.
    if method == "POST":
        body = event.get("body") or ""

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")

        form = parse_qs(body)

        student_id = form.get("student_id", [""])[0].strip()
        name = form.get("name", [""])[0].strip()
        course = form.get("course", [""])[0].strip()

        if (
            not student_id
            or not name
            or not course
            or len(student_id) > 40
            or len(name) > 100
            or len(course) > 100
        ):
            return html_response(
                "<h2>Invalid input</h2>"
                "<p>Enter an ID, name, and course "
                "within the field limits.</p>"
                '<a href="/">Return to the form</a>',
                400,
            )

        table.put_item(
            Item={
                "student_id": student_id,
                "name": name,
                "course": course,
                "updated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        )

        # Redirect after saving to prevent repeat submissions
        # when the user refreshes the page.
        return {
            "statusCode": 303,
            "headers": {
                "Location": "/?" + urlencode({
                    "student_id": student_id,
                    "saved": "1",
                }),
                "Cache-Control": "no-store",
            },
            "body": "",
        }

    # Display the page and optionally load a student.
    query = event.get("queryStringParameters") or {}
    student_id = query.get("student_id", "").strip()

    if len(student_id) > 40:
        return html_response("Student ID is too long.", 400)

    student = {}

    if student_id:
        student = table.get_item(
            Key={"student_id": student_id},
            ConsistentRead=True,
        ).get("Item", {})

    message = ""

    if query.get("saved") == "1" and student:
        message = "Student saved successfully."
    elif student_id and not student:
        message = "Student not found. Enter details to create it."
    elif student:
        message = "Student loaded. Edit the details and save."

    # Escape values so user input is displayed safely as text.
    page = PAGE.substitute(
        message=html.escape(message),
        student_id=html.escape(student_id, quote=True),
        name=html.escape(student.get("name", ""), quote=True),
        course=html.escape(student.get("course", ""), quote=True),
        updated_at=html.escape(student.get("updated_at", "")),
    )

    return html_response(page)