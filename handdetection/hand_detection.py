import cv2
import mediapipe as mp
import numpy as np
import time
from google.protobuf.json_format import MessageToDict

# Initialize MediaPipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2,
                      min_detection_confidence=0.75, min_tracking_confidence=0.75)
mpDraw = mp.solutions.drawing_utils

def is_fist_closed(landmarks):
    """Detect if the hand is clenched (fist) by checking if all four fingers are folded."""
    fingers_folded = 0
    if landmarks[8].y > landmarks[5].y:   # Index finger
        fingers_folded += 1
    if landmarks[12].y > landmarks[9].y:  # Middle finger
        fingers_folded += 1
    if landmarks[16].y > landmarks[13].y: # Ring finger
        fingers_folded += 1
    if landmarks[20].y > landmarks[17].y: # Pinky finger
        fingers_folded += 1
    return fingers_folded == 4

def draw_color_palette(image, colors, selected_color_index):
    """Draw horizontal color palette on top-left of image."""
    start_x, start_y = 10, 10
    rect_size = 50
    spacing = 20  # Increased spacing for clearer separation

    for i, color in enumerate(colors):
        top_left = (start_x + i * (rect_size + spacing), start_y)
        bottom_right = (top_left[0] + rect_size, top_left[1] + rect_size)
        cv2.rectangle(image, top_left, bottom_right, color, -1)
        if i == selected_color_index:
            cv2.rectangle(image, top_left, bottom_right, (255, 255, 255), 3)
    return start_x, start_y, rect_size, spacing

def draw_pen_size_selector_vertical(image, sizes, selected_size_index):
    """Draw vertical pen size selector on right side of the image."""
    height, width, _ = image.shape
    size_box_size = 50
    spacing = 15
    start_x = width - size_box_size - 10  # Margin from right edge
    start_y = 60  # Moved down from top for visual balance

    for i, size in enumerate(sizes):
        top_left = (start_x, start_y + i * (size_box_size + spacing))
        bottom_right = (top_left[0] + size_box_size, top_left[1] + size_box_size)
        cv2.rectangle(image, top_left, bottom_right, (200, 200, 200), -1)  # Light gray bg
        center = (top_left[0] + size_box_size // 2, top_left[1] + size_box_size // 2)
        cv2.circle(image, center, size, (50, 50, 50), -1)  # Circle showing brush size
        if i == selected_size_index:
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 255), 3)  # Highlight selected
    return start_x, start_y, size_box_size, spacing

# Available colors (BGR format)
color_options = [
    (0, 0, 255),    # Red
    (0, 255, 0),    # Green
    (255, 0, 0),    # Blue
    (0, 255, 255),  # Yellow
    (255, 0, 255),  # Magenta
    (255, 255, 0),  # Cyan
    (0, 0, 0),      # Black
]

# Pen brush sizes (radius)
pen_sizes = [2, 10, 15, 20]

selected_color_index = 0
selected_pen_size_index = 0

last_color_change_time = 0
color_change_debounce = 0.3  # seconds

# Selection lock for stable color selection
palette_locked = False

cap = cv2.VideoCapture(0)
canvas = None
prev_idx_tip_draw = None

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)  # Mirror image for natural interaction
    if canvas is None:
        canvas = np.zeros_like(img)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Draw palettes
    palette_x, palette_y, palette_rect_size, palette_spacing = draw_color_palette(img, color_options, selected_color_index)
    pen_x, pen_y, pen_box_size, pen_spacing = draw_pen_size_selector_vertical(img, pen_sizes, selected_pen_size_index)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            handedness_dict = MessageToDict(hand_handedness)
            label = handedness_dict['classification'][0]['label']  # "Left" or "Right"
            h, w, _ = img.shape
            lm = hand_landmarks.landmark
            x, y = int(lm[8].x * w), int(lm[8].y * h)  # Index finger tip coords

            if label == 'Right':
                margin = 6  # Increased to reduce border sensitivity
                current_time = time.time()

                palette_area_x1 = palette_x
                palette_area_x2 = palette_x + len(color_options) * (palette_rect_size + palette_spacing) - palette_spacing
                palette_area_y1 = palette_y
                palette_area_y2 = palette_y + palette_rect_size

                # Detect if finger is inside entire palette area horizontally and vertically
                if palette_area_y1 <= y <= palette_area_y2:
                    if palette_area_x1 <= x <= palette_area_x2:
                        if not palette_locked:
                            for i in range(len(color_options)):
                                block_x_start = palette_x + i * (palette_rect_size + palette_spacing) + margin
                                block_x_end = block_x_start + (palette_rect_size - 2 * margin)
                                if block_x_start <= x <= block_x_end:
                                    # Apply debounce and update selection
                                    if (current_time - last_color_change_time) > color_change_debounce:
                                        if selected_color_index != i:
                                            selected_color_index = i
                                            prev_idx_tip_draw = None
                                            last_color_change_time = current_time
                                    palette_locked = True
                                    break
                    else:
                        # Finger outside horizontally - unlock palette to allow next selection
                        if palette_locked:
                            palette_locked = False
                else:
                    # Finger outside vertically - unlock palette
                    if palette_locked:
                        palette_locked = False

                # Pen size selector (vertical) on right side
                if pen_x <= x <= pen_x + pen_box_size:
                    for i in range(len(pen_sizes)):
                        block_y_start = pen_y + i * (pen_box_size + pen_spacing)
                        block_y_end = block_y_start + pen_box_size
                        if block_y_start <= y <= block_y_end:
                            if selected_pen_size_index != i:
                                selected_pen_size_index = i
                                prev_idx_tip_draw = None
                            break

                # Drawing if not in palettes and fist not clenched
                if not (palette_area_y1 <= y <= palette_area_y2 and palette_area_x1 <= x <= palette_area_x2) and not (pen_x <= x <= pen_x + pen_box_size and pen_y <= y <= pen_y + len(pen_sizes)*(pen_box_size + pen_spacing)):
                    if not is_fist_closed(lm):
                        if prev_idx_tip_draw is not None:
                            cv2.line(canvas, prev_idx_tip_draw, (x, y), color_options[selected_color_index], pen_sizes[selected_pen_size_index])
                        prev_idx_tip_draw = (x, y)
                    else:
                        prev_idx_tip_draw = None

            elif label == 'Left':
                # Erasing with left hand index finger
                cv2.circle(canvas, (x, y), 20, (0, 0, 0), -1)

            mpDraw.draw_landmarks(img, hand_landmarks, mpHands.HAND_CONNECTIONS)
    else:
        prev_idx_tip_draw = None
        palette_locked = False  # Reset lock when no hands detected

    # Overlay canvas on webcam
    img_out = cv2.addWeighted(img, 0.7, canvas, 0.7, 0)
    cv2.imshow("Virtual Drawing", img_out)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        canvas = np.zeros_like(canvas)  # Clear the canvas
    if key == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
