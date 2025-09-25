"""
Bot events module for the Discord bot
Contains all bot event handlers
"""

import discord
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BotEvents:
    """Class containing all bot event handlers"""
    
    def __init__(self, bot, class_bot, code_detector, username_filter, assignment_reminder_system, bot_controller, warning_system, error_recovery):
        self.bot = bot
        self.class_bot = class_bot
        self.code_detector = code_detector
        self.username_filter = username_filter
        self.assignment_reminder_system = assignment_reminder_system
        self.bot_controller = bot_controller
        self.warning_system = warning_system
        self.error_recovery = error_recovery
        self.setup_events()
    
    def setup_events(self):
        """Register event handlers with the bot"""
        self.bot.add_listener(self.on_ready, 'on_ready')
        self.bot.add_listener(self.on_message, 'on_message')
        self.bot.add_listener(self.on_member_join, 'on_member_join')
        self.bot.add_listener(self.on_disconnect, 'on_disconnect')
        self.bot.add_listener(self.on_resumed, 'on_resumed')
        self.bot.add_listener(self.on_connect, 'on_connect')
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.bot.user} has landed! Class Bot is now monitoring for code.')
        print(f'Class Bot is ready! Logged in as {self.bot.user}')
        
        # Start assignment reminder system
        self.assignment_reminder_system.start_reminder_system()
        logger.info("Assignment reminder system started")

    async def on_disconnect(self):
        """Handle bot disconnection"""
        logger.warning("Bot disconnected from Discord")
        await self.error_recovery.handle_connection_error("Discord disconnection")

    async def on_resumed(self):
        """Handle bot reconnection"""
        logger.info("Bot resumed connection to Discord")
        self.error_recovery.reset_reconnect_counter()

    async def on_connect(self):
        """Handle successful bot connection"""
        logger.info("Bot connected to Discord")
        self.error_recovery.reset_reconnect_counter()

    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author.bot:
            return
        
        # Check if message is a command and if bot is enabled
        if message.content.startswith('!'):
            command_name = message.content[1:].split()[0]  # Extract command name
            if not self.bot_controller.can_execute_command(command_name):
                # Bot is disabled and command is not allowed
                status = self.bot_controller.get_status()
                embed = discord.Embed(
                    title="🤖 Bot Temporarily Disabled",
                    color=0xffaa00
                )
                
                if status["maintenance_mode"]:
                    embed.description = "The bot is currently in maintenance mode."
                else:
                    embed.description = "The bot is currently disabled."
                
                if status["disabled_reason"]:
                    embed.add_field(name="Reason", value=status["disabled_reason"], inline=False)
                
                if status["disabled_by"]:
                    embed.add_field(name="Disabled By", value=status["disabled_by"], inline=True)
                
                if status.get("remaining_minutes") and status["remaining_minutes"] > 0:
                    embed.add_field(name="Re-enabled In", value=f"{status['remaining_minutes']} minutes", inline=True)
                elif status["disabled_until"]:
                    embed.add_field(name="Status", value="Temporarily disabled", inline=True)
                else:
                    embed.add_field(name="Status", value="Indefinitely disabled", inline=True)
                
                embed.add_field(
                    name="Available Commands", 
                    value="`!bot_status`, `!bot_enable`, `!help`", 
                    inline=False
                )
                
                await message.channel.send(embed=embed)
                return
        
        await self.bot.process_commands(message)
        
        if self.class_bot.has_allowed_role(message.author):
            return
        
        code_detected = False
        reason = ""
        
        if message.content and self.code_detector.detect_code_in_text(message.content):
            code_detected = True
            reason = "Code detected in text message"
        
        if message.attachments and not code_detected:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    image_result = await self.code_detector.detect_code_in_image(attachment.url)
                    
                    if image_result is True:
                        code_detected = True
                        reason = "Code detected in uploaded image"
                        break
                    elif image_result is None:
                        await self.class_bot.warn_user_about_image(message.author, message.channel)
                        code_detected = True
                        reason = "Image posted when OCR unavailable - cannot verify content"
                        break
        
        if code_detected:
            try:
                await message.delete()
                await self.class_bot.warn_user(message.author, message.channel, reason)
            except discord.errors.NotFound:
                pass
            except discord.errors.Forbidden:
                logger.warning("Bot lacks permission to delete messages")

    async def on_member_join(self, member):
        """Check new members for inappropriate usernames and take action if needed."""
        try:
            # Skip bots
            if member.bot:
                return
            
            logger.info(f"New member joined: {member.display_name} ({member.name})")
            
            # Check both display name and username
            display_inappropriate, display_details = self.username_filter.check_username(member.display_name, member.id)
            user_inappropriate, user_details = self.username_filter.check_username(member.name, member.id)
            
            if display_inappropriate or user_inappropriate:
                # Determine the highest confidence and details
                if display_inappropriate and user_inappropriate:
                    details = display_details if display_details['confidence'] > user_details['confidence'] else user_details
                    flagged_name = member.display_name if display_details['confidence'] > user_details['confidence'] else member.name
                elif display_inappropriate:
                    details = display_details
                    flagged_name = member.display_name
                else:
                    details = user_details
                    flagged_name = member.name
                
                confidence = details['confidence']
                action = self.username_filter.config.get('action_on_detection', 'warn')
                
                logger.warning(f"Inappropriate username detected for new member: {member.display_name} ({member.name}) - Confidence: {confidence:.2f}")
                
                # Create admin notification embed
                admin_embed = discord.Embed(
                    title="🚨 Inappropriate Username Detected",
                    color=0xff6600
                )
                admin_embed.add_field(name="User", value=f"{member.mention} ({member.display_name})", inline=False)
                admin_embed.add_field(name="Flagged Name", value=flagged_name, inline=True)
                admin_embed.add_field(name="Confidence", value=f"{confidence:.2f}", inline=True)
                admin_embed.add_field(name="Action", value=action.title(), inline=True)
                
                if details.get('matches'):
                    match_info = []
                    for match_type, word in details['matches'][:3]:  # Show first 3 matches
                        match_info.append(f"• {match_type}: {word}")
                    admin_embed.add_field(name="Matches", value="\n".join(match_info), inline=False)
                
                # Find admin channels or general channel for notification
                notification_channel = None
                
                # Try to find a mod/admin channel first
                for channel in member.guild.text_channels:
                    if any(word in channel.name.lower() for word in ['mod', 'admin', 'staff', 'log']):
                        if channel.permissions_for(member.guild.me).send_messages:
                            notification_channel = channel
                            break
                
                # Fallback to general channel or first available channel
                if not notification_channel:
                    for channel in member.guild.text_channels:
                        if channel.permissions_for(member.guild.me).send_messages:
                            notification_channel = channel
                            break
                
                # Perform action based on configuration
                if action.lower() == "kick" and confidence >= 0.7:
                    try:
                        # Send DM before kicking
                        dm_embed = discord.Embed(
                            title="❌ Removed from Server",
                            description=f"You have been removed from {member.guild.name} due to an inappropriate username.",
                            color=0xff0000
                        )
                        dm_embed.add_field(
                            name="Flagged Name",
                            value=flagged_name,
                            inline=False
                        )
                        dm_embed.add_field(
                            name="What to do",
                            value="You can rejoin with a more appropriate username.",
                            inline=False
                        )
                        
                        try:
                            await member.send(embed=dm_embed)
                        except:
                            pass  # DM failed, continue with kick
                        
                        await member.kick(reason=f"Inappropriate username detected: {flagged_name} (confidence: {confidence:.2f})")
                        
                        admin_embed.add_field(name="Result", value="✅ User kicked", inline=False)
                        logger.info(f"Kicked new member {member.display_name} for inappropriate username")
                        
                    except Exception as e:
                        admin_embed.add_field(name="Result", value=f"❌ Failed to kick: {str(e)}", inline=False)
                        logger.error(f"Failed to kick member {member.display_name}: {e}")
                        
                elif action.lower() == "warn":
                    try:
                        # Send warning DM
                        dm_embed = discord.Embed(
                            title="⚠️ Username Policy Reminder",
                            description=f"Welcome to {member.guild.name}! Your username has been flagged as potentially inappropriate.",
                            color=0xffaa00
                        )
                        dm_embed.add_field(
                            name="Flagged Name", 
                            value=flagged_name,
                            inline=False
                        )
                        dm_embed.add_field(
                            name="Action Required",
                            value="Please consider changing your display name to something more appropriate for this academic server.",
                            inline=False
                        )
                        dm_embed.add_field(
                            name="How to change",
                            value="Right-click your name in the server and select 'Edit Server Profile'",
                            inline=False
                        )
                        
                        await member.send(embed=dm_embed)
                        admin_embed.add_field(name="Result", value="✅ Warning sent", inline=False)
                        logger.info(f"Warned new member {member.display_name} about inappropriate username")
                        
                    except Exception as e:
                        admin_embed.add_field(name="Result", value=f"❌ Failed to warn: {str(e)}", inline=False)
                        logger.error(f"Failed to warn member {member.display_name}: {e}")
                
                # Send admin notification
                if notification_channel:
                    await notification_channel.send(embed=admin_embed)
                    
        except Exception as e:
            logger.error(f"Error in on_member_join username check: {e}")