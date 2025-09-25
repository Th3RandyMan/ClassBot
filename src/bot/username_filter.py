"""
Advanced username filtering system for Discord bot.
Detects inappropriate usernames with configurable sensitivity and minimal false positives.
"""
import re
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

class UsernameFilter:
    def __init__(self, config_path: str = "config/username_filter.json"):
        """Initialize the username filter with configuration."""
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # Load configuration or create default
        self.config = self._load_config()
        
        # Compile regex patterns for performance
        self._compile_patterns()
        
    def _load_config(self) -> Dict:
        """Load filter configuration from JSON file."""
        default_config = {
            "enabled": True,
            "sensitivity": "medium",  # low, medium, high
            "action_on_detection": "warn",  # warn, kick, ban, none
            "whitelist": [],  # Usernames to never flag
            "word_lists": {
                "profanity": [
                    # Basic profanity (keeping it minimal and professional)
                    "fuck", "shit", "bitch", "damn", "ass", "hell",
                    "bastard", "crap", "piss", "whore", "slut"
                ],
                "hate_speech": [
                    # Racial and discriminatory terms (sample - you should expand this carefully)
                    "nigger", "faggot", "retard", "nazi", "hitler",
                    "jew", "kike", "spic", "chink", "terrorist"
                ],
                "inappropriate": [
                    # Other inappropriate terms
                    "porn", "xxx", "sex", "nude", "naked", "horny",
                    "rape", "kill", "murder", "suicide", "drug"
                ]
            },
            "patterns": {
                # Regex patterns for common evasion techniques
                "character_replacement": True,  # a->@, i->1, etc.
                "spacing_evasion": True,        # f u c k -> fuck
                "repeat_characters": True,      # fuuuuck -> fuck
                "backwards_words": True         # kcuf -> fuck
            },
            "exceptions": {
                # Context where words might be acceptable
                "educational_terms": ["hell", "damn"],  # Allow in educational context
                "common_words": ["ass", "hell"]         # Common words that need context
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return default_config
                
        except Exception as e:
            self.logger.error(f"Error loading username filter config: {e}")
            return default_config
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.compiled_patterns = {}
        
        # Character replacement patterns (l33t speak)
        if self.config["patterns"]["character_replacement"]:
            replacements = {
                '@': 'a', '4': 'a', '3': 'e', '1': 'i', '!': 'i', 
                '0': 'o', '5': 's', '7': 't', '8': 'b', '+': 't'
            }
            self.replacements = replacements
        
        # All inappropriate words combined
        all_words = []
        for word_list in self.config["word_lists"].values():
            all_words.extend(word_list)
        
        # Create regex patterns for each detection method
        self._create_word_patterns(all_words)
    
    def _create_word_patterns(self, words: List[str]):
        """Create regex patterns for word detection."""
        # Separate patterns for different detection methods
        self.basic_patterns = []
        self.leet_patterns = []
        self.spaced_patterns = []
        self.repeat_patterns = []
        self.backwards_patterns = []
        
        for word in words:
            # Basic pattern - both exact match and partial match for longer words
            self.basic_patterns.append(rf'\b{re.escape(word)}\b')  # Exact word
            if len(word) >= 4:  # Partial matches for longer words
                self.basic_patterns.append(re.escape(word))
            
            # Character replacement patterns (simplified)
            if self.config["patterns"]["character_replacement"]:
                leet_word = self._create_leet_variations(word)
                for variation in leet_word:
                    self.leet_patterns.append(variation)
            
            # Spacing patterns
            if self.config["patterns"]["spacing_evasion"]:
                spaced = r'\s*'.join(re.escape(c) for c in word)
                self.spaced_patterns.append(f'{spaced}')
            
            # Repeat patterns
            if self.config["patterns"]["repeat_characters"]:
                repeat = ''.join(f'{re.escape(c)}+' for c in word)
                self.repeat_patterns.append(repeat)
            
            # Backwards patterns
            if self.config["patterns"]["backwards_words"]:
                backwards = re.escape(word[::-1])
                self.backwards_patterns.append(f'\\b{backwards}\\b')
                if len(word) >= 4:
                    self.backwards_patterns.append(backwards)
        
        # Compile individual pattern groups
        self.basic_regex = re.compile('|'.join(self.basic_patterns), re.IGNORECASE) if self.basic_patterns else None
        self.leet_regex = re.compile('|'.join(self.leet_patterns), re.IGNORECASE) if self.leet_patterns else None
        self.spaced_regex = re.compile('|'.join(self.spaced_patterns), re.IGNORECASE) if self.spaced_patterns else None
        self.repeat_regex = re.compile('|'.join(self.repeat_patterns), re.IGNORECASE) if self.repeat_patterns else None
        self.backwards_regex = re.compile('|'.join(self.backwards_patterns), re.IGNORECASE) if self.backwards_patterns else None
    
    def _create_leet_variations(self, word: str) -> List[str]:
        """Create l33t speak variations of a word."""
        variations = []
        
        # Define character mappings
        leet_map = {
            'a': ['a', '@', '4'],
            'e': ['e', '3'],
            'i': ['i', '1', '!'],
            'o': ['o', '0'],
            's': ['s', '5', '$'],
            't': ['t', '7'],
            'b': ['b', '8'],
            'l': ['l', '1'],
            'g': ['g', '9'],
            'u': ['u', 'v'],
            'c': ['c', '('],
        }
        
        # Generate a few key variations instead of all combinations
        # This prevents regex complexity while catching common patterns
        variations.append(re.escape(word))  # Original
        
        # Common single replacements
        for char, replacements in leet_map.items():
            if char in word.lower():
                for replacement in replacements[1:]:  # Skip original character
                    leet_version = word.lower().replace(char, replacement)
                    variations.append(re.escape(leet_version))
                    # Also add partial match for longer words
                    if len(word) >= 4:
                        variations.append(re.escape(leet_version))
        
        return variations
    
    def check_username(self, username: str, user_id: Optional[int] = None) -> Tuple[bool, Dict]:
        """
        Check if username contains inappropriate content.
        
        Args:
            username: The username to check
            user_id: Optional user ID for whitelist checking
            
        Returns:
            Tuple of (is_inappropriate, details_dict)
        """
        if not self.config["enabled"]:
            return False, {"reason": "Filter disabled"}
        
        # Check whitelist
        if username.lower() in [w.lower() for w in self.config["whitelist"]]:
            return False, {"reason": "Whitelisted username"}
        
        # Clean username for analysis
        clean_username = self._clean_username(username)
        
        # Check for inappropriate content using different pattern types
        matches = []
        
        # Basic pattern matching
        if hasattr(self, 'basic_regex') and self.basic_regex:
            basic_matches = self.basic_regex.findall(clean_username.lower())
            matches.extend([("basic_match", match) for match in basic_matches if match])
        
        # L33t speak matching
        if hasattr(self, 'leet_regex') and self.leet_regex:
            leet_matches = self.leet_regex.findall(clean_username.lower())
            matches.extend([("leet_speak", match) for match in leet_matches if match])
        
        # Spaced character matching
        if hasattr(self, 'spaced_regex') and self.spaced_regex:
            spaced_matches = self.spaced_regex.findall(clean_username.lower())
            matches.extend([("spaced_evasion", match) for match in spaced_matches if match])
        
        # Repeated character matching
        if hasattr(self, 'repeat_regex') and self.repeat_regex:
            repeat_matches = self.repeat_regex.findall(clean_username.lower())
            matches.extend([("repeat_chars", match) for match in repeat_matches if match])
        
        # Backwards matching
        if hasattr(self, 'backwards_regex') and self.backwards_regex:
            backwards_matches = self.backwards_regex.findall(clean_username.lower())
            matches.extend([("backwards", match) for match in backwards_matches if match])
        
        # Additional severity-based checks
        severity_matches = self._check_severity(clean_username)
        matches.extend(severity_matches)
        
        # Remove duplicates while preserving order
        unique_matches = []
        seen = set()
        for match in matches:
            match_key = (match[0], match[1])
            if match_key not in seen:
                unique_matches.append(match)
                seen.add(match_key)
        
        matches = unique_matches
        
        # Determine if inappropriate
        is_inappropriate = len(matches) > 0
        
        # Build result details
        result = {
            "inappropriate": is_inappropriate,
            "confidence": self._calculate_confidence(matches),
            "matches": matches,
            "original_username": username,
            "cleaned_username": clean_username,
            "timestamp": datetime.now().isoformat(),
            "action_recommended": self.config["action_on_detection"] if is_inappropriate else "none"
        }
        
        if is_inappropriate:
            self.logger.warning(f"Inappropriate username detected: {username} (matches: {len(matches)})")
        
        return is_inappropriate, result
    
    def _clean_username(self, username: str) -> str:
        """Clean username for analysis (remove decorators, normalize)."""
        # Remove common decorators
        cleaned = re.sub(r'[_\-\.]+', ' ', username)
        
        # Remove numbers that might be used as separators
        cleaned = re.sub(r'\d+', '', cleaned)
        
        # Replace common character substitutions
        if hasattr(self, 'replacements'):
            for replacement, original in self.replacements.items():
                cleaned = cleaned.replace(replacement, original)
        
        return cleaned.strip()
    
    def _check_severity(self, username: str) -> List[Tuple[str, str]]:
        """Check based on configured sensitivity level."""
        matches = []
        sensitivity = self.config["sensitivity"]
        
        # High sensitivity: catch partial matches and context
        if sensitivity == "high":
            # Check for partial word matches
            for category, words in self.config["word_lists"].items():
                for word in words:
                    if word.lower() in username.lower() and len(word) >= 3:
                        matches.append((f"{category}_partial", word))
        
        # Medium sensitivity: standard checking with some context
        elif sensitivity == "medium":
            # Check for full word matches with some flexibility
            for category, words in self.config["word_lists"].items():
                for word in words:
                    # Skip if word is in exceptions for this context
                    if word in self.config["exceptions"].get("common_words", []):
                        continue
                    
                    if re.search(rf'\b{re.escape(word)}\b', username.lower()):
                        matches.append((category, word))
        
        # Low sensitivity: only obvious violations
        elif sensitivity == "low":
            # Only check hate speech and severe profanity
            severe_categories = ["hate_speech"]
            for category in severe_categories:
                if category in self.config["word_lists"]:
                    for word in self.config["word_lists"][category]:
                        if re.search(rf'\b{re.escape(word)}\b', username.lower()):
                            matches.append((category, word))
        
        return matches
    
    def _calculate_confidence(self, matches: List[Tuple[str, str]]) -> float:
        """Calculate confidence score for the detection."""
        if not matches:
            return 0.0
        
        confidence = 0.0
        for match_type, word in matches:
            if "hate_speech" in match_type:
                confidence += 0.9
            elif "profanity" in match_type:
                confidence += 0.7
            elif "inappropriate" in match_type:
                confidence += 0.5
            elif "partial" in match_type:
                confidence += 0.3
            else:
                confidence += 0.6
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def get_stats(self) -> Dict:
        """Get filter statistics and configuration info."""
        total_words = sum(len(words) for words in self.config["word_lists"].values())
        
        return {
            "enabled": self.config["enabled"],
            "sensitivity": self.config["sensitivity"],
            "total_filtered_words": total_words,
            "categories": list(self.config["word_lists"].keys()),
            "patterns_enabled": sum(1 for enabled in self.config["patterns"].values() if enabled),
            "whitelist_size": len(self.config["whitelist"])
        }
    
    def add_to_whitelist(self, username: str) -> bool:
        """Add username to whitelist."""
        try:
            if username.lower() not in [w.lower() for w in self.config["whitelist"]]:
                self.config["whitelist"].append(username)
                self._save_config()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error adding to whitelist: {e}")
            return False
    
    def remove_from_whitelist(self, username: str) -> bool:
        """Remove username from whitelist."""
        try:
            original_len = len(self.config["whitelist"])
            self.config["whitelist"] = [w for w in self.config["whitelist"] 
                                       if w.lower() != username.lower()]
            if len(self.config["whitelist"]) < original_len:
                self._save_config()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing from whitelist: {e}")
            return False
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

# Usage example and test function
def test_username_filter():
    """Test the username filter with various examples."""
    filter_system = UsernameFilter()
    
    test_cases = [
        "normaluser123",
        "f**k_this",
        "h4t3_speech", 
        "inappropriate_n@me",
        "ClassTA_Helper",
        "study_group_leader"
    ]
    
    print("Username Filter Test Results:")
    print("-" * 50)
    
    for username in test_cases:
        is_bad, details = filter_system.check_username(username)
        print(f"'{username}': {'❌ FLAGGED' if is_bad else '✅ CLEAN'}")
        if is_bad:
            print(f"  Confidence: {details['confidence']:.2f}")
            print(f"  Matches: {len(details['matches'])}")
            print(f"  Action: {details['action_recommended']}")
        print()

if __name__ == "__main__":
    test_username_filter()