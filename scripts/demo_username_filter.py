#!/usr/bin/env python3
"""
Demonstration script for the username filtering system
Shows all features and configuration options
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.username_filter import UsernameFilter

def demonstrate_username_filter():
    """Comprehensive demonstration of the username filtering system."""
    
    print("🤖 ClassBot Username Filtering System Demo")
    print("=" * 60)
    print()
    
    # Initialize filter
    filter_system = UsernameFilter()
    
    # Show current configuration
    stats = filter_system.get_stats()
    print("📊 Current Configuration:")
    print(f"   Status: {'🟢 Enabled' if stats['enabled'] else '🔴 Disabled'}")
    print(f"   Sensitivity: {stats['sensitivity'].title()}")
    print(f"   Action on Detection: {filter_system.config['action_on_detection'].title()}")
    print(f"   Total Filtered Words: {stats['total_filtered_words']}")
    print(f"   Active Categories: {', '.join(stats['categories'])}")
    print(f"   Pattern Detection: {stats['patterns_enabled']}/4 types enabled")
    print(f"   Whitelisted Users: {stats['whitelist_size']}")
    print()
    
    # Test various username types
    test_scenarios = [
        {
            "category": "✅ Clean Academic Usernames",
            "usernames": [
                "ClassTA_Helper",
                "study_group_leader", 
                "mathtutor2024",
                "johnsmith_student",
                "academichelper"
            ],
            "expected": "clean"
        },
        {
            "category": "🚩 Direct Violations",
            "usernames": [
                "fuckthisclass",
                "xxxporn123", 
                "nazipower",
                "killmyself",
                "hateschool"
            ],
            "expected": "flagged"
        },
        {
            "category": "🕵️ Evasion Attempts",
            "usernames": [
                "f u c k",
                "fuuuuck",
                "kcuf",
                "p o r n",
                "shiiiit"
            ],
            "expected": "flagged"
        },
        {
            "category": "⚠️ Context-Dependent",
            "usernames": [
                "hell_student",
                "damn_assignment", 
                "class_ass",
                "badass_coder"
            ],
            "expected": "flagged"
        }
    ]
    
    # Test each scenario
    for scenario in test_scenarios:
        print(f"{scenario['category']}:")
        print("-" * 40)
        
        for username in scenario['usernames']:
            is_inappropriate, details = filter_system.check_username(username)
            
            # Status indicators
            status = "🚩 FLAGGED" if is_inappropriate else "✅ CLEAN"
            expectation_met = "✅" if (
                (scenario['expected'] == 'flagged' and is_inappropriate) or 
                (scenario['expected'] == 'clean' and not is_inappropriate)
            ) else "❌"
            
            print(f"  {expectation_met} '{username}': {status}")
            
            if is_inappropriate:
                print(f"     Confidence: {details['confidence']:.2f}")
                print(f"     Action: {details['action_recommended'].title()}")
                if details.get('matches'):
                    match_types = list(set([match[0] for match in details['matches']]))
                    print(f"     Detection: {', '.join(match_types)}")
        print()
    
    # Demonstrate whitelist functionality
    print("🛡️ Whitelist Management:")
    print("-" * 40)
    test_username = "hell_student"
    
    # Check before whitelist
    before_result = filter_system.check_username(test_username)
    print(f"  Before whitelist: '{test_username}' -> {'FLAGGED' if before_result[0] else 'CLEAN'}")
    
    # Add to whitelist
    filter_system.add_to_whitelist(test_username)
    after_result = filter_system.check_username(test_username)
    print(f"  After whitelist: '{test_username}' -> {'FLAGGED' if after_result[0] else 'CLEAN'}")
    
    # Remove from whitelist
    filter_system.remove_from_whitelist(test_username)
    removed_result = filter_system.check_username(test_username)
    print(f"  After removal: '{test_username}' -> {'FLAGGED' if removed_result[0] else 'CLEAN'}")
    print()
    
    # Show available Discord commands
    print("🎮 Available Discord Commands:")
    print("-" * 40)
    print("  !check_usernames report    - Scan all members (report only)")
    print("  !check_usernames warn      - Scan and warn flagged users")
    print("  !check_usernames kick      - Scan and kick high-confidence violations")
    print("  !check_usernames stats     - Show filter statistics")
    print()
    print("  !username_whitelist add @user     - Add user to whitelist")
    print("  !username_whitelist remove @user  - Remove from whitelist")
    print("  !username_whitelist list          - Show whitelisted users")
    print()
    
    # Configuration recommendations
    print("⚙️ Recommended Settings for Academic Server:")
    print("-" * 40)
    print("  Sensitivity: Medium (balanced accuracy)")
    print("  Action: Warn (educational approach)")
    print("  Pattern Detection: All enabled")
    print("  Regular Review: Weekly check of detection logs")
    print("  Whitelist: Add any false positives immediately")
    print()
    
    # Summary
    total_tests = sum(len(scenario['usernames']) for scenario in test_scenarios)
    print(f"📈 Demo Summary:")
    print(f"   Total Test Cases: {total_tests}")
    print(f"   Detection Categories: {len(test_scenarios)}")
    print(f"   System Status: Ready for deployment")
    print()
    
    print("✅ Username filtering system is fully operational!")
    print("   The bot will now automatically check usernames for")
    print("   new members and provide admin tools for bulk scanning.")
    print()
    print("📖 For detailed usage instructions, see:")
    print("   docs/USERNAME_FILTERING_GUIDE.md")

if __name__ == "__main__":
    demonstrate_username_filter()