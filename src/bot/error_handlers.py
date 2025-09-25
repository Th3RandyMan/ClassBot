"""
Error handling module for the Discord bot
Contains error handlers for commands and general bot errors
"""

import discord
from discord.ext import commands
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlers:
    """Class containing all error handling functionality"""
    
    def __init__(self, bot, class_bot, log_channel_id=None):
        self.bot = bot
        self.class_bot = class_bot
        self.log_channel_id = log_channel_id
        self.setup_handlers()
    
    def setup_handlers(self):
        """Register error handlers with the bot"""
        self.bot.add_listener(self.on_command_error, 'on_command_error')
        self.bot.add_listener(self.on_error, 'on_error')
    
    async def on_command_error(self, ctx, error):
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
            if self.class_bot.has_admin_role(ctx.author):
                error_details = str(error)[:1000]  # Limit length
                embed.add_field(name="Error Details (Admin Only)", value=f"```\n{error_details}\n```", inline=False)
            
            await ctx.send(embed=embed)
            
            # Log the full error for debugging
            logger.error(f"Command error in {ctx.command}: {error}", exc_info=True)
            
            # Send to log channel if configured
            if self.log_channel_id:
                try:
                    log_channel = self.bot.get_channel(self.log_channel_id)
                    if log_channel and ctx.channel.id != self.log_channel_id:
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

    async def on_error(self, event, *args, **kwargs):
        """Handle general bot errors"""
        error_msg = traceback.format_exc()
        logger.error(f"Error in event {event}: {error_msg}")
        
        # Send critical errors to log channel if configured
        if self.log_channel_id:
            try:
                log_channel = self.bot.get_channel(self.log_channel_id)
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