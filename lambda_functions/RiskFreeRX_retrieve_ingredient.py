import json
import os
import requests
import openai

def lambda_handler(event, context):
    ndc = event.get("ndc")
    if not ndc:
        return {"error": "Missing 'ndc' parameter"}
    
    openfda_url = f"https://api.fda.gov/drug/label.json?search=openfda.product_ndc:{ndc}"
    
    try:
        response = requests.get(openfda_url)
        response.raise_for_status()
        data = response.json()
        
        if "results" not in data or not data["results"]:
            return {"error": "No results found for the given NDC"}
        
        drug_data = data["results"][0]
        generic_name = drug_data.get("openfda", {}).get("generic_name", ["Unknown"])[0]
        active_ingredients = [ai["name"] for ai in drug_data.get("active_ingredient", [])]
        inactive_ingredients = drug_data.get("inactive_ingredient", [])
        
        if not inactive_ingredients:
            inactive_ingredients = get_inactive_ingredients_from_openai(drug_data)
        
        return {
            "generic_name": generic_name,
            "active_ingredients": active_ingredients,
            "inactive_ingredients": inactive_ingredients,
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data from OpenFDA: {str(e)}"}

def get_inactive_ingredients_from_openai(drug_data):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Extract structured data from the given JSON."},
                {"role": "user", "content": f"Here is the JSON: {json.dumps(drug_data)}\n\nExtract the inactive ingredients in this format:\n\n{{\"generic_name\": str, \"active_ingredients\": list[str], \"inactive_ingredients\": list[str]}}"}
            ]
        )
        parsed_response = json.loads(response["choices"][0]["message"]["content"])
        return parsed_response.get("inactive_ingredients", [])
    except Exception as e:
        return ["Error extracting from OpenAI"]
