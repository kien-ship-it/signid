# ASL Recognition - macOS Setup Guide

## Quick Start

### 1. Install Python 3.12
```bash
# Check version
python3.12 --version

# Install if needed
brew install python@3.12
```

**Important**: MediaPipe requires Python 3.8-3.12 (NOT 3.13+)

### 2. Setup Project
```bash
cd signid
chmod +x setup_unix.sh
./setup_unix.sh
```

### 3. Grant Camera Permissions
**System Settings** → **Privacy & Security** → **Camera** → Enable for Terminal

### 4. Run Application
```bash
source venv/bin/activate
python demo_with_game.py
```

## Applications

- **demo_with_game.py** - Interactive game with web console
- **demo.py** - Basic hand detection demo
- **test_camera_fps.py** - Camera performance test

## Troubleshooting

### Camera Not Working
1. Grant camera permissions in System Settings
2. Close other apps (Zoom, FaceTime)
3. Test: `python test_camera_fps.py`

### Python Version Error
```bash
brew install python@3.12
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Module Not Found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Performance
- **Apple Silicon**: 50-60 FPS
- **Intel Mac**: 40-50 FPS

## Commands
```bash
./setup_unix.sh              # Setup
source venv/bin/activate     # Activate
python verify_setup.py       # Verify
python demo_with_game.py     # Run game
```

**Happy signing! 🤟**
