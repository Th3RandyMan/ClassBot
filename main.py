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

# Configure logging for immediate output with proper encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', mode='a', encoding='utf-8')
    ],
    force=True  # Override any existing loggers
)

# Ensure stdout/stderr use UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

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

# Global error handlers
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully"""
    
    # Ignore command not found errors (less spam)
    if isinstance(error, commands.CommandNotFound):
        return
    
    # Handle specific error types with user-friendly messages
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permission Error",
            description="You don't have permission to use this command.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="❌ Bot Permission Error",
            description="I don't have the necessary permissions to execute this command.",
            color=0xff0000
        )
        missing_perms = ", ".join(error.missing_permissions)
        embed.add_field(name="Missing Permissions", value=missing_perms, inline=False)
        await ctx.send(embed=embed)
        
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: `{error.param.name}`",
            color=0xff0000
        )
        embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`", inline=False)
        await ctx.send(embed=embed)
        
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description="One or more arguments are invalid.",
            color=0xff0000
        )
        embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`", inline=False)
        embed.add_field(name="Error Details", value=str(error), inline=False)
        await ctx.send(embed=embed)
        
    elif isinstance(error, commands.ChannelNotFound):
        embed = discord.Embed(
            title="❌ Channel Not Found",
            description="Could not find the specified channel.",
            color=0xff0000
        )
        embed.add_field(name="Tip", value="Make sure to use #channel-name or verify the channel exists.", inline=False)
        await ctx.send(embed=embed)
        
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ User Not Found",
            description="Could not find the specified user.",
            color=0xff0000
        )
        embed.add_field(name="Tip", value="Make sure to use @username or verify the user is in this server.", inline=False)
        await ctx.send(embed=embed)
        
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        
    else:
        # Handle unexpected errors
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="Something went wrong while executing this command.",
            color=0xff0000
        )
        
        # Add error details for admins
        if class_bot.has_admin_role(ctx.author):
            error_details = str(error)[:1000]  # Limit length
            embed.add_field(name="Error Details (Admin Only)", value=f"```\n{error_details}\n```", inline=False)
        
        await ctx.send(embed=embed)
        
        # Log the full error for debugging
        logger.error(f"Command error in {ctx.command}: {error}", exc_info=True)
        
        # Send to log channel if configured
        if LOG_CHANNEL_ID:
            try:
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel and ctx.channel.id != LOG_CHANNEL_ID:
                    error_embed = discord.Embed(
                        title="🚨 Command Error",
                        description=f"Error in command `{ctx.command}` by {ctx.author.mention}",
                        color=0xff0000
                    )
                    error_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                    error_embed.add_field(name="Command", value=f"`{ctx.message.content}`", inline=False)
                    error_embed.add_field(name="Error", value=f"```\n{str(error)[:500]}\n```", inline=False)
                    await log_channel.send(embed=error_embed)
            except Exception as log_error:
                logger.error(f"Failed to send error log: {log_error}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle general bot errors"""
    import traceback
    error_msg = traceback.format_exc()
    logger.error(f"Bot error in event {event}: {error_msg}")
    
    # Send to log channel if configured
    if LOG_CHANNEL_ID:
        try:
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                error_embed = discord.Embed(
                    title="🚨 Bot Error",
                    description=f"Error in event: `{event}`",
                    color=0xff0000
                )
                error_embed.add_field(name="Error", value=f"```\n{error_msg[:1000]}\n```", inline=False)
                await log_channel.send(embed=error_embed)
        except Exception as log_error:
            logger.error(f"Failed to send error log: {log_error}")


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
        await interaction.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
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

@bot.command(name='classbot')
async def classbot_hello(ctx):
    """Friendly greeting command"""
    
    # Create a friendly greeting embed
    embed = discord.Embed(
        title="👋 Hello!",
        description=f"Hello {ctx.author.display_name}! 🤖",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🎯 What I Do",
        value="I'm your friendly Class Bot! I help monitor code and keep the server organized.",
        inline=False
    )
    
    embed.add_field(
        name="💡 Need Help?",
        value="Use `!help_classbot` to see all my commands and features!",
        inline=False
    )
    
    # Add a fun fact or status
    guild_member_count = len(ctx.guild.members) if ctx.guild else "unknown"
    embed.add_field(
        name="📊 Server Stats",
        value=f"Watching over {guild_member_count} members in this server!",
        inline=False
    )
    
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='remove_roleless')
async def remove_roleless_users(ctx):
    """Remove all users without any role (Admin only)"""
    
    # Check if user has admin role
    if not class_bot.has_admin_role(ctx.author):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    # Get all members without roles (excluding @everyone)
    roleless_members = []
    excluded_members = []
    
    for member in ctx.guild.members:
        if len(member.roles) == 1 and member.roles[0].name == "@everyone":
            # Exclude all bots (including ClassBot)
            if member.bot:
                excluded_members.append(f"🤖 {member.display_name} (bot)")
                continue
            # Extra safety: Don't include the bot itself
            if member.id == bot.user.id:
                excluded_members.append(f"🤖 {member.display_name} (ClassBot)")
                continue
            # Don't include server owner for safety
            if member.id == ctx.guild.owner_id:
                excluded_members.append(f"👑 {member.display_name} (server owner)")
                continue
            
            roleless_members.append(member)
    
    # Log exclusions for transparency
    if excluded_members:
        logger.info(f"remove_roleless excluded {len(excluded_members)} members: {', '.join(excluded_members)}")
    
    if not roleless_members:
        if excluded_members:
            embed = discord.Embed(
                title="ℹ️ No Eligible Users Found",
                description="No users without roles found to remove.",
                color=0x0099ff
            )
            embed.add_field(
                name="🛡️ Protected Users Excluded",
                value=f"Found {len(excluded_members)} protected users (bots, server owner) that were automatically excluded.",
                inline=False
            )
            await ctx.send(embed=embed)
        else:
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
    
    # Add information about excluded members for transparency
    if excluded_members:
        excluded_info = f"🛡️ **{len(excluded_members)} protected users excluded** (bots, server owner)"
        embed.add_field(name="Protected Users:", value=excluded_info, inline=False)
    
    embed.set_footer(text="This action cannot be undone! Bots and server owner are automatically protected.")
    
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
            failure_list = "\n".join(failed_removals[:5])
            if len(failed_removals) > 5:
                failure_list += f"\n... and {len(failed_removals) - 5} more"
            result_embed.add_field(name="Failed Removals", value=failure_list, inline=False)
        
        await message.edit(embed=result_embed, view=None)
        
        # Log the action
        logger.info(f"Mass removal completed by {ctx.author.name}: {removed_count} removed, {len(failed_removals)} failed")
        
        # Send to log channel if configured
        if LOG_CHANNEL_ID:
            try:
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = discord.Embed(
                        title="🚨 Mass User Removal",
                        description=f"Admin {ctx.author.mention} removed {removed_count} roleless users",
                        color=0xff0000
                    )
                    log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                    log_embed.add_field(name="Total Removed", value=str(removed_count), inline=True)
                    log_embed.add_field(name="Failed", value=str(len(failed_removals)), inline=True)
                    await log_channel.send(embed=log_embed)
            except Exception as e:
                logger.error(f"Failed to send log message: {e}")
    else:
        # User cancelled
        await message.edit(content="❌ Operation cancelled by user.", embed=None, view=None)

@bot.command(name='clear_channel')
async def clear_channel_messages(ctx, channel: discord.TextChannel = None, limit: int = None):
    """Clear all messages from a specified channel (Admin only)"""
    
    if not class_bot.has_admin_role(ctx.author):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    # If no channel provided, show usage
    if channel is None:
        await ctx.send("❌ Please specify a channel. Usage: `!clear_channel #channel [limit]`")
        return
    
    # Create confirmation embed
    if limit is None:
        embed = discord.Embed(
            title="⚠️ Clear Channel Confirmation",
            description=f"Are you sure you want to **delete ALL messages** from {channel.mention}?",
            color=0xff0000
        )
        
        embed.add_field(
            name="⚠️ Warning", 
            value="This will delete **ALL messages** in the channel!\nThis action **cannot be undone**!",
            inline=False
        )
        embed.add_field(
            name="Channel Info",
            value=f"**Channel:** {channel.mention}\n**Requested by:** {ctx.author.mention}",
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
            description=f"Are you sure you want to delete the **last {limit} messages** from {channel.mention}?",
            color=0xff9900
        )
        
        embed.add_field(
            name="Action Details",
            value=f"**Channel:** {channel.mention}\n**Messages to delete:** {limit}\n**Requested by:** {ctx.author.mention}",
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
                title="🔄 Clearing messages...",
                description=f"{'Deleting all messages' if limit is None else f'Deleting last {limit} messages'} from {channel.mention}...",
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
                        progress_embed.description = f"Deleted {deleted_count} messages from {channel.mention}... (continuing)"
                        try:
                            await confirmation_msg.edit(embed=progress_embed)
                        except:
                            pass  # Continue even if edit fails
            else:
                # Delete specific number of messages
                deleted = await channel.purge(limit=limit, bulk=True)
                deleted_count = len(deleted)
            
            # Send completion message
            result_embed = discord.Embed(
                title="✅ Channel Cleared Successfully",
                description=f"Deleted **{deleted_count} messages** from {channel.mention}",
                color=0x00ff00
            )
            result_embed.add_field(name="Cleared by", value=ctx.author.mention, inline=True)
            result_embed.add_field(name="Channel", value=channel.mention, inline=True)
            await confirmation_msg.edit(embed=result_embed, view=None)
            
            # Log the action
            logger.info(f"Channel cleared by {ctx.author.name}: {deleted_count} messages from #{channel.name}")
            
            # Send to log channel if configured
            if LOG_CHANNEL_ID and ctx.channel.id != LOG_CHANNEL_ID:
                try:
                    log_channel = bot.get_channel(LOG_CHANNEL_ID)
                    if log_channel:
                        log_embed = discord.Embed(
                            title="🧹 Channel Cleared",
                            description=f"Admin {ctx.author.mention} cleared {deleted_count} messages from {channel.mention}",
                            color=0xff9900
                        )
                        await log_channel.send(embed=log_embed)
                except Exception as e:
                    logger.error(f"Failed to send log message: {e}")
                    
        except discord.errors.Forbidden:
            await confirmation_msg.edit(
                content="❌ I don't have permission to delete messages in that channel.",
                embed=None, view=None
            )
        except Exception as e:
            await confirmation_msg.edit(
                content=f"❌ An error occurred while clearing messages: {str(e)}",
                embed=None, view=None
            )
            logger.error(f"Error clearing channel: {e}")
    else:
        # User cancelled
        await confirmation_msg.edit(content="❌ Channel clearing cancelled by user.", embed=None, view=None)


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: Discord token not found. Please check your .env file.")
    else:
        asyncio.run(run_bot_with_recovery(bot, TOKEN, warning_system))