import cv2
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList, NormalizedLandmark
from typing import Literal

MARGIN = 10
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)


def drawLandmarks(rgbImage, detectionResult, mode: Literal["overlay", "transparent"] = "overlay", predictions=[]):
	h, w, _ = rgbImage.shape
	landmarksList = detectionResult.hand_landmarks
	handednessList = detectionResult.handedness
	output = np.zeros(rgbImage.shape, dtype=np.uint8) if mode == "transparent" else np.copy(rgbImage)

	# Loop through detected hands
	for idx in range(len(landmarksList)):
		landmarks = landmarksList[idx]
		handedness = handednessList[idx]

		# Draw landmarks
		normalizedLandmarks = NormalizedLandmarkList()
		normalizedLandmarks.landmark.extend([NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in landmarks])
		solutions.drawing_utils.draw_landmarks(
			output,
			normalizedLandmarks,
			solutions.hands.HAND_CONNECTIONS,
			solutions.drawing_styles.get_default_hand_landmarks_style(),
			solutions.drawing_styles.get_default_hand_connections_style(),
		)

		x = [landmark.x for landmark in landmarks]
		y = [landmark.y for landmark in landmarks]
		textX = int(min(x) * w)
		textY = int(min(y) * h) - 20

		# Draw handedness
		cv2.putText(
			img=output,
			text=f"{handedness[0].category_name}",
			org=(textX, textY),
			fontFace=cv2.FONT_HERSHEY_DUPLEX,
			fontScale=1,
			color=(0, 0, 0),
			thickness=5,
			lineType=cv2.LINE_AA,
		)
		cv2.putText(
			img=output,
			text=f"{handedness[0].category_name}",
			org=(textX, textY),
			fontFace=cv2.FONT_HERSHEY_DUPLEX,
			fontScale=1,
			color=(255, 255, 255),
			thickness=2,
			lineType=cv2.LINE_AA,
		)

	return output


def draw_landmarks_on_image(rgb_image, detection_result, predictions):
	h, w, _ = rgb_image.shape
	hand_landmarks_list = detection_result.hand_landmarks
	annotated_image = np.zeros(rgb_image.shape, dtype=np.uint8)

	# Loop through the detected hands to visualize.
	for idx in range(len(hand_landmarks_list)):
		hand_landmarks = hand_landmarks_list[idx]

		hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
		hand_landmarks_proto.landmark.extend([
			landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
		])

		solutions.drawing_utils.draw_landmarks(
			annotated_image,
			hand_landmarks_proto,
			solutions.hands.HAND_CONNECTIONS,
			solutions.drawing_styles.get_default_hand_landmarks_style(),
			solutions.drawing_styles.get_default_hand_connections_style(),
		)

		# Use min(x), min(y) for top-left of hand, as in drawLandmarks
		xs = [landmark.x for landmark in hand_landmarks]
		ys = [landmark.y for landmark in hand_landmarks]
		text_x = int(min(xs) * w)
		text_y = int(min(ys) * h) - 20

		# Prepare letter display
		letter = str(predictions[idx])
		font = cv2.FONT_HERSHEY_SIMPLEX
		font_scale = 3.0  # Large font
		font_thickness = 8
		text_color = (255, 255, 255)  # White
		outline_color = (0, 0, 0)     # Black

		# Get text size
		size, baseline = cv2.getTextSize(letter, font, font_scale, font_thickness)
		text_w, text_h = size
		draw_x = max(text_x, 0)
		draw_y = max(text_y, text_h + MARGIN)

		# Create a transparent image for the letter
		letter_img = np.zeros((text_h + 20, text_w + 20, 4), dtype=np.uint8)
		# Draw filled rectangle for background
		cv2.rectangle(letter_img, (0, 0), (text_w + 20, text_h + 20), (0, 0, 0, 255), thickness=-1)
		# Draw letter with outline for visibility
		cv2.putText(
			letter_img,
			letter,
			(10, text_h + 10),
			font,
			font_scale,
			outline_color + (255,),
			font_thickness + 4,
			cv2.LINE_AA,
		)
		cv2.putText(
			letter_img,
			letter,
			(10, text_h + 10),
			font,
			font_scale,
			text_color + (255,),
			font_thickness,
			cv2.LINE_AA,
		)
		# Flip the letter image horizontally
		letter_img = cv2.flip(letter_img, 1)

		# Overlay the flipped letter image at the correct position
		# Compute overlay region
		overlay_x1 = draw_x
		overlay_y1 = draw_y - text_h - 10
		overlay_x2 = overlay_x1 + letter_img.shape[1]
		overlay_y2 = overlay_y1 + letter_img.shape[0]
		# Clip to image bounds
		overlay_x1 = max(0, overlay_x1)
		overlay_y1 = max(0, overlay_y1)
		overlay_x2 = min(w, overlay_x2)
		overlay_y2 = min(h, overlay_y2)
		# Compute region in letter_img
		img_x1 = 0
		img_y1 = 0
		img_x2 = overlay_x2 - overlay_x1
		img_y2 = overlay_y2 - overlay_y1
		# Overlay with alpha blending
		roi = annotated_image[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
		letter_roi = letter_img[img_y1:img_y2, img_x1:img_x2]
		alpha = letter_roi[:, :, 3:4] / 255.0
		roi[:] = (1 - alpha) * roi + alpha * letter_roi[:, :, :3]

	return annotated_image


def add_transparent_image(background, foreground):
	# Fast path: if foreground is all zeros, just return background
	if not np.any(foreground):
		return background
	
	# Create binary mask where foreground has content (much faster than alpha blending)
	mask = np.any(foreground > 0, axis=-1, keepdims=True).astype(np.uint8)
	
	# Fast overlay: only blend where mask is 1
	return np.where(mask, foreground, background)
