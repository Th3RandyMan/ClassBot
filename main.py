#!/usr/bin/env python3
"""
Class Bot - Discord Bot for Code Monitoring
Main entry point with organized module structure
"""

import discord
from discord.ext import commands
import os
import logging
import asyncio
import sys
from dotenv import load_dotenv

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.warning_system import PersistentWarningSystem
from bot.error_recovery import ErrorRecoverySystem, run_bot_with_recovery
from bot.utils.code_detection import CodeDetector

# Import configuration
import os
import platform
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration from environment
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
ALLOWED_ROLE_NAME = os.getenv('ALLOWED_ROLE_NAME')
ADMIN_ROLE_NAMES = [name.strip() for name in os.getenv('ADMIN_ROLE_NAMES', 'Professor,Teaching Assistant (TA)').split(',')]
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID')) if os.getenv('LOG_CHANNEL_ID') else None

# Load environment variables
load_dotenv()

# Configure logging for cloud deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/bot.log')
    ]
)

logger = logging.getLogger(__name__)

# Get Discord token
TOKEN = os.getenv('DISCORD_TOKEN')

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize systems
warning_system = PersistentWarningSystem()
code_detector = CodeDetector()
error_recovery = ErrorRecoverySystem(bot, warning_system)


class ClassBot:
    """Main bot functionality class"""
    
    def __init__(self):
        self.bot = bot
        
    def has_allowed_role(self, member):
        """Check if member has any role (anyone with a role can post code)"""
        if ALLOWED_ROLE_NAME:
            return any(role.name == ALLOWED_ROLE_NAME for role in member.roles)
        else:
            # If no specific role is set, anyone with any role (except @everyone) can post
            return len(member.roles) > 1
    
    def has_admin_role(self, member):
        """Check if member has admin role"""
        return any(role.name in ADMIN_ROLE_NAMES for role in member.roles)
    
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


# Initialize the main bot class
class_bot = ClassBot()


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

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f'{bot.user} has landed! Class Bot is now monitoring for code.')
    print(f'Class Bot is ready! Logged in as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully"""
    if isinstance(error, commands.CommandNotFound):
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
        logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)
        await ctx.send("❌ An unexpected error occurred. The issue has been logged.")
        try:
            warning_system.save_warnings()
        except:
            pass

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    if message.author.bot:
        return
    
    await bot.process_commands(message)
    
    if class_bot.has_allowed_role(message.author):
        return
    
    code_detected = False
    reason = ""
    
    if message.content and code_detector.detect_code_in_text(message.content):
        code_detected = True
        reason = "Code detected in text message"
    
    if message.attachments and not code_detected:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                image_result = await code_detector.detect_code_in_image(attachment.url)
                
                if image_result is True:
                    code_detected = True
                    reason = "Code detected in uploaded image"
                    break
                elif image_result is None:
                    await class_bot.warn_user_about_image(message.author, message.channel)
                    code_detected = True
                    reason = "Image posted when OCR unavailable - cannot verify content"
                    break
    
    if code_detected:
        try:
            await message.delete()
            await class_bot.warn_user(message.author, message.channel, reason)
        except discord.errors.NotFound:
            pass
        except discord.errors.Forbidden:
            logger.warning("Bot lacks permission to delete messages")


# Import and setup all commands - temporarily simplified
# TODO: Move to separate commands module

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

@bot.command(name='help_classbot')
async def help_command(ctx):
    """Show help information about Class Bot"""
    
    embed = discord.Embed(
        title="🤖 Class Bot Help",
        description="I monitor messages for code and help maintain server order.",
        color=0x0099ff
    )
    
    embed.add_field(
        name="🎯 What I Do",
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


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: Discord token not found. Please check your .env file.")
    else:
        asyncio.run(run_bot_with_recovery(bot, TOKEN, warning_system))