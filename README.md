# Sign Language Recognition

Real-time ASL (American Sign Language) alphabet recognition using computer vision and machine learning.

![Demo Screenshot](https://github.com/user-attachments/assets/374a3dae-cd3b-43ee-8b4f-a511a4d87e62)

## Features

- 🎮 **Interactive Game Mode** - Practice spelling words with ASL signs
- 📹 **Real-time Hand Detection** - MediaPipe-powered hand tracking
- 🎯 **Letter Recognition** - ML model trained on ASL alphabet
- 🌐 **Web Console** - Beautiful browser-based game interface
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux

## Quick Start

### macOS
```bash
./setup_unix.sh
source venv/bin/activate
python demo_with_game.py
```

See [SETUP_MACOS.md](SETUP_MACOS.md) for detailed instructions.

### Windows
```cmd
setup_windows.bat
venv\Scripts\activate
python demo_with_game.py
```

See [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for detailed instructions.

### Linux
```bash
./setup_unix.sh
source venv/bin/activate
python demo_with_game.py
```

## Requirements

- **Python**: 3.8 to 3.12 (MediaPipe does NOT support 3.13+)
- **Camera**: Working webcam
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Applications

### Interactive Game (`demo_with_game.py`)
- Web-based control panel at `http://localhost:8765`
- Practice spelling custom words
- Real-time progress tracking
- Visual feedback for each letter

### Basic Demo (`demo.py`)
- Simple hand detection and letter recognition
- Performance metrics (FPS)
- Minimal interface

### Camera Test (`test_camera_fps.py`)
- Verify camera is working
- Measure actual FPS
- Performance diagnostics

## Project Structure

```
signid/
├── demo.py                    # Basic demo
├── demo_with_game.py          # Interactive game
├── platform_utils.py          # Cross-platform utilities
├── utils.py                   # Drawing utilities
├── verify_setup.py            # Setup verification
├── requirements.txt           # Python dependencies
├── archive/                   # ML models
│   ├── predictor_v1.pkl
│   └── scaler_v1.pkl
├── models/                    # MediaPipe model
│   └── hand_landmarker.task
└── resources/                 # Images
    └── handSignInstructions.png
```

## Troubleshooting

### Camera Not Working
1. Grant camera permissions in system settings
2. Close other apps using the camera
3. Run: `python test_camera_fps.py`

### Python Version Error
MediaPipe requires Python 3.8-3.12. If you have 3.13+:
- macOS: `brew install python@3.12`
- Windows: Download Python 3.12 from python.org

### Module Not Found
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## Performance

| Platform | Expected FPS |
|----------|-------------|
| macOS (Apple Silicon) | 50-60 |
| macOS (Intel) | 40-50 |
| Windows (Modern) | 30-50 |
| Linux | 30-45 |

## Tips for Best Results

1. **Good Lighting** - Bright, even lighting on hands
2. **Clear Background** - Simple, uncluttered background
3. **One Hand** - Show one hand at a time
4. **Steady Position** - Hold signs for 1-2 seconds
5. **Practice** - Start with simple words like "HELLO"

## Dependencies

- **joblib** - Model loading
- **mediapipe** - Hand tracking
- **opencv-python** - Camera and image processing
- **numpy** - Numerical operations
- **scikit-learn** - Machine learning

## License

See LICENSE file for details.

---

**Happy signing! 🤟**
