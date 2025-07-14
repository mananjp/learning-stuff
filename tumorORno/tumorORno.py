from datasets import load_dataset
from PIL import Image
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from collections import Counter
import joblib

# parameters for the images
TARGET_IMAGE_SIZE = (64, 64)
MIN_SAMPLES_PER_CLASS = 3000

#  Load dataset in streaming mode
dataset = load_dataset("hungngo04/brain-tumor-binary-classification-dataset", split="train", streaming=True)

# Collect balanced samples
X, y = [], []
label_counter = Counter()
for sample in dataset:
    label = sample["label"]
    img = sample["image"].convert("L").resize(TARGET_IMAGE_SIZE)
    X.append(np.array(img).flatten())
    y.append(label)
    label_counter[label] += 1
    # Stop when both classes have enough samples
    if len(label_counter) == 2 and min(label_counter.values()) >= MIN_SAMPLES_PER_CLASS:
        break

print('Loaded label counts:', label_counter)

X = np.array(X)
y = np.array(y)

# Check class distribution before splitting
print("Full dataset class distribution:", Counter(y))

# Stratified(classified) train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training set class distribution:", Counter(y_train))
print("Test set class distribution:", Counter(y_test))

# build and train logistic regression model
pipeline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)) #standarscaler()->normalising data
pipeline.fit(X_train, y_train)

joblib.dump(pipeline, 'tumor_detector.pkl') #saving the model
# evaluate the model
y_pred = pipeline.predict(X_test)
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
