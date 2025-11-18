@echo off
REM Windows setup script for ASL Recognition

echo ============================================================
echo ASL Recognition - Windows Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8-3.12 from python.org
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
echo ✅ Pip upgraded

echo.
echo Step 4: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo Step 5: Verifying setup...
python verify_setup.py
if errorlevel 1 (
    echo ERROR: Setup verification failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run basic demo: python demo.py
echo   3. Run interactive game: python demo_with_game.py
echo.
echo ============================================================
pause
