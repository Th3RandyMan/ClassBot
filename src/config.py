"""
Configuration file for Class Bot
Contains default settings and configuration options
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
class BotConfig:
    # Discord Settings
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
    
    # Role Configuration
    ALLOWED_ROLE_NAME = os.getenv('ALLOWED_ROLE_NAME', 'Student')
    ADMIN_ROLE_NAME = os.getenv('ADMIN_ROLE_NAME', 'Admin')
    
    # Logging
    LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID')) if os.getenv('LOG_CHANNEL_ID') else None
    
    # Bot Settings
    COMMAND_PREFIX = '!'
    DESCRIPTION = 'Class Bot - Monitors and manages code posting permissions'
    
    # Code Detection Settings
    MIN_CODE_PATTERNS = 2  # Minimum pattern matches to consider as code
    MIN_CODE_INDICATORS = 2  # Minimum structure indicators for code detection
    MIN_TEXT_LENGTH = 10  # Minimum text length to analyze
    
    # Rate Limiting
    REMOVAL_DELAY = 1  # Seconds between user removals to avoid rate limits
    
    # Tesseract Configuration (for Windows)
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.TOKEN:
            errors.append("DISCORD_TOKEN is required")
        
        if not cls.GUILD_ID:
            errors.append("GUILD_ID is required")
            
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("=== Class Bot Configuration ===")
        print(f"Guild ID: {cls.GUILD_ID}")
        print(f"Allowed Role: {cls.ALLOWED_ROLE_NAME}")
        print(f"Admin Role: {cls.ADMIN_ROLE_NAME}")
        print(f"Log Channel ID: {cls.LOG_CHANNEL_ID}")
        print(f"Command Prefix: {cls.COMMAND_PREFIX}")
        print("===============================")

# Code Detection Patterns
CODE_PATTERNS = [
    # Programming language keywords
    r'\b(def|class|import|from|if|else|elif|for|while|try|except|finally|return|yield|break|continue|pass|with|as|lambda|global|nonlocal)\b',
    r'\b(function|var|let|const|int|string|bool|float|double|char|void|public|private|protected|static|final|abstract|interface|extends|implements)\b',
    r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|FROM|WHERE|JOIN|GROUP|ORDER|BY|HAVING|UNION|INDEX)\b',
    
    # Syntax patterns
    r'[\{\}\[\]();].*[\{\}\[\]();]',  # Multiple brackets/parentheses
    r'#include\s*<.*>',  # C/C++ includes
    r'@\w+',  # Decorators/annotations
    r'\b\w+\s*\(\s*.*\s*\)',  # Function calls
    
    # Output statements
    r'console\.log|print\(|System\.out|cout\s*<<|printf\(|println\(',
    
    # Comments (be careful not to match URLs)
    r'^\s*\/\/.*$|^\s*\/\*.*\*\/\s*$|^\s*#(?!http).*$',
    
    # Variable assignments
    r'^\s*[\w\s]*\s*[=]\s*[\w\s\(\)\[\]\'\"]*;?\s*$',
    
    # HTML/XML tags
    r'<\/?[a-z][\s\S]*>',
    
    # Common file extensions in code
    r'\.(py|js|java|cpp|c|h|html|css|php|rb|go|rs|swift|kt|scala|sh|sql|json|xml|yaml|yml)(\s|$)',
]

# Warning Messages
class Messages:
    CODE_DETECTED_WARNING = "⚠️ **Code Detected!**\n\nYou are not allowed to post code without the **{role}** role.\nYour message has been deleted.\n\n**Warning #{count}** - Contact an admin if you believe this is a mistake."
    
    INSUFFICIENT_PERMISSIONS = "❌ You don't have permission to use this command."
    
    NO_ROLELESS_USERS = "✅ No users found without roles."
    
    OPERATION_CANCELLED = "❌ Operation cancelled."
    
    OPERATION_TIMEOUT = "⏰ Confirmation timed out. Operation cancelled."
    
    REMOVAL_CONFIRMATION = "⚠️ **Confirmation Required**\n\nAre you sure you want to remove **{count}** users without roles?\n\n**This action cannot be undone!**"

# Embed Colors
class Colors:
    WARNING = 0xff9900     # Orange
    ERROR = 0xff0000       # Red  
    SUCCESS = 0x00ff00     # Green
    INFO = 0x0099ff        # Blue
    DANGER = 0xff0000      # Red (for destructive actions)

if __name__ == "__main__":
    # Test configuration
    errors = BotConfig.validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")
        BotConfig.print_config()