#!/usr/bin/env python3
"""
Quick verification script to check if everything is set up correctly
"""
import sys
import platform

print("="*60)
print("ASL Recognition - Setup Verification")
print("="*60)

# Check Python version
print("\n1. Checking Python version...")
py_version = sys.version_info
print(f"   Python {py_version.major}.{py_version.minor}.{py_version.micro}")

if py_version.major == 3 and 8 <= py_version.minor <= 12:
    print("   ✅ Python version is compatible")
elif py_version.major == 3 and py_version.minor >= 13:
    print("   ❌ Python 3.13+ is NOT supported by MediaPipe")
    print("   Please use Python 3.8-3.12")
    sys.exit(1)
else:
    print("   ❌ Python version not supported")
    sys.exit(1)

# Check platform
print("\n2. Checking platform...")
system = platform.system()
print(f"   {system} {platform.release()}")
print(f"   Machine: {platform.machine()}")
print("   ✅ Platform detected")

# Check required modules
print("\n3. Checking required modules...")
required_modules = [
    'joblib',
    'mediapipe',
    'cv2',
    'numpy',
    'sklearn'
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError:
        print(f"   ❌ {module} - NOT INSTALLED")
        missing_modules.append(module)

if missing_modules:
    print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Check custom modules
print("\n4. Checking custom modules...")
try:
    from platform_utils import get_camera_backend, get_platform_info
    print("   ✅ platform_utils")
except ImportError as e:
    print(f"   ❌ platform_utils - {e}")
    sys.exit(1)

try:
    from utils import draw_landmarks_on_image, add_transparent_image
    print("   ✅ utils")
except ImportError as e:
    print(f"   ❌ utils - {e}")
    sys.exit(1)

# Check model files
print("\n5. Checking model files...")
import os

model_files = [
    "archive/predictor_v1.pkl",
    "archive/scaler_v1.pkl",
    "models/hand_landmarker.task"
]

for file_path in model_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} - NOT FOUND")

# Check camera backend
print("\n6. Checking camera backend...")
try:
    backend = get_camera_backend()
    import cv2
    backend_names = {
        cv2.CAP_AVFOUNDATION: "AVFoundation (macOS)",
        cv2.CAP_DSHOW: "DirectShow (Windows)",
        cv2.CAP_V4L2: "Video4Linux2 (Linux)",
        cv2.CAP_ANY: "Auto-detect"
    }
    backend_name = backend_names.get(backend, "Unknown")
    print(f"   ✅ {backend_name}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
print("\n✅ All checks passed! You're ready to run the application.")
print("\nNext steps:")
print("  • Basic demo:        python demo.py")
print("  • Interactive game:  python demo_with_game.py")
print("  • Camera test:       python test_camera_fps.py")
print("\n" + "="*60)
