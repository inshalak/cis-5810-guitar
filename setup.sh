#!/bin/bash

set -e

echo "Air Guitar setup"
echo ""

if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 not found"
    echo "MediaPipe requires Python 3.12 (not compatible with 3.13 yet)"
    echo ""
    echo "Install Python 3.12:"
    echo "  brew install python@3.12"
    exit 1
fi

echo "Python 3.12 found"
echo ""

echo "Creating virtual environment"
python3.12 -m venv venv
echo "Virtual environment created"
echo ""

echo "Installing dependencies"
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install mediapipe opencv-python numpy pygame
echo "Dependencies installed"
echo ""

echo "Generating audio samples"
python generate_samples.py
echo ""

echo "Setup complete"
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
