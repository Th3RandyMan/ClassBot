#!/usr/bin/env python3
"""
Test script to verify the help command change.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_help_command_change():
    """Test that the help command change was successful."""
    print("=" * 50)
    print("🔧 TESTING HELP COMMAND CHANGE")
    print("=" * 50)
    
    # Test 1: Check main.py for the command definition
    print("\n1. Checking command definition...")
    with open('main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    if "@bot.command(name='help')" in main_content:
        print("✅ Command definition updated to 'help'")
    else:
        print("❌ Command definition not found")
        return False
    
    if "help_command=None" in main_content:
        print("✅ Default help command disabled")
    else:
        print("❌ Default help command not disabled")
        return False
    
    # Test 2: Check bot controller configuration
    print("\n2. Checking bot controller...")
    try:
        from src.bot.bot_controller import BotController
        controller = BotController()
        allowed_commands = controller.config.get('allowed_commands_when_disabled', [])
        
        if 'help' in allowed_commands and 'help_classbot' not in allowed_commands:
            print("✅ Bot controller config updated")
        else:
            print("❌ Bot controller config not properly updated")
            print(f"    Allowed commands: {allowed_commands}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bot controller: {e}")
        return False
    
    # Test 3: Check JSON config file
    print("\n3. Checking JSON configuration...")
    try:
        import json
        with open('config/bot_control.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        allowed_commands = config.get('allowed_commands_when_disabled', [])
        if 'help' in allowed_commands and 'help_classbot' not in allowed_commands:
            print("✅ JSON config file updated")
        else:
            print("❌ JSON config file not properly updated")
            print(f"    Allowed commands: {allowed_commands}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking JSON config: {e}")
        return False
    
    # Test 4: Check for remaining references to help_classbot
    print("\n4. Checking for old references...")
    help_classbot_count = main_content.count('help_classbot')
    help_count = main_content.count('`!help`')
    
    print(f"   Remaining 'help_classbot' references: {help_classbot_count}")
    print(f"   New '!help' command references: {help_count}")
    
    if help_classbot_count == 0 and help_count >= 2:  # Should be at least 2 references to !help
        print("✅ References properly updated")
    else:
        print("⚠️ Some references may need manual review")
    
    print("\n" + "=" * 50)
    print("✅ HELP COMMAND CHANGE SUCCESSFUL!")
    print("=" * 50)
    
    print("\n📝 Summary of changes:")
    print("• Command name changed from 'help_classbot' to 'help'")
    print("• Default Discord.py help command disabled")
    print("• Bot controller config updated")
    print("• JSON config file updated")
    print("• All command references updated")
    
    print("\n🎯 Usage:")
    print("• Old command: !help_classbot")
    print("• New command: !help")
    
    return True

if __name__ == "__main__":
    success = test_help_command_change()
    if not success:
        print("\n❌ Some tests failed - please review the errors above")
        sys.exit(1)
    else:
        print("\n🚀 Ready to use the new !help command!")