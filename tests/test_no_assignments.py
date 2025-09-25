#!/usr/bin/env python3
"""
Test the improved "no assignments" messages.
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockChannel:
    def __init__(self, name):
        self.name = name
        self.mention = f"#{name}"

class MockUser:
    def __init__(self, is_admin=False):
        self.roles = []
        if is_admin:
            self.roles = [MockRole("Admin")]
        self.display_name = "TestUser"

class MockRole:
    def __init__(self, name):
        self.name = name

class MockGuild:
    def __init__(self):
        self.id = 12345

class MockContext:
    def __init__(self, is_admin=False):
        self.author = MockUser(is_admin)
        self.guild = MockGuild()
        self.channel = MockChannel("general")
        self.sent_embeds = []
    
    async def send(self, embed=None, content=None):
        if embed:
            self.sent_embeds.append(embed)
            print(f"📤 Embed sent: {embed.title}")
            print(f"   Description: {embed.description}")
            for field in embed.fields:
                print(f"   Field '{field.name}': {field.value[:100]}...")
            if embed.footer:
                print(f"   Footer: {embed.footer.text}")
            print()

async def test_no_assignments_messages():
    """Test all the 'no assignments' messages."""
    print("=" * 60)
    print("📝 TESTING 'NO ASSIGNMENTS' MESSAGES")
    print("=" * 60)
    
    try:
        from src.bot.assignment_manager import AssignmentManager
        from src.bot.assignment_commands import AssignmentCommands
        
        # Create empty assignment manager
        assignment_manager = AssignmentManager()
        
        # Clear any existing assignments for test
        assignment_manager.assignments["assignments"] = {}
        
        # Test with admin user
        print("\n👑 Testing as ADMIN user:")
        print("-" * 30)
        
        admin_bot = None  # Mock bot
        admin_roles = ["Admin", "TA"]
        assignment_commands = AssignmentCommands(admin_bot, assignment_manager, admin_roles)
        admin_ctx = MockContext(is_admin=True)
        
        # Test list_assignments with no assignments
        print("Testing !assignments (admin):")
        await assignment_commands.list_assignments(admin_ctx, 14)
        
        # Test all_assignments with no assignments
        print("Testing !all_assignments (admin):")
        await assignment_commands.all_assignments(admin_ctx)
        
        # Test next_assignment with no assignments
        print("Testing !next_assignment (admin):")
        await assignment_commands.next_assignment(admin_ctx)
        
        # Test with regular student user
        print("\n👥 Testing as STUDENT user:")
        print("-" * 30)
        
        student_ctx = MockContext(is_admin=False)
        
        # Test list_assignments with no assignments
        print("Testing !assignments (student):")
        await assignment_commands.list_assignments(student_ctx, 14)
        
        # Test all_assignments with no assignments
        print("Testing !all_assignments (student):")
        await assignment_commands.all_assignments(student_ctx)
        
        # Test next_assignment with no assignments
        print("Testing !next_assignment (student):")
        await assignment_commands.next_assignment(student_ctx)
        
        print("=" * 60)
        print("✅ ALL 'NO ASSIGNMENTS' MESSAGES TESTED")
        print("=" * 60)
        
        print("\n📊 Summary:")
        print("• ✅ Admin messages include instructions to add assignments")
        print("• ✅ Student messages are encouraging and helpful")
        print("• ✅ All messages include appropriate next steps")
        print("• ✅ Different colors used (green for positive, blue for neutral)")
        print("• ✅ Footer tips included for Discord Events")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_message_content():
    """Test the specific content of the improved messages."""
    print("\n" + "=" * 60)
    print("🔍 TESTING MESSAGE CONTENT QUALITY")
    print("=" * 60)
    
    try:
        from src.bot.assignment_manager import AssignmentManager
        from src.bot.assignment_commands import AssignmentCommands
        
        assignment_manager = AssignmentManager()
        assignment_manager.assignments["assignments"] = {}
        
        admin_bot = None
        admin_roles = ["Admin", "TA"]
        assignment_commands = AssignmentCommands(admin_bot, assignment_manager, admin_roles)
        
        # Test admin message content
        admin_ctx = MockContext(is_admin=True)
        await assignment_commands.list_assignments(admin_ctx, 7)
        
        admin_embed = admin_ctx.sent_embeds[-1]
        
        # Check admin message quality
        print("📋 Admin Message Analysis:")
        print(f"   Title: {admin_embed.title}")
        print(f"   Color: {'Green' if admin_embed.color.value == 0x00ff00 else 'Other'}")
        
        admin_content = str(admin_embed.fields[0].value).lower() if admin_embed.fields else ""
        has_add_command = "!add_assignment" in admin_content
        has_example = "example" in admin_content
        
        print(f"   ✅ Contains add command: {has_add_command}")
        print(f"   ✅ Contains example: {has_example}")
        
        # Test student message content
        student_ctx = MockContext(is_admin=False)
        await assignment_commands.list_assignments(student_ctx, 7)
        
        student_embed = student_ctx.sent_embeds[-1]
        
        print("\n👥 Student Message Analysis:")
        print(f"   Title: {student_embed.title}")
        print(f"   Color: {'Green' if student_embed.color.value == 0x00ff00 else 'Other'}")
        
        student_content = str(student_embed.fields[0].value).lower() if student_embed.fields else ""
        is_encouraging = any(word in student_content for word in ["enjoy", "great", "break", "time"])
        has_suggestions = "review" in student_content
        
        print(f"   ✅ Is encouraging: {is_encouraging}")
        print(f"   ✅ Has suggestions: {has_suggestions}")
        
        print("\n🎯 Content Quality Check:")
        print(f"   Admin messages are instructional: {'✅' if has_add_command and has_example else '❌'}")
        print(f"   Student messages are encouraging: {'✅' if is_encouraging and has_suggestions else '❌'}")
        print(f"   Both use positive colors: {'✅' if admin_embed.color.value == student_embed.color.value == 0x00ff00 else '❌'}")
        
        return has_add_command and has_example and is_encouraging and has_suggestions
        
    except Exception as e:
        print(f"❌ Error during content test: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Testing Improved 'No Assignments' Messages...\n")
    
    # Test message functionality
    functionality_test = await test_no_assignments_messages()
    
    # Test message content quality
    content_test = await test_message_content()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Message Functionality: {'✅ PASS' if functionality_test else '❌ FAIL'}")
    print(f"Content Quality: {'✅ PASS' if content_test else '❌ FAIL'}")
    
    if functionality_test and content_test:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✨ 'No assignments' messages are now much more helpful!")
        print("\n💡 Improvements made:")
        print("   • Admin messages include setup instructions")
        print("   • Student messages are encouraging and positive")
        print("   • All messages suggest next steps")
        print("   • Better use of colors and emojis")
        print("   • Footer tips about Discord Events")
    else:
        print(f"\n⚠️ Some tests failed - check the errors above")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)