import json
import os
import base64
import requests
import re
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")  # Updated to match sample.env
API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def lambda_handler(event, context):
    """Handles the image processing request in AWS Lambda."""
    try:
        # Parse JSON request
        body = json.loads(event["body"])
        encoded_image = body.get("encoded_image")
        user_id = body.get("user_id")

        if not encoded_image:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing encoded_image field"})}
        
        if not user_id:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing user_id field"})}

        # Extract text using Google Vision API
        extracted_text = extract_text_from_base64(encoded_image)

        if extracted_text.startswith("Error:"):
            return {"statusCode": 500, "body": json.dumps({"error": extracted_text})}

        # Extract NDC code using regex
        ndc_code = extract_ndc_code(extracted_text)

        # Insert into Supabase
        image_id = insert_into_supabase(user_id, encoded_image, ndc_code)

        if image_id is None:
            return {"statusCode": 500, "body": json.dumps({"error": "Database insertion failed"})}

        # Return JSON response
        return {
            "statusCode": 200,
            "body": json.dumps({"image_id": image_id, "ndc_code": ndc_code})
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
    response_json = response.json()

    if response.status_code == 200 and "responses" in response_json and response_json["responses"]:
        texts = response_json["responses"][0].get("textAnnotations", [])
        return texts[0]["description"] if texts else "No text found."
    else:
        return f"Error: {response_json.get('error', 'Unknown API error')}"

def extract_ndc_code(text):
    """Extracts NDC code using regex pattern matching."""
    pattern = r"NDC\s\d{4,5}-\d{3,4}-\d{1,2}"
    matches = re.findall(pattern, text)
    
    return matches[0] if matches else "No NDC found"

def insert_into_supabase(user_id, encoded_image, extracted_text):
    """Inserts image data into Supabase and returns image_id."""
    try:
        data = {
            "user_id": user_id,
            "encoded_image": encoded_image,
            "extracted_text": extracted_text
        }
        response = supabase.table("images").insert(data).execute()

        if response.data and len(response.data) > 0 and "image_id" in response.data[0]:
            return response.data[0]["image_id"]
        else:
            return None

    except Exception as e:
        return None
