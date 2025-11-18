#!/usr/bin/env python3
"""
Test script to measure actual camera FPS and display refresh rate
Cross-platform compatible version
"""
import cv2
import time
from platform_utils import initialize_camera, get_platform_info

print("Testing camera FPS and display refresh rate...")
print("=" * 60)

# Print platform information
platform_info = get_platform_info()
print(f"Platform: {platform_info['system']} {platform_info['release']}")
print(f"Machine: {platform_info['machine']}")
print(f"Python: {platform_info['python_version']}")
print("=" * 60)

# Initialize camera with cross-platform support
try:
    cam, actual_fps, width, height, backend_name = initialize_camera(camera_index=0, target_fps=60)
    print(f"\nCamera Settings:")
    print(f"  Backend: {backend_name}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Reported FPS: {actual_fps}")
    print("=" * 60)
except RuntimeError as e:
    print(f"Error: {e}")
    exit(1)

# Create optimized window
cv2.namedWindow("FPS Test", cv2.WINDOW_NORMAL)

# Measure actual FPS
frame_count = 0
start_time = time.time()
last_report = start_time

print("\nMeasuring actual FPS (press ESC to quit)...")
print("Waiting for stable measurement...\n")

while True:
    ret, frame = cam.read()
    if not ret:
        break
    
    frame_count += 1
    current_time = time.time()
    elapsed = current_time - start_time
    
    # Calculate and display FPS every second
    if current_time - last_report >= 1.0:
        fps = frame_count / elapsed
        
        # Draw FPS on frame
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(frame, f"Frames: {frame_count}", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(frame, f"Time: {elapsed:.1f}s", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        print(f"Actual FPS: {fps:.2f} | Frames: {frame_count} | Time: {elapsed:.1f}s")
        last_report = current_time
    
    cv2.imshow("FPS Test", frame)
    
    # Use 1ms wait for minimal delay
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Final report
final_time = time.time() - start_time
final_fps = frame_count / final_time

print("\n" + "=" * 60)
print("FINAL RESULTS:")
print(f"  Total Frames: {frame_count}")
print(f"  Total Time: {final_time:.2f}s")
print(f"  Average FPS: {final_fps:.2f}")
print(f"  Expected FPS: {actual_fps}")
print(f"  Performance: {(final_fps/actual_fps)*100:.1f}% of reported FPS")
print("=" * 60)

cam.release()
cv2.destroyAllWindows()
