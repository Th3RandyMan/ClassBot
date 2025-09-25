#!/usr/bin/env python3
"""
Class Bot - Discord Bot for Code Monitoring
Main entry point with organized module structure
"""

import discord
from discord.ext import commands
import sys
import os
import logging
import asyncio

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import configuration and setup
from config import BotConfig

# Initialize configuration and logging
BotConfig.setup_logging()
logger = logging.getLogger(__name__)

# Import bot modules
from bot.warning_system import PersistentWarningSystem
from bot.error_recovery import ErrorRecoverySystem, run_bot_with_recovery
from bot.utils.code_detection import CodeDetector
from bot.username_filter import UsernameFilter
from bot.bot_controller import bot_controller
from bot.error_handlers import ErrorHandlers
from bot.events import BotEvents
from bot.commands import BotCommands

# Import assignment system
from bot.assignment_manager import AssignmentManager
from bot.assignment_commands import AssignmentCommands
from bot.assignment_reminder_system import AssignmentReminderSystem

class ClassBot:
    """Main bot functionality class"""
    
    def __init__(self, bot=None, warning_system=None):
        self.bot = bot
        self.warning_system = warning_system
        
    def has_allowed_role(self, member):
        """Check if member has allowed role"""
        if not BotConfig.ALLOWED_ROLE_NAME:
            # If no specific role required, anyone with any role can post
            return len(member.roles) > 1  # More than just @everyone
        return any(role.name == BotConfig.ALLOWED_ROLE_NAME for role in member.roles)
    
    def has_admin_role(self, member):
        """Check if member has admin role"""
        return any(role.name in BotConfig.ADMIN_ROLE_NAMES for role in member.roles)
    
    async def warn_user(self, member, channel, reason):
        """Warn a user for posting code without permission"""
        try:
            # Get warning count
            warning_count = self.warning_system.get_warnings(member.id)
            warning_count += 1
            self.warning_system.add_warning(member.id, reason)
            
            # Create warning embed
            embed = discord.Embed(
                title="⚠️ Code Detected!",
                color=0xff9900
            )
            
            embed.description = f"{member.mention}, you are not allowed to post code without the appropriate role."
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Warning", value=f"This is warning #{warning_count}", inline=True)
            
            if BotConfig.ALLOWED_ROLE_NAME:
                embed.add_field(name="Required Role", value=BotConfig.ALLOWED_ROLE_NAME, inline=True)
            else:
                embed.add_field(name="Required", value="Any role", inline=True)
            
            embed.set_footer(text="Contact an admin if you believe this is a mistake.")
            
            await channel.send(embed=embed)
            
            # Log warning
            logger.info(f"Warned user {member.display_name} (#{warning_count}): {reason}")
            
        except Exception as e:
            logger.error(f"Error warning user: {e}")
            # Fallback to simple message
            await channel.send(f"⚠️ {member.mention} Code detected! You need the appropriate role to post code. Warning #{warning_count}")
    
    async def warn_user_about_image(self, member, channel):
        """Warn user about posting image when OCR is unavailable"""
        try:
            embed = discord.Embed(
                title="🖼️ Image Posted - OCR Unavailable",
                description=f"{member.mention}, I cannot verify the content of images right now.",
                color=0xffaa00
            )
            embed.add_field(
                name="Action Required",
                value="Please ensure your image doesn't contain code, or delete it and post as text instead.",
                inline=False
            )
            embed.add_field(
                name="Note",
                value="Images are not allowed when OCR system is unavailable for security.",
                inline=False
            )
            
            await channel.send(embed=embed)
            logger.info(f"Image warning sent to {member.display_name} - OCR unavailable")
            
            # Send to log channel
            if BotConfig.LOG_CHANNEL_ID:
                try:
                    log_channel = self.bot.get_channel(BotConfig.LOG_CHANNEL_ID)
                    if log_channel and channel.id != BotConfig.LOG_CHANNEL_ID:
                        log_embed = discord.Embed(
                            title="🖼️ Image Posted - OCR Unavailable",
                            description=f"User {member.mention} posted image in {channel.mention}",
                            color=0xffaa00
                        )
                        log_embed.add_field(name="User", value=member.mention, inline=True)
                        log_embed.add_field(name="Channel", value=channel.mention, inline=True)
                        log_embed.add_field(name="Issue", value="Image posted when OCR unavailable", inline=False)
                        await log_channel.send(embed=log_embed)
                except Exception as e:
                    logger.error(f"Failed to send image warning to log channel: {e}")
                    
        except Exception as e:
            logger.error(f"Error in warn_user_about_image: {e}")

def main():
    """Main bot initialization and startup"""
    
    # Validate configuration
    config_errors = BotConfig.validate_config()
    if config_errors:
        logger.error("Configuration errors found:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # Configure bot intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    # Create bot instance
    bot = commands.Bot(
        command_prefix=BotConfig.COMMAND_PREFIX, 
        intents=intents, 
        help_command=None
    )

    # Initialize systems
    warning_system = PersistentWarningSystem()
    code_detector = CodeDetector()
    error_recovery = ErrorRecoverySystem(bot, warning_system)
    username_filter = UsernameFilter()
    
    # Initialize main bot class
    class_bot = ClassBot(bot, warning_system)

    # Initialize assignment system
    assignment_manager = AssignmentManager()
    assignment_commands = AssignmentCommands(bot, assignment_manager, BotConfig.ADMIN_ROLE_NAMES)
    assignment_reminder_system = AssignmentReminderSystem(bot, assignment_manager)

    # Initialize and setup error handlers
    error_handlers = ErrorHandlers(bot, class_bot, BotConfig.LOG_CHANNEL_ID)
    
    # Initialize and setup event handlers
    bot_events = BotEvents(
        bot, class_bot, code_detector, username_filter, 
        assignment_reminder_system, bot_controller, warning_system, error_recovery
    )
    
    # Initialize and setup commands
    bot_commands = BotCommands(
        bot, class_bot, username_filter, bot_controller, 
        assignment_commands, BotConfig.ADMIN_ROLE_NAMES, BotConfig.LOG_CHANNEL_ID
    )

    logger.info("Bot initialization complete")
    
    # Start the bot with error recovery
    return run_bot_with_recovery(bot, BotConfig.TOKEN, warning_system)

if __name__ == "__main__":
    if not BotConfig.TOKEN:
        print("ERROR: Discord token not found. Please check your .env file.")
        sys.exit(1)
    else:
        asyncio.run(main())