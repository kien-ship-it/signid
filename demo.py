import math
import joblib
import mediapipe as mp
import cv2
import numpy as np
import time
from utils import draw_landmarks_on_image, add_transparent_image

with open("archive/predictor_v1.pkl", "rb") as f:
	classifier = joblib.load(f)

with open("archive/scaler_v1.pkl", "rb") as f:
	scaler = joblib.load(f)

HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult

predictions = []
drawn_frame = np.array([])

# Globals for one-hand-at-a-time logic
tracked_hand_index = None
no_hand_counter = 0
NO_HAND_THRESHOLD = 1  # Number of consecutive frames with no hands before resetting

image_path = "/Users/leduckien/Downloads/handSignInstructions.png"
image = cv2.imread(image_path)
# Display instruction image
cv2.imshow("Hand Sign Instructions", image)

def print_result(result, output_image, timestamp_ms):
	try:
		landmarks_ls = result.hand_world_landmarks
		handedness_ls = result.handedness
		global predictions
		global drawn_frame
		global tracked_hand_index
		global no_hand_counter
		predictions = []

		if len(landmarks_ls) == 0:
			# No hands detected
			no_hand_counter += 1
			if no_hand_counter >= NO_HAND_THRESHOLD:
				tracked_hand_index = None
				drawn_frame = np.zeros_like(output_image.numpy_view())
			return
		else:
			no_hand_counter = 0

		# If only one hand is detected, always use that hand
		if len(landmarks_ls) == 1:
			tracked_hand_index = handedness_ls[0][0].index
			main_hand_idx = 0
		else:
			# Multiple hands detected
			# If no hand is tracked, pick the first detected hand
			if tracked_hand_index is None:
				tracked_hand_index = handedness_ls[0][0].index

			# Find the hand with the tracked index
			main_hand_idx = None
			for idx, handedness in enumerate(handedness_ls):
				if handedness[0].index == tracked_hand_index:
					main_hand_idx = idx
					break

			# If tracked hand not found, switch to the first available hand
			if main_hand_idx is None:
				tracked_hand_index = handedness_ls[0][0].index
				main_hand_idx = 0

		if main_hand_idx is not None:
			landmarks = np.array([[landmark.x, landmark.y, landmark.z] for landmark in landmarks_ls[main_hand_idx]]).flatten()
			handedness = handedness_ls[main_hand_idx][0].index
			data = scaler.transform(np.array([[handedness] + landmarks.tolist()]))
			prediction = classifier.predict(data)
			predictions.append(prediction[0])

			# Create a HandLandmarkerResult-like object with only the main hand
			class SingleHandResult:
				def __init__(self, hand_landmarks, handedness):
					self.hand_landmarks = [hand_landmarks]
					self.handedness = [handedness]
					self.hand_world_landmarks = []
			main_result = SingleHandResult(result.hand_landmarks[main_hand_idx], result.handedness[main_hand_idx])
			drawn_frame = draw_landmarks_on_image(output_image.numpy_view(), main_result, predictions)
		else:
			# Tracked hand not found, do not update drawn_frame
			pass
	except Exception as e:
		print(e)


options = mp.tasks.vision.HandLandmarkerOptions(
	base_options=mp.tasks.BaseOptions(model_asset_path="./models/hand_landmarker.task"),
	running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
	num_hands=2,
	result_callback=print_result,
	min_hand_detection_confidence=0.5,
	min_hand_presence_confidence=0.5,
	min_tracking_confidence=0.5,
)

# Initialize camera with AVFoundation backend for better performance on macOS
cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

# Set camera to highest FPS possible
cam.set(cv2.CAP_PROP_FPS, 60)  # Request 60 FPS
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPG codec for higher FPS
cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce latency

timestamp = 0
frame_count = 0

# Get actual camera FPS after configuration
camera_fps = cam.get(cv2.CAP_PROP_FPS)
width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Camera configured:")
print(f"  Resolution: {width}x{height}")
print(f"  FPS: {camera_fps}")
print(f"  Backend: AVFoundation")

# Create optimized display window
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

# FPS measurement variables
fps_start_time = time.time()
fps_frame_count = 0
display_fps = 0.0
last_fps_update = fps_start_time

# Performance tracking
processing_times = []
mediapipe_times = []
display_times = []

with HandLandmarker.create_from_options(options) as landmarker:
	while cam.isOpened():
		loop_start = time.time()
		
		ret, frame = cam.read()
		if not ret:
			print("Dead")
			break

		# Generate timestamp in milliseconds for MediaPipe
		frame_count += 1
		fps_frame_count += 1
		timestamp = int(frame_count * (1000.0 / camera_fps))
		
		# Process every frame (no interval throttling)
		mp_start = time.time()
		mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
		landmarker.detect_async(mp_img, timestamp)
		mp_time = (time.time() - mp_start) * 1000  # Convert to ms
		mediapipe_times.append(mp_time)

		# Measure overlay time
		overlay_start = time.time()
		if drawn_frame.size > 0:
			frame = add_transparent_image(frame, drawn_frame)
		overlay_time = (time.time() - overlay_start) * 1000
		
		# Calculate FPS every second
		current_time = time.time()
		if current_time - last_fps_update >= 1.0:
			display_fps = fps_frame_count / (current_time - last_fps_update)
			fps_frame_count = 0
			last_fps_update = current_time
			
			# Print performance metrics
			avg_mp_time = np.mean(mediapipe_times[-30:]) if mediapipe_times else 0
			avg_total_time = np.mean(processing_times[-30:]) if processing_times else 0
			print(f"FPS: {display_fps:.1f} | MediaPipe: {avg_mp_time:.1f}ms | Overlay: {overlay_time:.1f}ms | Total: {avg_total_time:.1f}ms")
		
		# Draw FPS on frame
		flipped_frame = cv2.flip(frame, 1)
		cv2.putText(flipped_frame, f"FPS: {display_fps:.1f}", (10, 30), 
		           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
		
		display_start = time.time()
		cv2.imshow("Camera", flipped_frame)
		display_time = (time.time() - display_start) * 1000
		display_times.append(display_time)

		# Track total loop time
		loop_time = (time.time() - loop_start) * 1000
		processing_times.append(loop_time)

		# Reduced wait time from 5ms to 1ms for higher refresh rate
		if cv2.waitKey(1) & 0xFF == 27:
			break

print("\n" + "="*60)
print("PERFORMANCE SUMMARY:")
print(f"  Average FPS: {len(processing_times) / (time.time() - fps_start_time):.1f}")
print(f"  Avg MediaPipe time: {np.mean(mediapipe_times):.1f}ms")
print(f"  Avg Display time: {np.mean(display_times):.1f}ms")
print(f"  Avg Total loop time: {np.mean(processing_times):.1f}ms")
print(f"  Max loop time: {np.max(processing_times):.1f}ms")
print("="*60)

cam.release()
cv2.destroyAllWindows()
