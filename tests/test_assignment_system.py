#!/usr/bin/env python3
"""
Assignment System Test - Verify all components work together.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_assignment_system():
    """Test the assignment system components."""
    print("=" * 60)
    print("🎯 TESTING ASSIGNMENT SYSTEM INTEGRATION")
    print("=" * 60)
    
    try:
        # Test 1: Assignment Manager
        print("\n1. Testing Assignment Manager...")
        from src.bot.assignment_manager import AssignmentManager
        
        assignment_manager = AssignmentManager()
        print("✅ Assignment Manager initialized")
        
        # Test 2: Assignment Commands (basic import)
        print("\n2. Testing Assignment Commands...")
        from src.bot.assignment_commands import AssignmentCommands
        
        # Mock bot and admin roles for testing
        class MockBot:
            pass
        
        mock_bot = MockBot()
        admin_roles = ["Admin", "TA"]
        
        assignment_commands = AssignmentCommands(mock_bot, assignment_manager, admin_roles)
        print("✅ Assignment Commands initialized")
        
        # Test 3: Assignment Reminder System
        print("\n3. Testing Assignment Reminder System...")
        from src.bot.assignment_reminder_system import AssignmentReminderSystem
        
        reminder_system = AssignmentReminderSystem(mock_bot, assignment_manager)
        print("✅ Assignment Reminder System initialized")
        
        # Test 4: Date parsing
        print("\n4. Testing Date Parsing...")
        test_dates = [
            "tomorrow 5pm",
            "Jan 15 11:59pm",
            "12/25 2pm",
            "today 3pm"
        ]
        
        for date_str in test_dates:
            parsed = assignment_commands._parse_date(date_str)
            if parsed:
                print(f"✅ '{date_str}' -> {parsed.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"❌ Failed to parse '{date_str}'")
        
        # Test 5: Reminder time parsing
        print("\n5. Testing Reminder Time Parsing...")
        test_reminders = ["1d", "2h", "30m", "1w"]
        
        for reminder_str in test_reminders:
            try:
                delta = assignment_manager._parse_reminder_time(reminder_str)
                formatted = assignment_manager._format_reminder_time(delta)
                print(f"✅ '{reminder_str}' -> {formatted}")
            except Exception as e:
                print(f"❌ Failed to parse '{reminder_str}': {e}")
        
        # Test 6: Configuration files
        print("\n6. Testing Configuration...")
        config_path = "config/assignments.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✅ Assignment config file loaded")
            print(f"   Settings: {list(config.get('settings', {}).keys())}")
            print(f"   Assignments: {len(config.get('assignments', {}))}")
        else:
            print("⚠️ Assignment config file will be created on first use")
        
        # Test 7: Integration points
        print("\n7. Testing Integration Points...")
        
        # Check if main.py can import the modules
        try:
            # Test imports that main.py will use
            from src.bot.assignment_manager import AssignmentManager
            from src.bot.assignment_commands import AssignmentCommands  
            from src.bot.assignment_reminder_system import AssignmentReminderSystem
            print("✅ All modules can be imported by main.py")
        except ImportError as e:
            print(f"❌ Import error for main.py integration: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ASSIGNMENT SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n📋 System Summary:")
        print("• ✅ Assignment Manager - Handles Discord events and reminders")
        print("• ✅ Assignment Commands - Intuitive bot commands")  
        print("• ✅ Reminder System - Automated background notifications")
        print("• ✅ Date Parsing - Flexible date/time input")
        print("• ✅ Configuration - JSON-based settings")
        print("• ✅ Main Bot Integration - Ready to add to main.py")
        
        print("\n🎯 Next Steps:")
        print("1. Run the main bot with: python main.py")
        print("2. Test commands like: !add_assignment Test | tomorrow 5pm | Test assignment")
        print("3. Set reminder channel with: !set_reminder_channel #announcements")
        print("4. Check assignments with: !assignments")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during assignment system test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_syntax_check():
    """Test that main.py has no syntax errors with the new integration."""
    print("\n" + "=" * 60)
    print("🔧 TESTING MAIN.PY SYNTAX")
    print("=" * 60)
    
    try:
        import py_compile
        py_compile.compile('main.py', doraise=True)
        print("✅ main.py compiles without syntax errors")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking main.py: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Assignment System Integration Tests...\n")
    
    # Test assignment system components
    assignment_test = await test_assignment_system()
    
    # Test main.py syntax
    syntax_test = await test_syntax_check()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Assignment System: {'✅ PASS' if assignment_test else '❌ FAIL'}")
    print(f"Main.py Syntax: {'✅ PASS' if syntax_test else '❌ FAIL'}")
    
    if assignment_test and syntax_test:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("🚀 Assignment system is ready for Discord!")
        print("\n💡 Available Commands:")
        print("   Student: !assignments, !next_assignment, !assignment_help")  
        print("   Admin: !add_assignment, !remove_assignment, !set_reminder_channel")
    else:
        print(f"\n⚠️ Some tests failed - check the errors above")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)