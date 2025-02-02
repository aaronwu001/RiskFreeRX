import json
import os
import base64
import requests
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("GOOGLE_VISION_API_KEY")

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
    
def extract_ndc_code(text):
    """Extracts NDC code from given text"""
    pattern = r"NDC\s+([\d\s-]+)"
    matches = re.findall(pattern, text)
    cleaned_matches = [re.sub(r"\s+", "-", match.strip()) for match in matches]
    print(cleaned_matches)
    return cleaned_matches[0]

@app.route("/extract-text", methods=["POST"])
def extract_text():
    """Handles the image processing request."""
    try:
        data = request.get_json()
        encoded_image = data.get("encoded_image")

        if not encoded_image:
            return jsonify({"error": "Missing encoded_image field"}), 400

        extracted_text = extract_text_from_base64(encoded_image)
        
        # return jsonify({"extracted_text": extracted_text})
        ndc_code = extract_ndc_code(extracted_text)

        return jsonify({"ndc_code": ndc_code})

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
