import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:5000/extract-text"

st.title("Google Vision Text Extraction")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    
    if st.button("Extract Text"):
        response = requests.post(API_URL, json={"encoded_image": encoded_image})
        
        if response.status_code == 200:
            ndc_code = response.json().get("ndc_code", "No text found.")
            st.text_area("Extracted Text:", ndc_code, height=200)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
