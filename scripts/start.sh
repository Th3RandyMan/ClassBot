#!/bin/bash

# Startup script for cloud deployment
echo "🚀 Starting Class Bot..."
echo "Environment: $(uname -a)"

# Check if Tesseract is installed
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR is installed: $(tesseract --version | head -1)"
else
    echo "⚠️  Tesseract OCR not found - image detection will be disabled"
fi

# Check Python environment
echo "🐍 Python version: $(python --version)"
echo "📦 Installed packages:"
pip list | grep -E "(discord|pytesseract|pillow|opencv)" || echo "No relevant packages found"

# Start the bot
echo "🤖 Starting Discord bot..."
python bot.py