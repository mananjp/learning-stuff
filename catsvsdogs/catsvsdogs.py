import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import warnings

warnings.filterwarnings('ignore')

from ultralytics import YOLO

# Load YOLOv8 model
print("Loading YOLOv8 model...")
model = YOLO('yolov8m.pt')


def predict_is_dog_yolo(image_path, conf_threshold=0.3):
    """
    Uses YOLOv8 to detect dogs and cats in image
    Returns probability image contains a dog vs cat
    """
    try:
        results = model(image_path, conf=conf_threshold, verbose=False)
        dog_detections = []
        cat_detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id].lower()
                confidence = float(box.conf[0])

                if class_name == 'dog':
                    dog_detections.append(confidence)
                elif class_name == 'cat':
                    cat_detections.append(confidence)

        max_dog_conf = max(dog_detections) if dog_detections else 0.0
        max_cat_conf = max(cat_detections) if cat_detections else 0.0
        total_conf = max_dog_conf + max_cat_conf

        if total_conf > 0:
            is_dog_prob = max_dog_conf / total_conf
        else:
            is_dog_prob = 0.5

        return np.clip(is_dog_prob, 0.005, 0.995)

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return 0.5


# Get base directory (works in both Windows and Docker)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Set test and output directories (relative to script location)
test_dir = os.path.join(base_dir, 'images')
output_dir = os.path.join(base_dir, 'output')

# Create directories if they don't exist
os.makedirs(test_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Get list of test images
test_files = sorted([f for f in os.listdir(test_dir)
                     if f.endswith(('.jpg', '.jpeg', '.png'))])

print(f"\nProcessing {len(test_files)} test images with YOLOv8...")

predictions = []
image_ids = []

for filename in tqdm(test_files, desc="YOLOv8 Detection"):
    image_path = os.path.join(test_dir, filename)
    pred = predict_is_dog_yolo(image_path)

    image_id = os.path.splitext(filename)[0]
    image_ids.append(image_id)
    predictions.append(pred)

# Create submission dataframe
submission_option3 = pd.DataFrame({
    'id': image_ids,
    'is_dog': predictions
})

# Save submission
output_file = os.path.join(output_dir, 'submission_option3_yolo.csv')
submission_option3.to_csv(output_file, index=False)

print(f"\n✓ Option 3 Submission saved!")
print(f"Output file: {output_file}")
print(f"Total predictions: {len(submission_option3)}")
print(f"Dog probability range: {submission_option3['is_dog'].min():.3f} - {submission_option3['is_dog'].max():.3f}")
print(f"\nFirst 10 predictions:")
print(submission_option3.head(10))
