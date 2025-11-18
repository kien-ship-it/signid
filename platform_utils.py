"""
Cross-platform utilities for camera and system operations
"""
import cv2
import platform
import os


def get_camera_backend():
    """
    Get the appropriate camera backend for the current platform.
    
    Returns:
        int: OpenCV camera backend constant
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return cv2.CAP_AVFOUNDATION
    elif system == "Windows":
        return cv2.CAP_DSHOW  # DirectShow for Windows
    elif system == "Linux":
        return cv2.CAP_V4L2  # Video4Linux2 for Linux
    else:
        return cv2.CAP_ANY  # Auto-detect


def initialize_camera(camera_index=0, target_fps=60):
    """
    Initialize camera with platform-specific optimizations.
    
    Args:
        camera_index: Camera device index (default: 0)
        target_fps: Target frames per second (default: 60)
    
    Returns:
        tuple: (camera_object, actual_fps, width, height, backend_name)
    """
    backend = get_camera_backend()
    backend_names = {
        cv2.CAP_AVFOUNDATION: "AVFoundation (macOS)",
        cv2.CAP_DSHOW: "DirectShow (Windows)",
        cv2.CAP_V4L2: "Video4Linux2 (Linux)",
        cv2.CAP_ANY: "Auto-detect"
    }
    
    cam = cv2.VideoCapture(camera_index, backend)
    
    if not cam.isOpened():
        # Fallback to auto-detect
        cam = cv2.VideoCapture(camera_index)
        backend = cv2.CAP_ANY
    
    if not cam.isOpened():
        raise RuntimeError(f"Could not open camera {camera_index}")
    
    # Set camera properties with platform-specific handling
    cam.set(cv2.CAP_PROP_FPS, target_fps)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
    
    # Try MJPG codec for better performance (may not work on all platforms)
    try:
        cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    except:
        pass  # Ignore if not supported
    
    # Get actual camera properties
    actual_fps = cam.get(cv2.CAP_PROP_FPS)
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    backend_name = backend_names.get(backend, "Unknown")
    
    return cam, actual_fps, width, height, backend_name


def find_instruction_image():
    """
    Find the hand sign instruction image.
    
    Returns:
        str or None: Path to instruction image if found, None otherwise
    """
    # Primary location
    image_path = os.path.join(os.path.dirname(__file__), "resources", "handSignInstructions.png")
    
    if os.path.exists(image_path):
        return image_path
    
    return None


def get_platform_info():
    """
    Get detailed platform information for debugging.
    
    Returns:
        dict: Platform information
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }
