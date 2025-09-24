#!/bin/bash

# Build script for Render deployment
# This ensures proper installation order and error handling

echo "🚀 Starting Class Bot deployment on Render..."
echo "Python version: $(python --version)"
echo "Platform: $(uname -a)"

# Upgrade pip first
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Update package list
echo "🔄 Updating system packages..."
apt-get update

# Install Tesseract OCR and dependencies
echo "👁️ Installing Tesseract OCR..."
apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev

# Install additional libraries for image processing
echo "🖼️ Installing image processing libraries..."
apt-get install -y libgl1-mesa-glx libglib2.0-0

# Verify installations
echo "✅ Verifying installations..."

# Check Tesseract
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract installed: $(tesseract --version | head -1)"
else
    echo "❌ Tesseract installation failed"
fi

# Check Python packages
echo "📋 Python packages:"
pip list | grep -E "(discord|pytesseract|pillow|requests)" || echo "⚠️ Some packages may be missing"

echo "🎉 Build completed successfully!"
echo "Bot will start with: python bot.py"