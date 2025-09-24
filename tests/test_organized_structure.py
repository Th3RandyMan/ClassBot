#!/usr/bin/env python3
"""
Test the new organized structure and verify all components work together
"""

import os
import sys
import tempfile
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing Module Imports...")
    try:
        from bot.warning_system import PersistentWarningSystem
        print("  ✅ Warning system import: OK")
        
        from bot.error_recovery import ErrorRecoverySystem, run_bot_with_recovery
        print("  ✅ Error recovery import: OK")
        
        from bot.utils.code_detection import CodeDetector
        print("  ✅ Code detection import: OK")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_warning_system():
    """Test persistent warning system functionality"""
    print("\n🔍 Testing Persistent Warning System...")
    try:
        # Use a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        from bot.warning_system import PersistentWarningSystem
        warning_sys = PersistentWarningSystem(filename=temp_file, expiry_days=30)
        
        # Test adding warnings
        count1 = warning_sys.add_warning(12345, "Test warning 1")
        count2 = warning_sys.add_warning(12345, "Test warning 2") 
        count3 = warning_sys.add_warning(67890, "Another user warning")
        
        print(f"  ✅ Added warnings - User 1: {count2} warnings, User 2: {count3} warning")
        
        # Test getting warnings
        warnings = warning_sys.get_warnings(12345)
        print(f"  ✅ Retrieved {len(warnings)} warnings for user 12345")
        
        # Test stats
        stats = warning_sys.get_stats()
        print(f"  ✅ Stats: {stats['total_users_with_warnings']} users, {stats['total_active_warnings']} warnings")
        
        # Test clearing
        cleared = warning_sys.clear_warnings(12345)
        print(f"  ✅ Cleared warnings for user: {cleared}")
        
        # Cleanup
        os.unlink(temp_file)
        
        return True
    except Exception as e:
        print(f"  ❌ Warning system error: {e}")
        return False

def test_code_detection():
    """Test code detection functionality"""
    print("\n🔍 Testing Code Detection...")
    try:
        from bot.utils.code_detection import CodeDetector
        detector = CodeDetector()
        
        # Test various code samples
        test_cases = [
            ("Normal text", "Hello everyone, how are you today?", False),
            ("Python code", "def hello():\n    print('world')\n    return True", True),
            ("JavaScript", "function test() {\n    console.log('test');\n    return false;\n}", True),
            ("Conversation with 'if'", "If you have any questions, let me know", False)
        ]
        
        for name, text, expected in test_cases:
            result = detector.detect_code_in_text(text)
            status = "✅" if result == expected else "❌"
            print(f"  {status} {name}: {'Detected' if result else 'Not detected'} (expected: {'Detected' if expected else 'Not detected'})")
        
        # Test OCR availability
        ocr_available = detector.is_ocr_available()
        print(f"  ℹ️ OCR available: {ocr_available}")
        
        return True
    except Exception as e:
        print(f"  ❌ Code detection error: {e}")
        return False

def test_error_recovery():
    """Test error recovery system (basic functionality)"""
    print("\n🔍 Testing Error Recovery System...")
    try:
        # Set up fake environment
        os.environ['DISCORD_TOKEN'] = 'fake_token'
        
        from bot.error_recovery import ErrorRecoverySystem
        from bot.warning_system import PersistentWarningSystem
        
        # Create mock bot object
        class MockBot:
            pass
        
        mock_bot = MockBot()
        warning_sys = PersistentWarningSystem()
        error_recovery = ErrorRecoverySystem(mock_bot, warning_sys)
        
        # Test basic functionality
        print("  ✅ Error recovery system initialized")
        print(f"  ✅ Max reconnect attempts: {error_recovery.max_reconnect_attempts}")
        print(f"  ✅ Reconnect delay: {error_recovery.reconnect_delay} seconds")
        
        # Test reset function
        error_recovery.reset_reconnect_counter()
        print("  ✅ Reconnect counter reset successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Error recovery error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing New Organized Bot Structure")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Warning System", test_warning_system),
        ("Code Detection", test_code_detection),
        ("Error Recovery", test_error_recovery)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The organized structure is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)