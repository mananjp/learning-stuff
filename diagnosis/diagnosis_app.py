import streamlit as st
import pandas as pd
import joblib
import numpy as np
from PIL import Image

# Load trained model and label encoder
clf = joblib.load('cbc_disease_model.joblib')
label_encoder = joblib.load('disease_label_encoder.joblib')

FEATURE_ORDER = [
    'WBC', 'LY%', 'MO%', 'NE%', 'EO%', 'BA%', 'LY#', 'MO#', 'NE#', 'EO#', 'BA#',
    'RBC', 'HGB', 'HCT', 'MCV', 'MCHC', 'MCH', 'RDW', 'PLT', 'MPV', 'Age', 'Gender'
]

st.title("🩸 CBC Disease Prediction Web App")

st.markdown("""
Upload your CBC data or a blood report image to get a ranked prediction of possible diseases.
""")

option = st.radio("Input method:", ("Upload Image & Enter Data Manually", "Upload CBC as CSV/Excel File"))

if option == "Upload Image & Enter Data Manually":
    image_file = st.file_uploader("Upload CBC blood report image (JPG, PNG)", type=["jpg", "jpeg", "png"])
    if image_file:
        image = Image.open(image_file)
        st.image(image, caption="CBC Blood Report Image", use_column_width=True)
        st.info("Review and copy values from the image into the entry form below.")

    st.subheader("Enter Your Complete Blood Count (CBC) Values")

    user_input = {}

    # Demographics always at top
    demog_col, main_col1, main_col2 = st.columns([1, 2, 2])
    with demog_col:
        # Always show gender and age at the top
        gender_str = st.selectbox("Gender", ["Female", "Male"])
        user_input['Gender'] = 1 if gender_str == "Male" else 0
        user_input['Age'] = st.number_input("Age (years)", min_value=0, max_value=120, value=30)

    # Other CBC fields split nicely in two columns
    other_fields = [f for f in FEATURE_ORDER if f not in ["Gender", "Age"]]
    half = len(other_fields) // 2
    with main_col1:
        for field in other_fields[:half]:
            user_input[field] = st.number_input(f"{field}:", value=0.0, format="%.2f")
    with main_col2:
        for field in other_fields[half:]:
            user_input[field] = st.number_input(f"{field}:", value=0.0, format="%.2f")

    if st.button("Predict Disease"):
        df_input = pd.DataFrame([user_input])[FEATURE_ORDER]
        probas = clf.predict_proba(df_input)[0]
        sorted_indices = np.argsort(probas)[::-1]
        top_diseases = [(label_encoder.classes_[i], probas[i]) for i in sorted_indices[:5]]
        st.subheader("🧾 Predicted Disease Rankings")
        for rank, (disease, prob) in enumerate(top_diseases, 1):
            st.write(f"{rank}. **{disease}** — {prob * 100:.2f}%")

elif option == "Upload CBC as CSV/Excel File":
    data_file = st.file_uploader("Upload your CBC data file (.csv or .xlsx)", type=["csv", "xlsx"])
    if data_file:
        # Read uploaded file based on extension
        if data_file.name.endswith(".csv"):
            data = pd.read_csv(data_file)
        else:
            data = pd.read_excel(data_file)
        st.write("Uploaded CBC Data:")
        st.write(data)

        # Check for missing Age/Gender
        missing = []
        if 'Age' not in data.columns:
            missing.append('Age')
        if 'Gender' not in data.columns:
            missing.append('Gender')
        # Prompt as needed
        if missing:
            st.warning(f"Uploaded file is missing: {', '.join(missing)}")
            if 'Age' in missing:
                age_value = st.number_input("Enter Age (years)", min_value=0, max_value=120, value=30, key='age_up')
                data['Age'] = age_value
            if 'Gender' in missing:
                gender_choice = st.selectbox("Select Gender", ["Female", "Male"], key='gender_up')
                data['Gender'] = 1 if gender_choice == "Male" else 0

        # Reorder/limit columns and handle prediction for first row
        try:
            df_input = data[FEATURE_ORDER]
        except Exception:
            st.error("Uploaded file is missing other required columns.")
        else:
            # Only process the first row for prediction (can be expanded to batch)
            df_input_single = df_input.iloc[[0]]
            probas = clf.predict_proba(df_input_single)[0]
            sorted_indices = np.argsort(probas)[::-1]
            top_diseases = [(label_encoder.classes_[i], probas[i]) for i in sorted_indices[:5]]
            st.subheader("🧾 Predicted Disease Rankings")
            for rank, (disease, prob) in enumerate(top_diseases, 1):
                st.write(f"{rank}. **{disease}** — {prob * 100:.2f}%")
