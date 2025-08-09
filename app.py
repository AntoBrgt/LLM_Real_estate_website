import streamlit as st
import json
from generator import generate_listing

st.set_page_config(page_title="Real Estate Listing Generator", layout="centered")

st.title("🏡 Real Estate Listing Generator")

st.markdown("""
Paste your property data in JSON format below, select language and tone, then click **Generate**.  
The app will generate SEO-optimized, multilingual listing content wrapped in exact HTML tags.
""")

default_json = json.dumps({
    "title": "T3 apartment in Lisbon",
    "location": {"city": "Lisbon", "neighborhood": "Campo de Ourique"},
    "features": {
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 120,
        "balcony": True,
        "parking": False,
        "elevator": True,
        "floor": 2,
        "year_built": 2005
    },
    "price": 650000,
    "listing_type": "sale",
    "language": "en"
}, indent=2)

uploaded_file = st.file_uploader("Upload your property JSON file", type=["json"])

json_input = ""

if uploaded_file is not None:
    try:
        json_input = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
else:
    json_input = default_json

json_input = st.text_area("Property JSON", value=json_input, height=300)

tone = st.selectbox("Select Tone", ["friendly", "formal", "luxury", "investor"], index=0)

if st.button("Generate"):

    try:
        data = json.loads(json_input)
        if "location" not in data or "city" not in data["location"]:
            st.error("JSON must include 'location' object with a 'city' field.")
            st.stop()
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON input: {e}")
        st.stop()

    with st.spinner("Generating content..."):
        try:
            html_output = generate_listing(data, tone=tone)
            st.markdown("### Generated HTML Content")
            st.code(html_output, language="html")
        except Exception as e:
            st.error(f"Error during generation: {e}")