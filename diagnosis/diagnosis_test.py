import joblib
import pandas as pd

# Load model and encoder
clf = joblib.load('cbc_disease_model.joblib')
label_encoder = joblib.load('disease_label_encoder.joblib')

# New patient input for Bacterial Infection
new_patient = pd.DataFrame([{
    'WBC': 16000, 'LY%': 15,'MO%': 5,'NE%': 78,'EO%': 1,'BA%': 0.2,'LY#': 2400,'MO#': 800,'NE#': 12480,
    'EO#': 160,'BA#': 32,'RBC': 4.8,'HGB': 13.5,'HCT': 42.0,'MCV': 88,'MCHC': 33,'MCH': 29,'RDW': 13.5,
    'PLT': 270000,'MPV': 9.5,'Age': 38,'Gender': 1 #1->male 0-> female
}])

# Predict top label
prediction = clf.predict(new_patient)
predicted_disease = label_encoder.inverse_transform(prediction)
print("🧾 Most Probable Disease:", predicted_disease[0])

# Predict probabilities
probas = clf.predict_proba(new_patient)[0]
sorted_indices = probas.argsort()[::-1]
top_diseases = [(label_encoder.classes_[i], round(probas[i], 4)) for i in sorted_indices[:5]]

# Print ranked results
print("🔍 Predicted disease rankings:")
for rank, (disease, prob) in enumerate(top_diseases, 1):
    print(f"{rank}. {disease} — {prob * 100:.2f}%")
