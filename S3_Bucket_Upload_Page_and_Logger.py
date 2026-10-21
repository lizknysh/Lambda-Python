import base64
import json
import logging
import os
import re
import uuid

import boto3
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_NAME = os.environ["BUCKET_NAME"]
MAX_BYTES = 10 * 1024 * 1024

s3 = boto3.client(
    "s3",
    region_name=os.environ["AWS_REGION"],
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"},
    ),
)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MCIT Cloud Upload</title>

  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      font-family: Arial, sans-serif;
      color: #17213b;
      background: linear-gradient(135deg, #eaf2ff, #f5edff);
    }

    .card {
      width: 100%;
      max-width: 480px;
      padding: 36px;
      background: white;
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(36, 53, 100, 0.12);
    }

    .badge {
      display: inline-block;
      padding: 7px 12px;
      border-radius: 20px;
      background: #edf2ff;
      color: #405ad5;
      font-size: 12px;
      font-weight: bold;
    }

    h1 { margin-bottom: 10px; }
    p { color: #65708a; line-height: 1.6; }

    .upload-box {
      margin: 24px 0;
      padding: 24px;
      border: 2px dashed #becaf1;
      border-radius: 16px;
      background: #f8faff;
    }

    input { width: 100%; margin-top: 14px; }

    button {
      width: 100%;
      padding: 15px;
      border: none;
      border-radius: 12px;
      background: #405ad5;
      color: white;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
    }

    button:disabled { opacity: 0.6; cursor: wait; }

    #status {
      margin-top: 20px;
      font-size: 14px;
      line-height: 1.6;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
    }

    .success { color: #147347; }
    .error { color: #b42318; }

    .footer {
      margin-top: 24px;
      font-size: 12px;
      color: #7a849b;
      text-align: center;
    }
  </style>
</head>

<body>
  <main class="card">
    <span class="badge">MCIT CLOUD LAB</span>
    <h1>Upload a file</h1>
    <p>Choose a document, image, or other file to store in Amazon S3.</p>

    <form id="uploadForm">
      <div class="upload-box">
        <label for="file"><strong>Select your file</strong></label>
        <input id="file" type="file" required>
        <p>Maximum file size: 10 MB.</p>
      </div>

      <button id="uploadButton" type="submit">Upload to S3</button>
    </form>

    <div id="status" role="status" aria-live="polite"></div>
    <div class="footer">AWS Lambda + Amazon S3</div>
  </main>

  <script>
    const form = document.getElementById("uploadForm");
    const button = document.getElementById("uploadButton");
    const status = document.getElementById("status");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const file = document.getElementById("file").files[0];
      if (!file) return;

      status.className = "";
      status.textContent = "";

      if (file.size === 0 || file.size > 10 * 1024 * 1024) {
        status.className = "error";
        status.textContent = "Choose a non-empty file smaller than 10 MB.";
        return;
      }

      button.disabled = true;
      button.textContent = "Uploading...";

      try {
        status.textContent = "Preparing your upload...";

        const response = await fetch("/upload", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            filename: file.name,
            size: file.size
          })
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Could not prepare upload.");
        }

        const data = new FormData();

        for (const [key, value] of Object.entries(result.fields)) {
          data.append(key, value);
        }

        // S3 requires the file field to be added last.
        data.append("file", file);

        status.textContent = "Uploading your file to S3...";

        const uploaded = await fetch(result.url, {
          method: "POST",
          body: data
        });

        if (!uploaded.ok) {
          throw new Error(
            "S3 rejected the upload (HTTP " + uploaded.status +
            "). Check the Lambda role permissions."
          );
        }

        status.className = "success";
        status.textContent =
          "Upload successful!\\nFile: " + file.name +
          "\\nS3 location: " + result.location;

        form.reset();

      } catch (error) {
        status.className = "error";
        status.textContent =
          error.message +
          "\\nIf the browser reports 'Failed to fetch', check S3 CORS.";

      } finally {
        button.disabled = false;
        button.textContent = "Upload to S3";
      }
    });
  </script>
</body>
</html>
"""


def response(status, body, content_type="application/json"):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": content_type,
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
        "body": (
            json.dumps(body)
            if content_type == "application/json"
            else body
        ),
    }


def lambda_handler(event, context):
    method = (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", "GET")
    )
    path = event.get("rawPath", "/")

    if method == "GET" and path == "/":
        return response(200, HTML, "text/html; charset=utf-8")

    if method == "POST" and path == "/upload":
        try:
            body = event.get("body") or "{}"

            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode("utf-8")

            payload = json.loads(body)

            if not isinstance(payload, dict):
                return response(400, {"error": "Invalid request."})

            filename = payload.get("filename")
            size = payload.get("size")

            if not isinstance(filename, str) or not filename.strip():
                return response(400, {"error": "A filename is required."})

            if (
                type(size) is not int
                or size < 1
                or size > MAX_BYTES
            ):
                return response(
                    400,
                    {"error": "File must be between 1 byte and 10 MB."},
                )

            # Remove directory paths and unsafe filename characters.
            filename = filename.replace("\\\\", "/").split("/")[-1]
            safe_name = re.sub(
                r"[^A-Za-z0-9._-]", "_", filename
            )[:150]

            if not safe_name or safe_name in (".", ".."):
                safe_name = "file"

            # A unique key prevents files with the same name overwriting.
            key = f"uploads/{uuid.uuid4().hex}_{safe_name}"

            upload = s3.generate_presigned_post(
                Bucket=BUCKET_NAME,
                Key=key,
                Conditions=[
                    ["content-length-range", 1, MAX_BYTES]
                ],
                ExpiresIn=300,
            )

            return response(
                200,
                {
                    "url": upload["url"],
                    "fields": upload["fields"],
                    "location": f"s3://{BUCKET_NAME}/{key}",
                },
            )

        except (ValueError, UnicodeError):
            return response(400, {"error": "Invalid request data."})

        except Exception:
            logger.exception("Could not prepare S3 upload")
            return response(
                500,
                {"error": "Could not prepare upload. Check CloudWatch logs."},
            )

    return response(404, {"error": "Page not found."})