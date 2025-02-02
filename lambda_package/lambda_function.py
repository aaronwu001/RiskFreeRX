import json
import os
import base64
import re
import requests

# API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")

def lambda_handler(event, context):
    """Handles the image processing request in AWS Lambda."""

    try:
        # Parse JSON request
        encoded_image = event.get("encoded_image")

        if not encoded_image:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing encoded_image field"})}

        # Extract text using Google Vision API
        extracted_text = extract_text_from_base64(encoded_image)

        return {
            "extracted text": extracted_text
        }

    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON format"})}
    
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def extract_text_from_base64(encoded_image):
    """Extracts text from an image using Google Vision API."""
    url = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

    request_payload = {
        "requests": [
            {
                "image": {"content": encoded_image},
                "features": [{"type": "TEXT_DETECTION"}]
            }
        ]
    }

    response = requests.post(url, json=request_payload)

    if response.status_code == 200:
        response_json = response.json()
        texts = response_json["responses"][0].get("textAnnotations", [])
        return texts[0]["description"] if texts else "No text found."
    else:
        return f"Error: {response.json()}"
