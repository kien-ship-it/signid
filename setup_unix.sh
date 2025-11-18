#!/bin/bash
# Unix setup script for ASL Recognition (macOS/Linux)

set -e  # Exit on error

echo "============================================================"
echo "ASL Recognition - Unix Setup (macOS/Linux)"
echo "============================================================"
echo ""

# Check if Python 3.12 is available
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✅ Found Python 3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Found Python $VERSION"
else
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8-3.12"
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -ne 3 ] || [ "$MINOR" -lt 8 ] || [ "$MINOR" -gt 12 ]; then
    echo "❌ ERROR: Python version $PYTHON_VERSION is not supported"
    echo "Please use Python 3.8-3.12 (MediaPipe requirement)"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
$PYTHON_CMD -m venv venv
echo "✅ Virtual environment created"

echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

echo ""
echo "Step 3: Upgrading pip..."
pip install --upgrade pip
echo "✅ Pip upgraded"

echo ""
echo "Step 4: Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "Step 5: Verifying setup..."
python verify_setup.py

echo ""
echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run basic demo: python demo.py"
echo "  3. Run interactive game: python demo_with_game.py"
echo ""
echo "============================================================"
