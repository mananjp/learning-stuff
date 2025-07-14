import streamlit as st
import joblib
from PIL import Image
import numpy as np

# Load your trained model
pipeline = joblib.load('tumor_detector.pkl')

def preprocess_image(image):
    img = image.convert('L').resize((64, 64))
    img_array = np.array(img).flatten()
    return img_array.reshape(1, -1)

st.title("Brain Tumor Detection")

uploaded_file = st.file_uploader("Upload an MRI image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded MRI', use_column_width=True)
    img_features = preprocess_image(image)
    prediction = pipeline.predict(img_features)[0]
    if prediction == 1:
        st.error("Tumor detected")
    else:
        st.success("No tumor detected")
