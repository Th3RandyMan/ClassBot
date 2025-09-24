"""
Test script to check if Tesseract OCR is installed and working
"""
import subprocess
import sys

def test_tesseract_installation():
    """Test if Tesseract is installed and accessible"""
    print("🔍 Testing Tesseract OCR Installation...")
    print("=" * 50)
    
    try:
        # Try to run tesseract --version
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Tesseract is installed and accessible!")
            print(f"Version info:\n{result.stdout}")
            return True
        else:
            print("❌ Tesseract command failed")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Tesseract not found in PATH")
        print("\n📝 To install Tesseract on Windows:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install the executable")
        print("3. Add to PATH or specify path in bot code")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Tesseract command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Tesseract: {e}")
        return False

def test_python_tesseract():
    """Test if pytesseract Python package works"""
    print("\n🐍 Testing Python Tesseract Package...")
    print("=" * 50)
    
    try:
        import pytesseract
        from PIL import Image
        import io
        import numpy as np
        
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple white image with black text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a default font
            draw.text((10, 10), "Hello World", fill='black')
        except:
            # If font fails, still create the image
            draw.text((10, 10), "Hello World", fill='black')
        
        # Test OCR
        text = pytesseract.image_to_string(img)
        print(f"✅ pytesseract is working!")
        print(f"Extracted text: '{text.strip()}'")
        
        return True
        
    except ImportError as e:
        print(f"❌ pytesseract not installed: {e}")
        print("Install with: pip install pytesseract")
        return False
    except Exception as e:
        print(f"❌ Error with pytesseract: {e}")
        return False

def main():
    print("🤖 Discord Bot - Tesseract OCR Test")
    print("=" * 50)
    
    tesseract_ok = test_tesseract_installation()
    python_ok = test_python_tesseract()
    
    print("\n📊 Summary:")
    print("=" * 50)
    
    if tesseract_ok and python_ok:
        print("✅ OCR is fully configured and ready!")
        print("Your Discord bot can detect code in images.")
    elif tesseract_ok:
        print("⚠️  Tesseract installed, but Python package needs setup")
        print("Run: pip install pytesseract")
    elif python_ok:
        print("⚠️  Python package installed, but Tesseract binary needed")
        print("Install Tesseract from the link above")
    else:
        print("❌ OCR not configured")
        print("The bot will work for text detection only (no image detection)")
        
    print("\n💡 Note: The bot will work without OCR, just without image detection!")

if __name__ == "__main__":
    main()