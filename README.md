# Sign Language Recognition - Setup and Run Guide

This guide will help you install dependencies and run the different applications in this project.

# Demo
<img width="1512" height="982" alt="Screenshot 2025-11-16 at 06 41 13" src="https://github.com/user-attachments/assets/374a3dae-cd3b-43ee-8b4f-a511a4d87e62" />

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installing Dependencies](#installing-dependencies)
3. [Running the Applications](#running-the-applications)
4. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: Python 3.8 to 3.12 (mediapipe does not support Python 3.13+)
- **Camera**: Working webcam
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

---

## 📦 Installing Dependencies

### Step 1: Create Virtual Environment (Recommended)

```bash
# Navigate to the project directory
cd signid

# Create virtual environment with Python 3.12 (mediapipe requires Python 3.12 or lower)
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 2: Install Required Libraries

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required libraries
pip install -r requirements.txt

# Or install individually:
# pip install joblib mediapipe opencv-python numpy scikit-learn
```

#### Individual Library Installation

If you prefer to install libraries one by one:

```bash
# joblib - For loading trained ML models
pip install joblib

# mediapipe - Google's hand tracking library
pip install mediapipe

# opencv-python - Computer vision and camera handling
pip install opencv-python

# numpy - Numerical operations
pip install numpy

# scikit-learn - Machine learning library for model predictions
pip install scikit-learn
```

#### Library Descriptions

| Library           | Version     | Purpose                                                 |
| ----------------- | ----------- | ------------------------------------------------------- |
| **joblib**        | >=1.5.2     | Load pre-trained machine learning models (`.pkl` files) |
| **mediapipe**     | >=0.10.21   | Google's hand landmark detection and tracking           |
| **opencv-python** | >=4.11.0    | Camera capture, image processing, and display           |
| **numpy**         | >=1.26.4,<2 | Array operations and numerical computations             |
| **scikit-learn**  | >=1.7.2     | Machine learning algorithms and model training          |

### Step 3: Verify Installation

```bash
# Test if all libraries are installed correctly
python3 -c "import joblib, mediapipe, cv2, numpy, sklearn; print('✅ All libraries installed successfully!')"
```

If you see `✅ All libraries installed successfully!`, you're ready to go!

---

## 🚀 Running the Applications

### 1. **demo.py** - Basic Hand Sign Recognition

Simple camera-based hand sign recognition with real-time letter detection.

**Features:**

- Real-time hand tracking
- Letter prediction display
- Performance metrics (FPS, processing time)
- One-hand-at-a-time recognition

**How to Run:**

```bash
python3 demo.py
```

**Controls:**

- Show hand signs to the camera
- Press **ESC** to quit

**What You'll See:**

- Camera window with hand landmarks overlay
- Predicted letter displayed on screen
- FPS counter showing performance
- Hand sign instructions window

---

### 2. **demo_with_game.py** - Interactive Game with Web Console

Full-featured game application with a beautiful web-based control panel.

**Features:**

- Web-based game console (runs in browser)
- Real-time progress tracking
- Custom word input
- Visual letter-by-letter progress
- Camera feed with hand detection

**How to Run:**

```bash
python3 demo_with_game.py
```

**What Happens:**

1. Web browser opens automatically to `http://localhost:8765`
2. Camera window shows hand detection feed
3. Control the game from the web console

**Web Console Controls:**

- **Start (HELLO)** - Quick start with default word
- **Custom Word Input** - Type any word to practice
- **Reset Game** - Clear and restart

**Game Flow:**

1. Click "Start (HELLO)" or enter a custom word
2. Show the hand sign for each letter
3. Progress bar updates as you complete letters
4. See current target letter highlighted
5. Completion message when finished

**Controls:**

- Use web browser buttons/input fields
- Press **ESC** in camera window to quit

**What You'll See:**

- 📱 **Web Console**: Beautiful UI with status, progress, and controls
- 📸 **Camera Window**: Live feed with hand landmarks and FPS
- 🎯 **Target Letter**: Large display of current letter to sign
- ✅ **Progress Tracker**: Visual feedback on completed letters

---

### 3. **test_camera_fps.py** - Camera Performance Test

Diagnostic tool to measure actual camera FPS and performance.

**Features:**

- Real-time FPS measurement
- Frame count and timing statistics
- Performance comparison with reported FPS

**How to Run:**

```bash
python3 test_camera_fps.py
```

**What You'll See:**

- Camera feed with FPS overlay
- Console output with performance metrics
- Frame count and elapsed time
- Final performance summary

**Controls:**

- Press **ESC** to stop test

**Output Includes:**

- Actual FPS achieved
- Total frames captured
- Total time elapsed
- Performance percentage vs. reported FPS

**Example Output:**

```
Testing camera FPS and display refresh rate...
============================================================
Camera Settings:
  Backend: AVFoundation
  Resolution: 1280x720
  Reported FPS: 30.0
============================================================

Measuring actual FPS (press ESC to quit)...
Actual FPS: 29.85 | Frames: 298 | Time: 10.0s

============================================================
FINAL RESULTS:
  Total Frames: 1234
  Total Time: 41.35s
  Average FPS: 29.84
  Expected FPS: 30.0
  Performance: 99.5% of reported FPS
============================================================
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. **ModuleNotFoundError: No module named 'X'**

**Solution:** Install the missing library

```bash
pip install <library-name>
```

#### 2. **Camera not opening / "Error: Could not open camera"**

**Solutions:**

- Check if another application is using the camera
- Grant camera permissions to Terminal/Python
  - **macOS**: System Settings → Privacy & Security → Camera
  - **Windows**: Settings → Privacy → Camera
- Try different camera index:
  ```python
  # In the code, change:
  cam = cv2.VideoCapture(0)  # Try 1, 2, etc.
  ```

#### 3. **Web console not opening (demo_with_game.py)**

**Solutions:**

- Manually open browser to `http://localhost:8765`
- Check if port 8765 is already in use:

  ```bash
  # macOS/Linux
  lsof -i :8765

  # Windows
  netstat -ano | findstr :8765
  ```

- Change port in code if needed (search for `web_console_port = 8765`)

#### 4. **FileNotFoundError: predictor_v1.pkl or scaler_v1.pkl**

**Solution:** Ensure model files exist in the `archive/` directory

```bash
ls archive/
# Should show: predictor_v1.pkl and scaler_v1.pkl
```

#### 5. **Low FPS / Laggy performance**

**Solutions:**

- Close other applications
- Reduce camera resolution (if configurable)
- Use `test_camera_fps.py` to check baseline camera performance
- Check CPU usage

#### 6. **Hand not being detected**

**Solutions:**

- Ensure good lighting
- Position hand clearly in camera view
- Avoid complex backgrounds
- Check if hand landmarks are visible in camera feed

#### 7. **Wrong letters being detected**

**Solutions:**

- Ensure proper hand positioning (refer to instruction image)
- Keep hand steady for 1-2 seconds
- Ensure only one hand is in frame
- Good lighting is essential

---

## 📚 Additional Resources

### Project Files

- `demo.py` - Basic recognition demo
- `demo_with_game.py` - Interactive game with web console
- `test_camera_fps.py` - Camera performance test
- `utils.py` - Helper functions for drawing and overlays
- `archive/` - Contains trained ML models (`.pkl` files)
- `models/` - Contains MediaPipe hand landmark model

### Hand Sign Reference

The instruction image (`handSignInstructions.png`) shows the ASL alphabet hand signs.

---

## 💡 Tips for Best Experience

1. **Lighting**: Ensure good, even lighting on your hands
2. **Background**: Use a simple, uncluttered background
3. **Distance**: Position hand 1-2 feet from camera
4. **Steadiness**: Hold hand signs steady for 1-2 seconds
5. **One Hand**: Only show one hand at a time for accurate recognition
6. **Practice**: Start with simple words to get familiar with the system

---

## 🎮 Quick Start Commands

```bash
# 1. Setup (first time only)
python3.12 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

# 2. Run basic demo
python3 demo.py

# 3. Run interactive game
python3 demo_with_game.py

# 4. Test camera performance
python3 test_camera_fps.py
```

---

## ❓ Need Help?

If you encounter issues not covered here:

1. Check if all dependencies are installed correctly
2. Verify camera permissions are granted
3. Try running `test_camera_fps.py` to diagnose camera issues
4. Ensure Python version is 3.8 to 3.12 (not 3.13+): `python3 --version`
5. If using Python 3.13+, recreate your venv with Python 3.12: `python3.12 -m venv venv`
6. Check console output for specific error messages

---

**Enjoy practicing sign language! 🤟**
