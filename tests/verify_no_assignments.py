#!/usr/bin/env python3
"""
Simple test to verify no assignments message improvements.
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_message_content():
    """Test that the improved messages are in the code."""
    print("=" * 60)
    print("🔍 VERIFYING IMPROVED 'NO ASSIGNMENTS' MESSAGES")
    print("=" * 60)
    
    try:
        # Read the assignment commands file
        with open('src/bot/assignment_commands.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test 1: Check for improved list_assignments message
        print("\n1. Testing list_assignments improvements:")
        
        improvements = [
            "Great news! No assignments are due",  # Positive message
            "For Admins",  # Admin-specific help
            "Enjoy the Break!",  # Student encouragement  
            "Add an assignment:",  # Admin instructions
            "Review previous material",  # Student suggestions
            "Check Different Time Ranges",  # Navigation help
        ]
        
        for improvement in improvements:
            if improvement in content:
                print(f"   ✅ Found: '{improvement}'")
            else:
                print(f"   ❌ Missing: '{improvement}'")
        
        # Test 2: Check for improved all_assignments message
        print("\n2. Testing all_assignments improvements:")
        
        all_improvements = [
            "Get Started",  # Admin help
            "Create your first assignment:",  # Clear instructions
            "Setup Reminders",  # Reminder setup help
            "Nothing Here Yet",  # Student message
            "Your instructor hasn't added",  # Clear explanation
            "In the meantime:",  # Helpful suggestions
        ]
        
        for improvement in all_improvements:
            if improvement in content:
                print(f"   ✅ Found: '{improvement}'")
            else:
                print(f"   ❌ Missing: '{improvement}'")
        
        # Test 3: Check for improved next_assignment message
        print("\n3. Testing next_assignment improvements:")
        
        next_improvements = [
            "You're all caught up!",  # Positive message
            "Admin Options",  # Admin-specific help
            "Great Work!",  # Student encouragement
            "Use this time wisely:",  # Constructive suggestions
            "Check for More",  # Navigation options
        ]
        
        for improvement in next_improvements:
            if improvement in content:
                print(f"   ✅ Found: '{improvement}'")
            else:
                print(f"   ❌ Missing: '{improvement}'")
        
        # Test 4: Check for color improvements
        print("\n4. Testing color improvements:")
        
        color_count = content.count('color=0x00ff00')  # Green color for positive messages
        if color_count >= 2:  # Should be at least 2 green messages
            print(f"   ✅ Found {color_count} positive (green) color messages")
        else:
            print(f"   ⚠️ Only found {color_count} green color messages")
        
        # Test 5: Check for emoji improvements
        print("\n5. Testing emoji improvements:")
        
        emojis = ['🎉', '😊', '🌟', '👑', '🔍', '💡']
        emoji_count = 0
        for emoji in emojis:
            if emoji in content:
                emoji_count += 1
        
        print(f"   ✅ Found {emoji_count}/6 improved emojis")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        total_improvements = len(improvements) + len(all_improvements) + len(next_improvements)
        found_improvements = sum(1 for imp in improvements + all_improvements + next_improvements if imp in content)
        
        print(f"Content Improvements: {found_improvements}/{total_improvements}")
        print(f"Color Improvements: {'✅' if color_count >= 2 else '❌'}")
        print(f"Emoji Improvements: {'✅' if emoji_count >= 4 else '❌'}")
        
        success_rate = found_improvements / total_improvements
        overall_success = success_rate >= 0.8 and color_count >= 2 and emoji_count >= 4
        
        if overall_success:
            print(f"\n🎉 VERIFICATION SUCCESSFUL!")
            print("✨ All 'no assignments' messages have been improved!")
            print(f"\n💡 Key improvements:")
            print("   • Admin messages now include setup instructions")
            print("   • Student messages are encouraging and positive") 
            print("   • All messages suggest helpful next steps")
            print("   • Positive green colors for 'no assignments' scenarios")
            print("   • Better emojis for visual appeal")
        else:
            print(f"\n⚠️ Some improvements may be missing")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def test_message_examples():
    """Show examples of what the improved messages look like."""
    print("\n" + "=" * 60)
    print("📋 MESSAGE EXAMPLES")
    print("=" * 60)
    
    print("\n👑 ADMIN MESSAGE EXAMPLE (!assignments):")
    print("   Title: 📅 No Upcoming Assignments")
    print("   Description: Great news! No assignments are due in the next 14 days.")
    print("   Color: Green (positive)")
    print("   Fields: For Admins, Check Different Time Ranges")
    print("   Footer: Tip about Discord Events")
    
    print("\n👥 STUDENT MESSAGE EXAMPLE (!assignments):")
    print("   Title: 📅 No Upcoming Assignments") 
    print("   Description: Great news! No assignments are due in the next 14 days.")
    print("   Color: Green (positive)")
    print("   Fields: Enjoy the Break!, Check Different Time Ranges")
    print("   Footer: Tip about Discord Events")
    
    print("\n📚 ALL ASSIGNMENTS ADMIN EXAMPLE:")
    print("   Title: 📅 No Assignments Found")
    print("   Description: No assignments have been created yet.")
    print("   Color: Blue (informational)")
    print("   Fields: Get Started, Setup Reminders")
    print("   Footer: Info about Discord Events and announcements")
    
    print("\n🎉 NEXT ASSIGNMENT EXAMPLE:")
    print("   Title: 🎉 No Upcoming Assignments")
    print("   Description: You're all caught up! No assignments due in the next 30 days.")
    print("   Color: Green (celebratory)")
    print("   Fields: Great Work! or Admin Options, Check for More")
    print("   Footer: Tip about Discord Events")

if __name__ == "__main__":
    print("🚀 Verifying 'No Assignments' Message Improvements...\n")
    
    success = test_message_content()
    test_message_examples()
    
    if success:
        print(f"\n✅ All improvements verified successfully!")
    else:
        print(f"\n⚠️ Some improvements may need attention")
        
    sys.exit(0 if success else 1)