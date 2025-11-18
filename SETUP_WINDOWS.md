# ASL Recognition - Windows Setup Guide

## Quick Start

### 1. Install Python 3.12
1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important**: Check "Add Python to PATH"

**Important**: MediaPipe requires Python 3.8-3.12 (NOT 3.13+)

### 2. Setup Project
```cmd
# Navigate to project directory
cd signid

# Run automated setup
setup_windows.bat
```

### 3. Grant Camera Permissions
1. Open **Settings** → **Privacy** → **Camera**
2. Enable "Allow desktop apps to access your camera"

### 4. Run Application
```cmd
venv\Scripts\activate
python demo_with_game.py
```

## Troubleshooting

### Camera Not Working
1. Grant camera permissions in Windows Settings
2. Close other apps using camera (Teams, Skype)
3. Run: `python test_camera_fps.py`
4. Try different camera index (0, 1, 2)

### Python Version Error
1. Uninstall Python 3.13+ if installed
2. Install Python 3.12 from python.org
3. Recreate virtual environment:
```cmd
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Module Not Found
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### PowerShell Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

## Performance
- **Modern PC**: 30-50 FPS
- **Older PC**: 20-30 FPS

## Commands

### Command Prompt
```cmd
setup_windows.bat            # Setup
venv\Scripts\activate        # Activate
python verify_setup.py       # Verify
python demo_with_game.py     # Run game
python demo.py               # Run basic demo
```

### PowerShell
```powershell
.\setup_windows.bat          # Setup
venv\Scripts\Activate.ps1    # Activate
python verify_setup.py       # Verify
python demo_with_game.py     # Run game
python demo.py               # Run basic demo
```

**Happy signing! 🤟**
