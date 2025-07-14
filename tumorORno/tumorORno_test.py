from PIL import Image
import numpy as np
import joblib

# Load the trained model
pipeline = joblib.load('tumor_detector.pkl')

def preprocess_image(image_path):
    img = Image.open(image_path).convert('L').resize((64, 64))
    img_array = np.array(img).flatten()
    return img_array.reshape(1, -1)

img_features = preprocess_image('img_1.png')
prediction = pipeline.predict(img_features)[0]

if prediction == 1:
    print("Prediction: Tumor detected")
else:
    print("Prediction: No tumor detected")
