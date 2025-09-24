import discord
from discord.ext import commands
import os
import re
import logging
import asyncio
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import io
import requests
import platform
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging for cloud deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This will output to console/logs in cloud
    ]
)
logger = logging.getLogger(__name__)

# Configure Tesseract for different environments
def configure_tesseract():
    """Configure Tesseract OCR for different deployment environments"""
    system = platform.system().lower()
    
    if system == "linux":
        # Cloud deployment (Render, Heroku, etc.)
        linux_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',  # For some cloud environments
            'tesseract'  # If in PATH
        ]
        
        for path in linux_paths:
            if path == 'tesseract' or os.path.exists(path):
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    # Test if it works
                    version = pytesseract.get_tesseract_version()
                    logger.info(f"Configured Tesseract for Linux: {path} (version {version})")
                    return True
                except Exception as e:
                    logger.debug(f"Tesseract path {path} failed: {e}")
                    continue
        
        logger.warning("Tesseract not found on Linux. Image detection will be disabled.")
        return False
        
    elif system == "windows":
        # Local Windows development
        windows_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            'tesseract'  # If in PATH
        ]
        
        for path in windows_paths:
            if path == 'tesseract' or os.path.exists(path):
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    # Test if it works
                    version = pytesseract.get_tesseract_version()
                    logger.info(f"Configured Tesseract for Windows: {path} (version {version})")
                    return True
                except Exception as e:
                    logger.debug(f"Tesseract path {path} failed: {e}")
                    continue
        
        logger.warning("Tesseract not found on Windows. Image detection will be disabled.")
        return False
    else:
        logger.info(f"Unknown system: {system}. Trying default Tesseract configuration.")
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Default Tesseract configuration working (version {version})")
            return True
        except Exception as e:
            logger.warning(f"Default Tesseract configuration failed: {e}")
            return False

# Configure Tesseract on startup and store result
TESSERACT_AVAILABLE = configure_tesseract()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
ALLOWED_ROLE_NAME = os.getenv('ALLOWED_ROLE_NAME', '')  # Empty means any role is allowed
ADMIN_ROLE_NAMES = os.getenv('ADMIN_ROLE_NAMES', 'Professor,Teaching Assistant (TA)').split(',')
ADMIN_ROLE_NAMES = [role.strip() for role in ADMIN_ROLE_NAMES]  # Clean up whitespace
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID')) if os.getenv('LOG_CHANNEL_ID') else None

# Environment detection
IS_CLOUD_DEPLOYMENT = os.getenv('RENDER') is not None or os.getenv('DYNO') is not None or platform.system().lower() == 'linux'

logger.info(f"Bot starting up - Cloud deployment: {IS_CLOUD_DEPLOYMENT}")
logger.info(f"Environment: {platform.system()} {platform.release()}")
logger.info(f"Python version: {platform.python_version()}")
logger.info(f"Admin roles configured: {ADMIN_ROLE_NAMES}")
logger.info(f"Code posting allowed for: {'Any role' if not ALLOWED_ROLE_NAME else ALLOWED_ROLE_NAME}")
logger.info(f"OCR (Image detection) available: {TESSERACT_AVAILABLE}")

# Log environment variables (excluding sensitive ones)
logger.debug(f"GUILD_ID: {GUILD_ID}")
logger.debug(f"LOG_CHANNEL_ID: {LOG_CHANNEL_ID}")

# Additional environment info for debugging
if IS_CLOUD_DEPLOYMENT:
    logger.info("Running in cloud environment - using Linux configuration")
    logger.info(f"Render deployment: {os.getenv('RENDER') is not None}")
    logger.info(f"Heroku deployment: {os.getenv('DYNO') is not None}")
else:
    logger.info("Running in local development environment")

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Enhanced Error Recovery System
class ErrorRecoverySystem:
    """Handles automatic reconnection and error recovery"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # seconds
        self.is_recovering = False
        
    async def handle_connection_error(self, error):
        """Handle connection-related errors with automatic recovery"""
        if self.is_recovering:
            return  # Already handling recovery
            
        self.is_recovering = True
        logger.error(f"Connection error occurred: {error}")
        
        while self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * self.reconnect_attempts  # Exponential backoff
            
            logger.info(f"Attempting reconnect #{self.reconnect_attempts} in {delay} seconds...")
            await asyncio.sleep(delay)
            
            try:
                # Save warnings before potential restart
                warning_system.save_warnings()
                logger.info("Saved warnings before reconnection attempt")
                
                # The bot will automatically try to reconnect
                self.is_recovering = False
                self.reconnect_attempts = 0
                logger.info("Successfully recovered from connection error")
                return
                
            except Exception as e:
                logger.error(f"Reconnection attempt #{self.reconnect_attempts} failed: {e}")
                
        # Max attempts reached
        logger.critical(f"Failed to reconnect after {self.max_reconnect_attempts} attempts")
        self.is_recovering = False
    
    def reset_reconnect_counter(self):
        """Reset reconnection attempts counter on successful connection"""
        self.reconnect_attempts = 0

# Initialize error recovery system
error_recovery = ErrorRecoverySystem(bot)

# Enhanced error handlers
@bot.event
async def on_disconnect():
    """Handle bot disconnection"""
    logger.warning("Bot disconnected from Discord")
    await error_recovery.handle_connection_error("Discord disconnection")

@bot.event 
async def on_resumed():
    """Handle bot reconnection"""
    logger.info("Bot resumed connection to Discord")
    error_recovery.reset_reconnect_counter()

@bot.event
async def on_connect():
    """Handle successful bot connection"""
    logger.info("Bot connected to Discord")
    error_recovery.reset_reconnect_counter()

# Global error handler for commands
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully"""
    if isinstance(error, commands.CommandNotFound):
        # Silently ignore unknown commands
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the required permissions for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid command arguments. Please check your input.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, discord.HTTPException):
        logger.error(f"Discord HTTP error in command {ctx.command}: {error}")
        await ctx.send("❌ A network error occurred. Please try again.")
    else:
        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)
        await ctx.send("❌ An unexpected error occurred. The issue has been logged.")
        
        # Save warnings in case of critical error
        try:
            warning_system.save_warnings()
        except:
            pass

# Code detection patterns
CODE_PATTERNS = [
    # Programming language keywords and patterns
    r'\b(def|class|import|from|if|else|elif|for|while|try|except|return|function|var|let|const|int|string|bool|float|double|char|void|public|private|protected|static)\b',
    r'[\{\}\[\]();].*[\{\}\[\]();]',  # Multiple brackets/parentheses
    r'#include\s*<.*>',  # C/C++ includes
    r'@\w+',  # Decorators/annotations
    r'\b\w+\s*\(\s*\w*\s*\w+\s*\w*\s*\)',  # Function calls
    r'console\.log|print\(|System\.out|cout\s*<<',  # Output statements
    r'\/\/.*|\/\*.*\*\/|#.*',  # Comments (but be careful with URLs)
    r'^\s*[\w\s]*\s*[=]\s*[\w\s\(\)\[\]\'\"]*;?\s*$',  # Variable assignments
    r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b',  # SQL keywords
    r'<\/?[a-z][\s\S]*>',  # HTML tags
]

# Compile regex patterns for better performance
compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in CODE_PATTERNS]

class PersistentWarningSystem:
    """Persistent warning system with JSON storage and auto-expiration"""
    
    def __init__(self, filename="warnings.json", expiry_days=30):
        self.filename = filename
        self.expiry_days = expiry_days
        self.warnings = {}
        self.load_warnings()
        
    def load_warnings(self):
        """Load warnings from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to int and parse timestamps
                    self.warnings = {}
                    for user_id, warning_list in data.items():
                        self.warnings[int(user_id)] = []
                        for warning in warning_list:
                            if isinstance(warning, dict):
                                # New format with timestamp
                                self.warnings[int(user_id)].append({
                                    'reason': warning['reason'],
                                    'timestamp': datetime.fromisoformat(warning['timestamp'])
                                })
                            else:
                                # Old format - add current timestamp
                                self.warnings[int(user_id)].append({
                                    'reason': warning,
                                    'timestamp': datetime.now()
                                })
                logger.info(f"Loaded {len(self.warnings)} user warning records")
            else:
                logger.info("No existing warnings file found - starting fresh")
        except Exception as e:
            logger.error(f"Error loading warnings: {e}")
            self.warnings = {}
    
    def save_warnings(self):
        """Save warnings to JSON file"""
        try:
            # Clean expired warnings before saving
            self.cleanup_expired_warnings()
            
            # Convert to serializable format
            data = {}
            for user_id, warning_list in self.warnings.items():
                data[str(user_id)] = []
                for warning in warning_list:
                    data[str(user_id)].append({
                        'reason': warning['reason'],
                        'timestamp': warning['timestamp'].isoformat()
                    })
            
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved warnings to {self.filename}")
        except Exception as e:
            logger.error(f"Error saving warnings: {e}")
    
    def cleanup_expired_warnings(self):
        """Remove warnings older than expiry_days"""
        cutoff_date = datetime.now() - timedelta(days=self.expiry_days)
        expired_count = 0
        
        for user_id in list(self.warnings.keys()):
            original_count = len(self.warnings[user_id])
            self.warnings[user_id] = [
                warning for warning in self.warnings[user_id]
                if warning['timestamp'] > cutoff_date
            ]
            expired_count += original_count - len(self.warnings[user_id])
            
            # Remove empty user records
            if not self.warnings[user_id]:
                del self.warnings[user_id]
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired warnings")
    
    def add_warning(self, user_id, reason):
        """Add a warning for a user"""
        if user_id not in self.warnings:
            self.warnings[user_id] = []
        
        warning = {
            'reason': reason,
            'timestamp': datetime.now()
        }
        self.warnings[user_id].append(warning)
        self.save_warnings()
        return len(self.warnings[user_id])
    
    def get_warnings(self, user_id):
        """Get all warnings for a user"""
        self.cleanup_expired_warnings()
        return self.warnings.get(user_id, [])
    
    def get_warning_count(self, user_id):
        """Get warning count for a user"""
        return len(self.get_warnings(user_id))
    
    def clear_warnings(self, user_id):
        """Clear all warnings for a user"""
        if user_id in self.warnings:
            del self.warnings[user_id]
            self.save_warnings()
            return True
        return False
    
    def get_stats(self):
        """Get warning system statistics"""
        self.cleanup_expired_warnings()
        total_users = len(self.warnings)
        total_warnings = sum(len(warnings) for warnings in self.warnings.values())
        return {'total_users_with_warnings': total_users, 'total_active_warnings': total_warnings}

# Initialize persistent warning system
warning_system = PersistentWarningSystem()

class ClassBot:
    def __init__(self):
        self.bot = bot
        
    def has_allowed_role(self, member):
        """Check if member has any role (anyone with a role can post code)"""
        if not member.roles:
            return False
        
        # If ALLOWED_ROLE_NAME is empty/None, anyone with ANY role can post code
        if not ALLOWED_ROLE_NAME:
            # Check if user has any role other than @everyone
            user_roles = [role for role in member.roles if role.name != "@everyone"]
            return len(user_roles) > 0
        else:
            # Check for specific role
            return any(role.name == ALLOWED_ROLE_NAME for role in member.roles)
    
    def has_admin_role(self, member):
        """Check if member has any of the admin roles"""
        if not member.roles:
            return False
        
        member_role_names = [role.name for role in member.roles]
        return any(admin_role in member_role_names for admin_role in ADMIN_ROLE_NAMES)
    
    def detect_code_in_text(self, text):
        """Detect if text contains code using multiple sophisticated heuristics"""
        if not text or len(text.strip()) < 15:
            return False
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Score different aspects of the text
        keyword_score = self._analyze_keywords(text_lower)
        structure_score = self._analyze_structure(lines)
        syntax_score = self._analyze_syntax(text)
        context_score = self._analyze_context(text_lower)
        
        # Calculate weighted total score
        total_score = (
            keyword_score * 0.3 +      # Keywords are important but not definitive
            structure_score * 0.4 +    # Structure is very important for code
            syntax_score * 0.4 +       # Syntax patterns are crucial
            context_score * 0.2        # Context helps reduce false positives
        )
        
        # Debug logging (optional - can be removed in production)
        if total_score > 0.5:  # Only log when close to threshold
            print(f"Code detection scores: keyword={keyword_score:.2f}, structure={structure_score:.2f}, syntax={syntax_score:.2f}, context={context_score:.2f}, total={total_score:.2f}")
        
        # Threshold for code detection (adjustable)
        return total_score >= 0.6
    
    def _analyze_keywords(self, text_lower):
        """Analyze programming keywords with context awareness"""
        # More specific keyword patterns that are less likely to appear in normal text
        strong_keywords = [
            r'\bdef\s+\w+\s*\(',           # function definitions
            r'\bclass\s+\w+\s*[:\(]',      # class definitions
            r'\bimport\s+\w+',             # import statements
            r'\bfrom\s+\w+\s+import',      # from import statements
            r'\breturn\s+[^;]+[;\n]?',     # return statements
            r'\b(console\.log|print|printf|cout|System\.out)\s*\(',  # output functions
            r'\b(int|string|bool|float|double|char|void)\s+\w+',     # type declarations
            r'\b(public|private|protected|static)\s+',               # access modifiers
        ]
        
        weak_keywords = [
            r'\b(if|else|elif|for|while|try|except|catch)\b',  # Control flow (common in speech)
            r'\b(function|var|let|const)\b',                   # Variable declarations
        ]
        
        strong_matches = 0
        weak_matches = 0
        
        for pattern in strong_keywords:
            if re.search(pattern, text_lower):
                strong_matches += 1
        
        for pattern in weak_keywords:
            matches = len(re.findall(pattern, text_lower))
            weak_matches += matches
        
        # Strong keywords are much more indicative
        keyword_score = (strong_matches * 0.4) + (min(weak_matches, 5) * 0.05)
        return min(keyword_score, 1.0)
    
    def _analyze_structure(self, lines):
        """Analyze code-like structural patterns"""
        if len(lines) < 2:
            return 0
        
        structure_indicators = 0
        indented_lines = 0
        lines_with_endings = 0
        bracket_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for consistent indentation (multiple levels)
            if line.startswith('    ') or line.startswith('\t'):
                indented_lines += 1
            
            # Check for code-like line endings
            if stripped.endswith((';', '{', '}', ':', ',')):
                lines_with_endings += 1
            
            # Check for brackets at end of lines (function calls, array access)
            if re.search(r'[\{\}\[\]()]\s*$', stripped):
                bracket_lines += 1
        
        total_lines = len([l for l in lines if l.strip()])
        
        if total_lines == 0:
            return 0
        
        # Calculate ratios
        indentation_ratio = indented_lines / total_lines
        ending_ratio = lines_with_endings / total_lines
        bracket_ratio = bracket_lines / total_lines
        
        # Multiple lines with indentation is a strong indicator
        if indented_lines >= 3 and indentation_ratio >= 0.5:
            structure_indicators += 0.6
        
        # High ratio of lines ending with code punctuation
        if ending_ratio >= 0.4:
            structure_indicators += 0.4
        
        # Multiple bracket patterns
        if bracket_ratio >= 0.3:
            structure_indicators += 0.3
        
        return min(structure_indicators, 1.0)
    
    def _analyze_syntax(self, text):
        """Analyze syntax patterns specific to code"""
        syntax_score = 0
        
        # Function call patterns (more specific)
        function_calls = len(re.findall(r'\w+\s*\([^)]*\)\s*[;,\n]', text))
        if function_calls >= 2:
            syntax_score += 0.4
        elif function_calls == 1:
            syntax_score += 0.2
        
        # Variable assignment patterns
        assignments = len(re.findall(r'\w+\s*[=]\s*[^=][^;,\n]*[;,\n]', text))
        if assignments >= 2:
            syntax_score += 0.3
        elif assignments >= 1:
            syntax_score += 0.15
        
        # Multiple brackets/parentheses in sequence
        bracket_sequences = len(re.findall(r'[\{\}\[\]()]+', text))
        if bracket_sequences >= 4:
            syntax_score += 0.3
        elif bracket_sequences >= 2:
            syntax_score += 0.15
        
        # Comments (but avoid URLs)
        comment_patterns = [
            r'^\s*//[^\n]+$',           # Single line comments
            r'^\s*/\*.*\*/\s*$',        # Block comments
            r'^\s*#(?!http)[^\n]+$',    # Python comments (avoid #hashtags and URLs)
        ]
        
        comments = 0
        for pattern in comment_patterns:
            comments += len(re.findall(pattern, text, re.MULTILINE))
        
        if comments >= 1:
            syntax_score += 0.2
        
        # Code blocks (multiple lines with brackets)
        if re.search(r'\{[^}]*\n[^}]*\}', text, re.DOTALL):
            syntax_score += 0.4
        
        return min(syntax_score, 1.0)
    
    def _analyze_context(self, text_lower):
        """Analyze context to reduce false positives"""
        # Phrases that suggest natural language rather than code
        natural_language_phrases = [
            r'\b(i think|i believe|in my opinion|what if|how about|let me know)\b',
            r'\b(please|thank you|thanks|could you|would you|can you)\b',
            r'\b(the problem is|i need help|i\'m confused|i don\'t understand)\b',
            r'\b(assignment|homework|project|exercise|question)\b',
        ]
        
        # Code-specific phrases that increase confidence
        code_phrases = [
            r'\b(compile|debug|syntax error|runtime error|null pointer)\b',
            r'\b(algorithm|data structure|method|function|variable|array)\b',
            r'\b(loop|iteration|recursion|binary search|sorting)\b',
        ]
        
        natural_count = 0
        code_count = 0
        
        for pattern in natural_language_phrases:
            natural_count += len(re.findall(pattern, text_lower))
        
        for pattern in code_phrases:
            code_count += len(re.findall(pattern, text_lower))
        
        # If lots of natural language indicators, reduce score
        if natural_count >= 3:
            return -0.3
        elif natural_count >= 1:
            return -0.1
        
        # If code-specific terms, increase confidence
        if code_count >= 2:
            return 0.2
        elif code_count >= 1:
            return 0.1
        
        return 0
    
    async def detect_code_in_image(self, image_url):
        """Extract text from image and check for code"""
        try:
            # Check if OCR is available
            if not self._is_ocr_available():
                logger.warning("OCR not available - skipping image detection")
                return False
            
            # Download image with timeout
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to download image: {response.status_code}")
                return False
            
            # Check file size (limit to 10MB)
            if len(response.content) > 10 * 1024 * 1024:
                logger.warning("Image too large for processing")
                return False
                
            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content))
            
            # Resize if too large (for faster processing)
            if image.width > 2000 or image.height > 2000:
                image.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image, config='--psm 6')
            
            if not extracted_text.strip():
                logger.debug("No text extracted from image")
                return False
            
            logger.debug(f"Extracted text from image: {extracted_text[:100]}...")
            
            # Check if extracted text contains code
            return self.detect_code_in_text(extracted_text)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading image: {e}")
            return False
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract not found - image detection disabled")
            # Return None to indicate OCR unavailable (not False for no code)
            return None
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            # Return None to indicate processing error (not False for no code)
            return None
    
    def _is_ocr_available(self):
        """Check if OCR functionality is available"""
        return TESSERACT_AVAILABLE
    
    async def warn_user(self, member, channel, reason):
        """Issue a warning to a user"""
        user_id = member.id
        
        warning_count = warning_system.add_warning(user_id, reason)
        
        # Send warning message
        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"{member.mention}, you are not allowed to post code without having a role assigned.",
            color=0xff9900
        )
        embed.add_field(name="Warning Count", value=f"{warning_count}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Required", value="You must have a role assigned to post code", inline=False)
        embed.set_footer(text="Contact a Professor or TA if you need a role assigned.")
        
        await channel.send(embed=embed)
        
        # Log to admin channel if configured
        if LOG_CHANNEL_ID:
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="Code Detection - Warning Issued",
                    color=0xff9900
                )
                log_embed.add_field(name="User", value=f"{member.display_name} ({member.id})", inline=True)
                log_embed.add_field(name="Channel", value=channel.mention, inline=True)
                log_embed.add_field(name="Warning Count", value=f"{warning_count}", inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                await log_channel.send(embed=log_embed)

    async def warn_user_about_image(self, member, channel):
        """Issue a special warning about image posting when OCR is unavailable"""
        embed = discord.Embed(
            title="🚨 Image Upload Alert",
            description=f"{member.mention}, image content verification is currently unavailable. Please ensure your image does not contain code, or contact an admin for assistance.",
            color=0xff6600  # Orange color for alerts
        )
        embed.add_field(
            name="Why this happened:",
            value="The bot cannot currently scan images for code content. To be safe, images from users without roles are being flagged.",
            inline=False
        )
        embed.add_field(
            name="What you can do:",
            value="• Get assigned an appropriate role\n• Contact an admin if this is not code-related\n• Repost as text instead of an image",
            inline=False
        )
        embed.set_footer(text=f"User: {member.display_name}")
        
        await channel.send(embed=embed)
        
        # Log to admin channel if configured
        if LOG_CHANNEL_ID:
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="Image Alert - OCR Unavailable",
                    color=0xff6600
                )
                log_embed.add_field(name="User", value=f"{member.display_name} ({member.id})", inline=True)
                log_embed.add_field(name="Channel", value=channel.mention, inline=True)
                log_embed.add_field(name="Issue", value="Image posted when OCR unavailable", inline=False)
                await log_channel.send(embed=log_embed)

class ConfirmView(discord.ui.View):
    def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()

# Initialize bot instance
class_bot = ClassBot()

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has landed! Class Bot is now monitoring for code.')
    print(f'Class Bot is ready! Logged in as {bot.user}')

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Check if user has allowed role
    if class_bot.has_allowed_role(message.author):
        return
    
    # Check for code in message content
    code_detected = False
    reason = ""
    
    if message.content and class_bot.detect_code_in_text(message.content):
        code_detected = True
        reason = "Code detected in text message"
    
    # Check attachments for code in images
    if message.attachments and not code_detected:
        has_images = False
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                has_images = True
                image_result = await class_bot.detect_code_in_image(attachment.url)
                
                if image_result is True:  # Code detected
                    code_detected = True
                    reason = "Code detected in uploaded image"
                    break
                elif image_result is None:  # OCR not available
                    # Send alert about image when OCR is unavailable
                    await class_bot.warn_user_about_image(message.author, message.channel)
                    code_detected = True  # Treat as violation when OCR unavailable
                    reason = "Image posted when OCR unavailable - cannot verify content"
                    break
                # If image_result is False, continue checking other images
    
    # If code is detected, delete message and warn user
    if code_detected:
        try:
            await message.delete()
            await class_bot.warn_user(message.author, message.channel, reason)
        except discord.errors.NotFound:
            # Message was already deleted
            pass
        except discord.errors.Forbidden:
            logger.warning("Bot lacks permission to delete messages")

@bot.command(name='remove_roleless')
async def remove_roleless_users(ctx):
    """Remove all users without any role (Admin only)"""
    
    # Check if user has admin role
    if not class_bot.has_admin_role(ctx.author):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    # Get all members without roles (excluding @everyone)
    roleless_members = []
    for member in ctx.guild.members:
        if len(member.roles) == 1 and member.roles[0].name == "@everyone":
            if not member.bot:  # Don't include bots
                roleless_members.append(member)
    
    if not roleless_members:
        await ctx.send("✅ No users found without roles.")
        return
    
    # Create confirmation embed
    embed = discord.Embed(
        title="⚠️ Confirmation Required",
        description=f"Are you sure you want to remove **{len(roleless_members)}** users without roles?",
        color=0xff0000
    )
    
    member_list = "\n".join([f"• {member.display_name} ({member.name})" for member in roleless_members[:10]])
    if len(roleless_members) > 10:
        member_list += f"\n... and {len(roleless_members) - 10} more"
    
    embed.add_field(name="Users to be removed:", value=member_list, inline=False)
    embed.set_footer(text="This action cannot be undone!")
    
    # Send confirmation message with buttons
    view = ConfirmView()
    message = await ctx.send(embed=embed, view=view)
    
    # Wait for user response
    await view.wait()
    
    if view.value is None:
        await message.edit(content="⏰ Confirmation timed out. Operation cancelled.", embed=None, view=None)
        return
    elif view.value:
        # User confirmed, proceed with removal
        removed_count = 0
        failed_removals = []
        
        progress_embed = discord.Embed(
            title="🔄 Removing users...",
            description="This may take a moment.",
            color=0xffa500
        )
        await message.edit(embed=progress_embed, view=None)
        
        for member in roleless_members:
            try:
                await member.kick(reason=f"Removed by {ctx.author.name} - No role assigned")
                removed_count += 1
                await asyncio.sleep(1)  # Rate limiting
            except discord.errors.Forbidden:
                failed_removals.append(f"{member.display_name} (insufficient permissions)")
            except discord.errors.HTTPException as e:
                failed_removals.append(f"{member.display_name} (error: {str(e)})")
        
        # Send results
        result_embed = discord.Embed(
            title="✅ Operation Complete",
            color=0x00ff00
        )
        result_embed.add_field(name="Successfully Removed", value=str(removed_count), inline=True)
        result_embed.add_field(name="Failed", value=str(len(failed_removals)), inline=True)
        
        if failed_removals:
            failures_text = "\n".join(failed_removals[:5])
            if len(failed_removals) > 5:
                failures_text += f"\n... and {len(failed_removals) - 5} more"
            result_embed.add_field(name="Failed Removals", value=failures_text, inline=False)
        
        await message.edit(embed=result_embed)
        
        # Log to admin channel
        if LOG_CHANNEL_ID:
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="Mass User Removal",
                    color=0xff0000
                )
                log_embed.add_field(name="Executed by", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Users Removed", value=str(removed_count), inline=True)
                log_embed.add_field(name="Failed", value=str(len(failed_removals)), inline=True)
                await log_channel.send(embed=log_embed)
    else:
        # User cancelled
        await message.edit(content="❌ Operation cancelled.", embed=None, view=None)

@bot.command(name='warnings')
async def check_warnings(ctx, member: discord.Member = None):
    """Check warnings for a user (Admin only)"""
    
    if not class_bot.has_admin_role(ctx.author):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    if member is None:
        member = ctx.author
    
    user_id = member.id
    warnings = warning_system.get_warnings(user_id)
    
    embed = discord.Embed(
        title=f"Warnings for {member.display_name}",
        color=0x0099ff
    )
    
    if warnings:
        warning_text = []
        for i, warning in enumerate(warnings):
            timestamp = warning['timestamp'].strftime("%Y-%m-%d %H:%M")
            warning_text.append(f"{i+1}. {warning['reason']} ({timestamp})")
        embed.add_field(name=f"Total Warnings: {len(warnings)}", value="\n".join(warning_text), inline=False)
        
        # Show expiration info
        expiry_date = datetime.now() + timedelta(days=warning_system.expiry_days)
        embed.set_footer(text=f"Warnings automatically expire after {warning_system.expiry_days} days")
    else:
        embed.add_field(name="No Warnings", value="This user has no warnings.", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='clear_warnings')
async def clear_warnings(ctx, member: discord.Member):
    """Clear warnings for a user (Admin only)"""
    
    if not class_bot.has_admin_role(ctx.author):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    user_id = member.id
    if warning_system.clear_warnings(user_id):
        await ctx.send(f"✅ Cleared all warnings for {member.display_name}")
    else:
        await ctx.send(f"ℹ️ {member.display_name} has no warnings to clear.")

@bot.command(name='clear_channel')
async def clear_channel_messages(ctx, channel: discord.TextChannel, limit: int = None):
    """Clear all messages from a specified channel (Admin only) - Optimized for speed"""
    
    if not class_bot.has_admin_role(ctx.author):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    # Create confirmation embed without slow message counting
    if limit is None:
        embed = discord.Embed(
            title="⚠️ Clear Channel Confirmation",
            description=f"Are you sure you want to **delete ALL messages** from #{channel.name}?",
            color=0xff0000
        )
        
        embed.add_field(
            name="⚠️ Warning", 
            value="This will delete **ALL messages** in the channel!\nThis action **cannot be undone**!",
            inline=False
        )
        embed.add_field(
            name="Channel Info",
            value=f"**Channel:** #{channel.name}\n**Requested by:** {ctx.author.mention}",
            inline=False
        )
        embed.set_footer(text="Use '!clear_channel #channel <number>' to delete a specific number of messages instead.")
    else:
        # Limited clear with specific number
        if limit <= 0:
            await ctx.send("❌ Message limit must be a positive number.")
            return
        
        if limit > 1000:
            await ctx.send("❌ Cannot delete more than 1000 messages at once. Use the command without a number to clear all messages.")
            return
        
        embed = discord.Embed(
            title="⚠️ Clear Messages Confirmation",
            description=f"Are you sure you want to delete the **last {limit} messages** from #{channel.name}?",
            color=0xff9900
        )
        
        embed.add_field(
            name="Action Details",
            value=f"**Channel:** #{channel.name}\n**Messages to delete:** {limit}\n**Requested by:** {ctx.author.mention}",
            inline=False
        )
        embed.set_footer(text="This action cannot be undone!")
    
    # Send confirmation message with buttons
    view = ConfirmView()
    confirmation_msg = await ctx.send(embed=embed, view=view)
    
    # Wait for user response
    await view.wait()
    
    if view.value is None:
        await confirmation_msg.edit(content="⏰ Confirmation timed out. Channel clearing cancelled.", embed=None, view=None)
        return
    elif view.value:
        # User confirmed, proceed with clearing
        try:
            # Immediate feedback
            progress_embed = discord.Embed(
                title="� Clearing messages...",
                description=f"{'Deleting all messages' if limit is None else f'Deleting last {limit} messages'} from #{channel.name}...",
                color=0xffa500
            )
            await confirmation_msg.edit(embed=progress_embed, view=None)
            
            deleted_count = 0
            
            if limit is None:
                # Optimized bulk delete for all messages
                while True:
                    # Use bulk delete in chunks of 100 (Discord's limit for bulk delete)
                    deleted = await channel.purge(limit=100, bulk=True)
                    if not deleted:
                        break
                    deleted_count += len(deleted)
                    
                    # Update progress every 200 messages for very large channels
                    if deleted_count % 200 == 0:
                        progress_embed.description = f"Deleted {deleted_count} messages from #{channel.name}... (continuing)"
                        try:
                            await confirmation_msg.edit(embed=progress_embed)
                        except:
                            pass  # Don't let progress updates break the deletion
            else:
                # Optimized delete for specific limit
                deleted_messages = await channel.purge(limit=limit, bulk=True)
                deleted_count = len(deleted_messages)
            
            # Send success message
            success_embed = discord.Embed(
                title="✅ Channel Cleared",
                description=f"Successfully deleted **{deleted_count} messages** from #{channel.name}",
                color=0x00ff00
            )
            success_embed.add_field(name="Cleared by", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
            
            await confirmation_msg.edit(embed=success_embed)
            
            # Log to admin channel if configured
            if LOG_CHANNEL_ID and channel.id != LOG_CHANNEL_ID:
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = discord.Embed(
                        title="🗑️ Channel Messages Cleared",
                        color=0xff9900
                    )
                    log_embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
                    log_embed.add_field(name="Messages Deleted", value=str(deleted_count), inline=True)
                    log_embed.add_field(name="Cleared by", value=ctx.author.mention, inline=True)
                    await log_channel.send(embed=log_embed)
                    
        except discord.errors.Forbidden:
            error_embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to delete messages in that channel.",
                color=0xff0000
            )
            await confirmation_msg.edit(embed=error_embed, view=None)
        except discord.errors.HTTPException as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while clearing messages: {str(e)}",
                color=0xff0000
            )
            await confirmation_msg.edit(embed=error_embed, view=None)
        except Exception as e:
            logger.error(f"Error clearing channel {channel.name}: {e}")
            error_embed = discord.Embed(
                title="❌ Unexpected Error",
                description="An unexpected error occurred. Please try again or contact support.",
                color=0xff0000
            )
            await confirmation_msg.edit(embed=error_embed, view=None)
    else:
        # User cancelled
        await confirmation_msg.edit(content="❌ Channel clearing cancelled.", embed=None, view=None)

@bot.command(name='help_classbot')
async def help_command(ctx):
    """Display help information about Class Bot"""
    
    embed = discord.Embed(
        title="🤖 Class Bot Help",
        description="Class Bot monitors users without roles and prevents them from posting code.",
        color=0x0099ff
    )
    
    embed.add_field(
        name="📋 Features",
        value="• Detects code in text messages\n• Detects code in uploaded images\n• Warns users without roles\n• Tracks warning counts",
        inline=False
    )
    
    if class_bot.has_admin_role(ctx.author):
        embed.add_field(
            name="👑 Admin Commands",
            value="• `!remove_roleless` - Remove all users without roles\n• `!warnings @user` - Check user warnings\n• `!clear_warnings @user` - Clear user warnings\n• `!clear_channel #channel [limit]` - Delete messages in channel",
            inline=False
        )
    
    embed.add_field(
        name="⚙️ Configuration",
        value=f"• Code Posting: **{'Anyone with a role' if not ALLOWED_ROLE_NAME else ALLOWED_ROLE_NAME}**\n• Admin Roles: **{', '.join(ADMIN_ROLE_NAMES)}**",
        inline=False
    )
    
    embed.set_footer(text="Contact an admin if you need the appropriate role.")
    
    await ctx.send(embed=embed)

async def run_bot_with_recovery():
    """Run bot with enhanced error recovery and automatic restart"""
    max_restarts = 5
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            logger.info(f"Starting bot (attempt {restart_count + 1}/{max_restarts})")
            
            # Ensure warnings are saved before starting
            warning_system.save_warnings()
            
            await bot.start(TOKEN)
            
        except discord.LoginFailure:
            logger.critical("Invalid Discord token - cannot start bot")
            break
        except discord.ConnectionClosed:
            logger.error("Discord connection closed - attempting restart")
        except discord.HTTPException as e:
            logger.error(f"Discord HTTP error: {e} - attempting restart")
        except Exception as e:
            logger.error(f"Unexpected error: {e} - attempting restart", exc_info=True)
        
        # Save warnings before restart
        try:
            warning_system.save_warnings()
            logger.info("Saved warnings before restart")
        except Exception as e:
            logger.error(f"Failed to save warnings before restart: {e}")
        
        restart_count += 1
        if restart_count < max_restarts:
            delay = min(30, 5 * restart_count)  # Exponential backoff, max 30 seconds
            logger.info(f"Restarting in {delay} seconds... (attempt {restart_count + 1}/{max_restarts})")
            await asyncio.sleep(delay)
        else:
            logger.critical(f"Maximum restart attempts ({max_restarts}) reached - stopping bot")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: Discord token not found. Please check your .env file.")
    else:
        # Run with enhanced error recovery
        asyncio.run(run_bot_with_recovery())