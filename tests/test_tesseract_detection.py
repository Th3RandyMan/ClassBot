"""
Quick test to see if our bot can auto-detect Tesseract
"""
import os
import platform
import pytesseract

def test_tesseract_detection():
    """Test if the bot's Tesseract auto-detection works"""
    
    print("🔍 Testing bot's Tesseract auto-detection...")
    
    system = platform.system().lower()
    
    if system == "linux":
        # Cloud deployment (Render, Heroku, etc.)
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        print("Configured Tesseract for Linux cloud deployment")
    elif system == "windows":
        # Local Windows development
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            'tesseract'  # If in PATH
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Configured Tesseract for Windows: {path}")
                break
            elif path == 'tesseract':
                try:
                    # Test if tesseract command works
                    version = pytesseract.get_tesseract_version()
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"✅ Configured Tesseract for Windows: {path} (in PATH)")
                    break
                except:
                    continue
        else:
            print("❌ Tesseract not found on Windows. Image detection will be disabled.")
            return False
    else:
        print(f"Unknown system: {system}. Using default Tesseract configuration.")
    
    # Test if it works
    try:
        version = pytesseract.get_tesseract_version()
        print(f"🎉 Tesseract working! Version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        return False

if __name__ == "__main__":
    test_tesseract_detection()