import pandas as pd
import numpy as np

# Load your CBC data
cbc_df = pd.read_csv("cbc_dataframe.csv")

# Drop any rows that are completely empty
cbc_df = cbc_df.dropna(how='all').reset_index(drop=True)

# Step 1: Assign random age and gender
np.random.seed(42)
cbc_df['Age'] = np.random.randint(18, 81, size=len(cbc_df))
cbc_df['Gender'] = np.random.choice(['Male', 'Female'], size=len(cbc_df))

# Step 2: Define flagging and disease mapping function
def generate_flags_and_diseases(row):
    flags = []
    diseases = set()

    gender = row['Gender']
    hgb_thresh = 13.0 if gender == 'Male' else 12.0

    # ========== RBC Profile ==========
    if row.get('HGB', np.nan) < hgb_thresh:
        flags.append('Low_Hemoglobin')
        diseases.update(['Anemia', 'Chronic Kidney Disease'])

    if row.get('HGB', np.nan) > 17.5:
        flags.append('High_Hemoglobin')
        diseases.update(['Polycythemia Vera', 'Chronic Hypoxia'])

    if row.get('RBC', np.nan) < 4.2:
        flags.append('Low_RBC')
        diseases.update(['Anemia', 'Bone Marrow Suppression'])

    if row.get('RBC', np.nan) > 6.0:
        flags.append('High_RBC')
        diseases.update(['Polycythemia Vera', 'Dehydration'])

    # ========== MCV / MCH / RDW ==========
    if row.get('MCV', np.nan) < 80:
        flags.append('Low_MCV')
        diseases.update(['Iron Deficiency Anemia', 'Thalassemia'])

    if row.get('MCV', np.nan) > 100:
        flags.append('High_MCV')
        diseases.update(['Vitamin B12 Deficiency', 'Liver Disease', 'Hypothyroidism'])

    if row.get('MCH', np.nan) < 27:
        flags.append('Low_MCH')
        diseases.update(['Iron Deficiency Anemia'])

    if row.get('RDW', np.nan) > 14.5:
        flags.append('High_RDW')
        diseases.update(['Mixed Anemia', 'Nutritional Deficiency', 'Bone Marrow Disorders'])

    # ========== White Blood Cells ==========
    if row.get('WBC', np.nan) < 4.0:
        flags.append('Low_WBC')
        diseases.update(['Viral Infection', 'Bone Marrow Failure', 'Aplastic Anemia', 'Leukemia'])

    if row.get('WBC', np.nan) > 11.0:
        flags.append('High_WBC')
        diseases.update(['Bacterial Infection', 'Leukemia', 'Sepsis'])

    if row.get('NE%', np.nan) > 70:
        flags.append('High_Neutrophils')
        diseases.update(['Bacterial Infection', 'Sepsis', 'CML'])

    if row.get('LY%', np.nan) > 40:
        flags.append('High_Lymphocytes')
        diseases.update(['Viral Infection', 'Lymphocytic Leukemia'])

    if row.get('MO%', np.nan) > 10:
        flags.append('High_Monocytes')
        diseases.update(['Chronic Inflammation', 'Tuberculosis', 'Leukemia'])

    if row.get('EO%', np.nan) > 5:
        flags.append('High_Eosinophils')
        diseases.update(['Allergy', 'Parasitic Infection', 'Asthma'])

    if row.get('BA%', np.nan) > 1:
        flags.append('High_Basophils')
        diseases.update(['Chronic Myeloid Leukemia', 'Myeloproliferative Disease'])

    # ========== Platelets & MPV ==========
    if row.get('PLT', np.nan) < 150:
        flags.append('Low_Platelets')
        diseases.update(['Dengue', 'Bone Marrow Suppression', 'DIC', 'ITP'])

    if row.get('PLT', np.nan) > 450:
        flags.append('High_Platelets')
        diseases.update(['Iron Deficiency', 'Chronic Inflammation', 'Leukemia'])

    if row.get('MPV', np.nan) > 10.5 and row.get('PLT', np.nan) < 150:
        flags.append('High_MPV_with_Thrombocytopenia')
        diseases.update(['ITP', 'Bone Marrow Activation'])

    # Return
    flag_str = ', '.join(flags) if flags else None
    disease_str = ', '.join(sorted(diseases)) if diseases else None

    return pd.Series([flag_str, disease_str], index=['Flags', 'Probable_Diseases'])


# Step 3: Apply flagging
cbc_df[['Flags', 'Probable_Diseases']] = cbc_df.apply(generate_flags_and_diseases, axis=1)

# Step 4: Export to Excel
cbc_df.to_excel("expanded_integrated_flagged_cbc_dataset.xlsx", index=False)
print("✅ Dataset exported as 'expanded_integrated_flagged_cbc_dataset.xlsx'")
