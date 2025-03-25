```python
import streamlit as st
import requests
from PIL import Image
import io
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration with optimized settings
st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Streamlit App UI
st.title("Healthcare Assistant")
st.write("Get detailed information about medicines by entering a name or uploading an image.")

# Function to get medicine information from OpenRouter AI
def get_medicine_info(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourapplication.com",
        "X-Title": "Medicine Information Retriever",
    }
    
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "system", "content": "You are an expert in pharmacology and medicine information retrieval. Your task is to provide accurate medicine details."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", 
            headers=headers, 
            json=payload
        )
        response_data = response.json()
        
        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0]['message']['content']
        else:
            return "No information could be retrieved."
    
    except Exception as e:
        return f"Error retrieving medicine information: {str(e)}"

# Input methods: text or image
input_method = st.radio("Choose input method:", ["Enter Medicine Name", "Upload Medicine Image"])

if input_method == "Enter Medicine Name":
    medicine_name = st.text_input("Enter medicine name:")
    
    if st.button("Get Medicine Information", key="get_medicine_text") and medicine_name:
        with st.spinner("Retrieving information..."):
            prompt = f"""You are an expert in pharmacology and medicine information retrieval. 
            Provide well-structured, accurate, and human-understandable details for the medicine: {medicine_name}.
            Format the output in a markdown table with the following headers:
            | Medicine Name | Uses | Dosage | Side Effects | Precautions | Interactions | Storage Instructions | Alternative Medicines | Manufacturer Details | Legal Status |
            If the medicine is unknown, state that the data is unavailable for each field."""
            
            medicine_info = get_medicine_info(prompt)
            st.markdown(medicine_info)
                
else:  # Upload Medicine Image
    medicine_image = st.file_uploader("Upload medicine packaging image", type=["jpg", "jpeg", "png"], key="medicine_image")
    
    if medicine_image:
        try:
            # Using a smaller preview size for better performance
            img = Image.open(medicine_image)
            # Resize image for display to improve performance
            display_img = img.copy()
            if max(display_img.size) > 800:
                display_img.thumbnail((800, 800))
            st.image(display_img, caption="Uploaded Medicine Image", use_column_width=True)
            
            if st.button("Get Medicine Information", key="get_medicine_image"):
                with st.spinner("Analyzing image and retrieving information..."):
                    try:
                        # Convert image to byte format for potential OCR
                        img_byte_arr = io.BytesIO()
                        # Ensure format is specified
                        if hasattr(img, 'format') and img.format:
                            img.save(img_byte_arr, format=img.format)
                        else:
                            img.save(img_byte_arr, format='JPEG')
                        
                        img_bytes = img_byte_arr.getvalue()
                        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                        
                        prompt = """You are an expert in pharmacology and medicine information retrieval.
                        Analyze the uploaded image of medicine packaging. First extract the medicine name using OCR,
                        then provide well-structured, accurate details about this medicine.
                        Format the output in a markdown table with the following headers:
                        | Medicine Name | Uses | Dosage | Side Effects | Precautions | Interactions | Storage Instructions | Alternative Medicines | Manufacturer Details | Legal Status |
                        If the medicine is unknown or unrecognizable, state 'Invalid input. Please enter a valid medicine name or a clear image of the medicine label.'"""
                        
                        medicine_info = get_medicine_info(prompt)
                        st.markdown(medicine_info)
                            
                    except Exception as e:
                        st.error(f"Error retrieving medicine information: {str(e)}")
        except Exception as e:
            st.error(f"Error opening image: {str(e)}")

# Add a footer with minimal content
st.markdown("---")
st.markdown("Healthcare Assistant © 2025")
```
