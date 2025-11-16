import cv2
import mediapipe as mp
import numpy as np

def check_camera():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return False
    
    # Try to read frames
    for _ in range(10):
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Cannot read frames from the camera.")
            cap.release()
            return False
        
        # Check if the frame is not empty
        if frame is None or frame.size == 0:
            print("Error: Received empty frame.")
            cap.release()
            return False
        
        # Display basic frame information
        print(f"Frame shape: {frame.shape}, Frame type: {frame.dtype}")
        cv2.imshow('Camera Test', frame)
        
        # Break if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def check_mediapipe_hand_detection():
    # Import necessary MediaPipe modules
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    # Create HandLandmarker options
    base_options = python.BaseOptions(
        model_asset_path='/Users/leduckien/signid/models/hand_landmarker.task'
    )
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Create the hand landmarker
    landmarker = vision.HandLandmarker.create_from_options(options)

    # Open camera
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MP image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hands
        detection_result = landmarker.detect_for_video(mp_image, int(cv2.getTickCount() / cv2.getTickFrequency() * 1000))
        
        # Draw landmarks if hands are detected
        if detection_result.hand_landmarks:
            for landmarks in detection_result.hand_landmarks:
                for landmark in landmarks:
                    # Convert normalized coordinates to pixel coordinates
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        cv2.imshow('Hand Tracking', frame)
        
        # Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Run diagnostics
print("Checking camera:")
camera_status = check_camera()
print("\nCamera check complete.")

print("\nTesting MediaPipe Hand Detection:")
check_mediapipe_hand_detection()