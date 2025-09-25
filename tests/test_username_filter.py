#!/usr/bin/env python3
"""
Test script for username filter functionality
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.username_filter import UsernameFilter

def test_comprehensive_username_filter():
    """Comprehensive test of the username filter with various test cases."""
    filter_system = UsernameFilter()
    
    # Test cases: (username, expected_result, description)
    test_cases = [
        # Clean usernames - should pass
        ("normaluser123", False, "Normal username"),
        ("ClassTA_Helper", False, "Academic helper"),
        ("study_group_leader", False, "Study group leader"),
        ("johnsmith2024", False, "Regular name with year"),
        ("mathtutor", False, "Academic tutor"),
        
        # Inappropriate usernames - should be flagged
        ("fuckthisclass", True, "Direct profanity"),
        ("ihateschool", True, "Hate speech context"),
        ("killmyself", True, "Self-harm reference"),
        ("xxxporn123", True, "Explicit content"),
        ("nazipower", True, "Hate symbol"),
        
        # Character replacement evasion - should be flagged
        ("f*ckthis", True, "Asterisk replacement"),
        ("f@ckthis", True, "@ replacement"),
        ("fück", True, "Unicode evasion"),
        ("n1gg3r", True, "L33t speak evasion"),
        ("b1tch", True, "Numeric replacement"),
        
        # Spacing evasion - should be flagged
        ("f u c k", True, "Spaced letters"),
        ("p o r n", True, "Spaced inappropriate word"),
        
        # Repeated characters - should be flagged
        ("fuuuuck", True, "Repeated characters"),
        ("shiiiit", True, "Extended letters"),
        
        # Backwards words - should be flagged
        ("kcuf", True, "Backwards profanity"),
        ("ttihs", True, "Backwards word"),
        
        # Edge cases - context dependent
        ("hell_student", True, "Contains filtered word"),
        ("damn_assignment", True, "Profanity in context"),
        ("class_ass", True, "Inappropriate in username"),
        
        # Should NOT be flagged (common words in appropriate context)
        # Note: These depend on sensitivity settings
    ]
    
    print("🧪 Comprehensive Username Filter Test Results")
    print("=" * 60)
    print()
    
    total_tests = len(test_cases)
    correct_predictions = 0
    
    for username, expected_inappropriate, description in test_cases:
        is_inappropriate, details = filter_system.check_username(username)
        
        # Check if prediction matches expectation
        is_correct = is_inappropriate == expected_inappropriate
        correct_predictions += 1 if is_correct else 0
        
        # Status emoji
        status = "✅" if is_correct else "❌"
        flag_status = "🚩 FLAGGED" if is_inappropriate else "✅ CLEAN"
        
        print(f"{status} '{username}': {flag_status}")
        print(f"   Expected: {'FLAGGED' if expected_inappropriate else 'CLEAN'}")
        print(f"   Description: {description}")
        
        if is_inappropriate:
            print(f"   Confidence: {details['confidence']:.2f}")
            if details.get('matches'):
                matches = [f"{match_type}: {word}" for match_type, word in details['matches'][:2]]
                print(f"   Matches: {', '.join(matches)}")
        
        if not is_correct:
            print(f"   ⚠️  PREDICTION MISMATCH!")
        
        print()
    
    # Summary
    accuracy = (correct_predictions / total_tests) * 100
    print("=" * 60)
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Correct Predictions: {correct_predictions}")
    print(f"   Accuracy: {accuracy:.1f}%")
    print()
    
    # Filter statistics
    stats = filter_system.get_stats()
    print(f"🔧 Filter Configuration:")
    print(f"   Status: {'Enabled' if stats['enabled'] else 'Disabled'}")
    print(f"   Sensitivity: {stats['sensitivity'].title()}")
    print(f"   Total Filtered Words: {stats['total_filtered_words']}")
    print(f"   Active Patterns: {stats['patterns_enabled']}")
    print(f"   Categories: {', '.join(stats['categories'])}")
    print()
    
    if accuracy < 80:
        print("⚠️  Warning: Accuracy is below 80%. Consider adjusting filter sensitivity.")
    elif accuracy >= 90:
        print("🎉 Excellent! Filter accuracy is very high.")
    else:
        print("✅ Good accuracy. Filter is working well.")

if __name__ == "__main__":
    test_comprehensive_username_filter()