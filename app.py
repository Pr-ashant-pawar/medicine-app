import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import os
from dotenv import load_dotenv
import base64

# Load environment variables (recommended for API keys)
load_dotenv()

# Initialize OpenAI Client with settings for faster performance
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "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"),
    timeout=30.0,  # Set reasonable timeout
)

# Set page configuration with optimized settings
st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon="💊",
    layout="centered",  # Using centered layout for better performance
    initial_sidebar_state="collapsed"  # Keep sidebar collapsed for faster loading
)

# Streamlit App UI - Clean and minimal
st.title("Healthcare Assistant")
st.write("Get detailed information about medicines by entering a name or uploading an image.")

# Input methods: text or image
input_method = st.radio("Choose input method:", ["Enter Medicine Name", "Upload Medicine Image"])

if input_method == "Enter Medicine Name":
    medicine_name = st.text_input("Enter medicine name:")
    
    if st.button("Get Medicine Information", key="get_medicine_text") and medicine_name:
        with st.spinner("Retrieving information..."):
            try:
                prompt = f"""You are an expert in pharmacology and medicine information retrieval. 
                Provide well-structured, accurate, and human-understandable details for the medicine: {medicine_name}.
                Format the output in a markdown table with the following headers:
                | Medicine Name | Uses | Dosage | Side Effects | Precautions | Interactions | Storage Instructions | Alternative Medicines | Manufacturer Details | Legal Status |
                If the medicine is unknown, state that the data is unavailable for each field."""
                
                # Call the AI model to get medicine information
                completion = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://yourapplication.com",
                        "X-Title": "Medicine Information Retriever",
                    },
                    model="deepseek/deepseek-r1:free",
                    messages=[
                        {"role": "system", "content": "You are an expert in pharmacology and medicine information retrieval. Your task is to provide accurate medicine details."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Display medicine information
                if completion and hasattr(completion, 'choices') and len(completion.choices) > 0:
                    medicine_info = completion.choices[0].message.content
                    st.markdown(medicine_info)
                else:
                    st.error("Error: No response received from AI model. Please try again.")
                    
            except Exception as e:
                st.error(f"Error retrieving medicine information: {str(e)}")
                
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
                        
                        # Call the AI model to get medicine information
                        completion = client.chat.completions.create(
                            extra_headers={
                                "HTTP-Referer": "https://yourapplication.com",
                                "X-Title": "Medicine Information Retriever",
                            },
                            model="deepseek/deepseek-r1:free",
                            messages=[
                                {"role": "system", "content": "You are an expert in pharmacology and medicine information retrieval. Your task is to provide accurate medicine details."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        
                        # Display medicine information
                        if completion and hasattr(completion, 'choices') and len(completion.choices) > 0:
                            medicine_info = completion.choices[0].message.content
                            st.markdown(medicine_info)
                        else:
                            st.error("Error: No response received from AI model. Please try again.")
                            
                    except Exception as e:
                        st.error(f"Error retrieving medicine information: {str(e)}")
        except Exception as e:
            st.error(f"Error opening image: {str(e)}")

# Add a footer with minimal content
st.markdown("---")
st.markdown("Healthcare Assistant © 2025")
