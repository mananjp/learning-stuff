import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# --- Read your dataset ---
df = pd.read_excel('expanded_integrated_flagged_cbc_dataset.xlsx')  # Change to sep=',' if needed

# --- Preprocessing ---
df.columns = df.columns.str.strip().str.replace(' ', '_')
df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})

feature_cols = [
    'WBC', 'LY%', 'MO%', 'NE%', 'EO%', 'BA%', 'LY#', 'MO#', 'NE#', 'EO#', 'BA#',
    'RBC', 'HGB', 'HCT', 'MCV', 'MCHC', 'MCH', 'RDW', 'PLT', 'MPV', 'Age', 'Gender'
]
df[feature_cols] = df[feature_cols].apply(pd.to_numeric, errors='coerce')
df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())

# Use first probable disease
df['Label'] = df['Probable_Diseases'].fillna('None').apply(lambda x: x.split(',')[0].strip())
label_encoder = LabelEncoder()
df['Label_encoded'] = label_encoder.fit_transform(df['Label'])

# --- Model Training & Evaluation ---
X = df[feature_cols]
y = df['Label_encoded']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

import joblib

# Save model and label encoder to file
joblib.dump(clf, 'cbc_disease_model.joblib')
joblib.dump(label_encoder, 'disease_label_encoder.joblib')

print("✅ Model and label encoder saved successfully!")


# --- Accuracy and Report ---
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
