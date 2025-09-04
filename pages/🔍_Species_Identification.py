import streamlit as st
from PIL import Image

st.title("🔍 Species Identification - Indian Marine Biodiversity Platform")

uploaded_file = st.file_uploader("Upload a fish/marine species image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    st.info("AI model inference coming soon!")
