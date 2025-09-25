#!/usr/bin/env python3
"""
Assignment Reminder System - Background task for sending automated reminders.
"""

import discord
from discord.ext import tasks
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AssignmentReminderSystem:
    """Background system for sending automated assignment reminders."""
    
    def __init__(self, bot, assignment_manager):
        self.bot = bot
        self.assignment_manager = assignment_manager
        self.reminder_task = None
        
    def start_reminder_system(self):
        """Start the background reminder system."""
        if not self.reminder_task or self.reminder_task.is_being_cancelled():
            self.reminder_task = self.check_reminders.start()
            logger.info("Assignment reminder system started")
        
    def stop_reminder_system(self):
        """Stop the background reminder system."""
        if self.reminder_task and not self.reminder_task.is_being_cancelled():
            self.reminder_task.cancel()
            logger.info("Assignment reminder system stopped")
    
    @tasks.loop(minutes=15)  # Check every 15 minutes
    async def check_reminders(self):
        """Check for pending reminders and send them."""
        try:
            pending_reminders = self.assignment_manager.get_pending_reminders()
            
            if not pending_reminders:
                return
            
            reminder_channel_id = self.assignment_manager.get_reminder_channel_id()
            if not reminder_channel_id:
                logger.warning("No reminder channel set - skipping reminders")
                return
            
            channel = self.bot.get_channel(reminder_channel_id)
            if not channel:
                logger.error(f"Reminder channel {reminder_channel_id} not found")
                return
            
            for assignment_id, reminder_data in pending_reminders:
                await self._send_reminder(channel, assignment_id, reminder_data)
                
                # Mark reminder as sent
                self.assignment_manager.mark_reminder_sent(
                    assignment_id, 
                    reminder_data["reminder"]["time"]
                )
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in reminder system: {e}")
    
    async def _send_reminder(self, channel: discord.TextChannel, assignment_id: str, reminder_data: dict):
        """Send a reminder message to the channel."""
        try:
            assignment = reminder_data["assignment"]
            reminder = reminder_data["reminder"]
            
            due_date = datetime.fromisoformat(assignment["due_date"])
            current_time = datetime.now()
            time_until_due = due_date - current_time
            
            # Create urgency-based styling
            if time_until_due.total_seconds() <= 7200:  # 2 hours or less
                title = "🚨 URGENT: Assignment Due Very Soon!"
                color = 0xff0000  # Red
                urgency_emoji = "🚨"
            elif time_until_due.days <= 1:  # 1 day or less
                title = "⚠️ Assignment Due Tomorrow!"
                color = 0xff8800  # Orange
                urgency_emoji = "⚠️"
            elif time_until_due.days <= 3:  # 3 days or less
                title = "📅 Assignment Due This Week"
                color = 0xffaa00  # Yellow
                urgency_emoji = "📅"
            else:  # More than 3 days
                title = "📋 Assignment Reminder"
                color = 0x0099ff  # Blue
                urgency_emoji = "📋"
            
            embed = discord.Embed(
                title=title,
                description=f"**{assignment['name']}**",
                color=color
            )
            
            # Format time remaining
            if time_until_due.days > 0:
                if time_until_due.days == 1:
                    time_str = "tomorrow"
                else:
                    time_str = f"in {time_until_due.days} days"
            elif time_until_due.seconds > 3600:
                hours = time_until_due.seconds // 3600
                time_str = f"in {hours} hour{'s' if hours > 1 else ''}"
            else:
                minutes = max(1, time_until_due.seconds // 60)
                time_str = f"in {minutes} minute{'s' if minutes > 1 else ''}"
            
            embed.add_field(
                name="📝 Description",
                value=assignment["description"],
                inline=False
            )
            
            embed.add_field(
                name="⏰ Due Date",
                value=f"<t:{int(due_date.timestamp())}:F>",
                inline=True
            )
            
            embed.add_field(
                name="⌛ Time Remaining",
                value=f"Due **{time_str}**",
                inline=True
            )
            
            # Add helpful tips based on time remaining
            if time_until_due.total_seconds() <= 7200:  # 2 hours
                tips = "💡 **Last minute tips:**\n• Double-check your work\n• Make sure to submit on time\n• Ask for help if needed!"
            elif time_until_due.days <= 1:  # 1 day
                tips = "💡 **Final day reminders:**\n• Review the requirements\n• Start early if you haven't\n• Visit office hours if stuck"
            else:
                tips = "💡 **Stay on track:**\n• Plan your approach\n• Break it into smaller tasks\n• Don't wait until the last minute!"
            
            embed.add_field(name="💪 Tips", value=tips, inline=False)
            
            # Add footer with Discord event info
            embed.set_footer(
                text="💡 Check the Events tab for more details and to get Discord notifications!",
                icon_url="https://cdn.discordapp.com/emojis/📅.png"
            )
            
            # Send the reminder
            await channel.send(
                content=f"{urgency_emoji} **Assignment Reminder** {urgency_emoji}",
                embed=embed
            )
            
            logger.info(f"Sent reminder for assignment '{assignment['name']}' (due {reminder['description']} before)")
            
        except Exception as e:
            logger.error(f"Error sending reminder for assignment {assignment_id}: {e}")
    
    @check_reminders.before_loop
    async def before_reminder_check(self):
        """Wait for bot to be ready before starting reminder checks."""
        await self.bot.wait_until_ready()
        logger.info("Assignment reminder system is ready")
    
    @check_reminders.error
    async def reminder_error(self, exception):
        """Handle errors in the reminder loop."""
        logger.error(f"Error in assignment reminder loop: {exception}")
        # The task will automatically restart after an error
    
    async def send_test_reminder(self, channel: discord.TextChannel, assignment_name: str = "Test Assignment"):
        """Send a test reminder (for testing purposes)."""
        try:
            test_assignment = {
                "name": assignment_name,
                "description": "This is a test reminder to verify the reminder system is working properly.",
                "due_date": (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            test_reminder = {
                "assignment": test_assignment,
                "reminder": {
                    "time": datetime.now().isoformat(),
                    "description": "2 hours"
                }
            }
            
            await self._send_reminder(channel, "test", test_reminder)
            return True
            
        except Exception as e:
            logger.error(f"Error sending test reminder: {e}")
            return False