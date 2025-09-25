#!/usr/bin/env python3
"""
Test script for bot status functionality including OCR status.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot.bot_controller import BotController
import json
from datetime import datetime, timedelta

def test_bot_status():
    """Test the bot status functionality."""
    print("=" * 60)
    print("🤖 TESTING BOT STATUS WITH OCR INTEGRATION")
    print("=" * 60)
    
    try:
        # Initialize bot controller
        controller = BotController()
        
        # Get full status
        status = controller.get_status()
        
        print("\n📊 Complete Bot Status:")
        print("-" * 30)
        
        # Bot state
        if status["enabled"]:
            print("🟢 Bot Status: ONLINE")
            print("✅ All Commands: Available")
            print("🔍 Monitoring: Active")
        else:
            print("🔴 Bot Status: DISABLED")
            if status["maintenance_mode"]:
                print("🔧 Mode: Maintenance")
            else:
                print("⏸️ Mode: Temporarily Disabled")
            
            if status["disabled_reason"]:
                print(f"📝 Reason: {status['disabled_reason']}")
            
            if status["disabled_by"]:
                print(f"👤 Disabled By: {status['disabled_by']}")
            
            if status.get("remaining_minutes") and status["remaining_minutes"] > 0:
                print(f"⏱️ Re-enabled In: {status['remaining_minutes']} minutes")
        
        # OCR Status
        if "ocr" in status:
            print(f"\n🖼️ OCR System Status:")
            print("-" * 20)
            ocr_data = status["ocr"]
            print(f"Status: {ocr_data['status']}")
            print(f"Available: {ocr_data['available']}")
            print(f"Version: {ocr_data['version']}")
            
            # Format for Discord-like display
            ocr_field_value = ocr_data["status"]
            if ocr_data["available"] and ocr_data["version"] != "Unknown" and "version check failed" not in ocr_data["version"]:
                ocr_field_value += f" (v{ocr_data['version']})"
            elif not ocr_data["available"]:
                ocr_field_value += "\nImage detection disabled"
            
            print(f"Discord Display: {ocr_field_value}")
        
        # System info
        print(f"\n🔧 System Information:")
        print("-" * 20)
        print("Bot Version: ClassBot v2.0")
        current_time = datetime.now()
        uptime_start = current_time - timedelta(hours=1)  # Simulated uptime
        print(f"Simulated Uptime: Started {uptime_start.strftime('%H:%M:%S')}")
        
        print("\n" + "=" * 60)
        print("✅ BOT STATUS TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during bot status test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ocr_standalone():
    """Test OCR functionality separately."""
    print("\n🖼️ TESTING OCR SYSTEM SEPARATELY")
    print("-" * 40)
    
    try:
        controller = BotController()
        ocr_status = controller.get_ocr_status()
        
        print("OCR Test Results:")
        for key, value in ocr_status.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Bot Status Tests...\n")
    
    # Test individual components
    ocr_success = test_ocr_standalone()
    status_success = test_bot_status()
    
    print(f"\n📋 Test Summary:")
    print(f"OCR Test: {'✅ PASS' if ocr_success else '❌ FAIL'}")
    print(f"Bot Status Test: {'✅ PASS' if status_success else '❌ FAIL'}")
    
    if ocr_success and status_success:
        print(f"\n🎉 ALL TESTS PASSED - Ready for Discord!")
    else:
        print(f"\n⚠️ Some tests failed - check the errors above")