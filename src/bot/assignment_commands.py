#!/usr/bin/env python3
"""
Assignment Commands - Intuitive Discord commands for managing assignments and events.
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AssignmentCommands(commands.Cog):
    """Commands for managing assignments and Discord events."""
    
    def __init__(self, bot, assignment_manager, admin_role_names):
        self.bot = bot
        self.assignment_manager = assignment_manager
        self.admin_role_names = admin_role_names
    
    def _has_admin_role(self, user: discord.Member) -> bool:
        """Check if user has admin role."""
        return any(role.name in self.admin_role_names for role in user.roles)
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats into datetime object."""
        try:
            # Handle common date formats
            date_string = date_string.strip().lower()
            current_time = datetime.now()
            
            # Handle "tomorrow" and "today"
            if "tomorrow" in date_string:
                base_date = current_time + timedelta(days=1)
                time_part = date_string.replace("tomorrow", "").strip()
            elif "today" in date_string:
                base_date = current_time
                time_part = date_string.replace("today", "").strip()
            else:
                # Try to parse full date string
                base_date = current_time
                time_part = date_string
            
            # Extract time if present
            time_patterns = [
                r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 11:59pm, 2:30am
                r'(\d{1,2})\s*(am|pm)',          # 11pm, 2am
                r'(\d{1,2}):(\d{2})',            # 23:59, 14:30
            ]
            
            hour = 23
            minute = 59
            
            for pattern in time_patterns:
                match = re.search(pattern, time_part)
                if match:
                    if len(match.groups()) == 3:  # with am/pm
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        ampm = match.group(3)
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                    elif len(match.groups()) == 2 and ':' in match.group(0):  # 24-hour format
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                    else:  # just hour with am/pm
                        hour = int(match.group(1))
                        minute = 0
                        ampm = match.group(2)
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                    break
            
            # If we found "tomorrow" or "today", use that date
            if "tomorrow" in date_string or "today" in date_string:
                return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Try common date formats
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})',          # 12/15, 1/5
                r'(\w+)\s+(\d{1,2})',            # Jan 15, January 15
                r'(\d{1,2})\s+(\w+)',            # 15 Jan, 15 January
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_string)
                if match:
                    if '/' in match.group(0):
                        month = int(match.group(1))
                        day = int(match.group(2))
                        year = current_time.year
                        # If the date has passed this year, assume next year
                        test_date = datetime(year, month, day, hour, minute)
                        if test_date < current_time:
                            year += 1
                        return datetime(year, month, day, hour, minute)
                    else:
                        # Handle month names
                        months = {
                            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
                            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
                            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
                            'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
                            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
                            'dec': 12, 'december': 12
                        }
                        
                        month_str = match.group(1).lower() if match.group(1).isalpha() else match.group(2).lower()
                        day_str = match.group(2) if match.group(1).isalpha() else match.group(1)
                        
                        if month_str in months:
                            month = months[month_str]
                            day = int(day_str)
                            year = current_time.year
                            # If the date has passed this year, assume next year
                            test_date = datetime(year, month, day, hour, minute)
                            if test_date < current_time:
                                year += 1
                            return datetime(year, month, day, hour, minute)
            
            # If no date pattern found, assume it's for today or near future
            # Default to tomorrow at specified time if no date given
            return (current_time + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_string}': {e}")
            return None
    
    @commands.command(name='add_assignment', aliases=['new_assignment', 'assignment'])
    @commands.has_permissions(administrator=True)
    async def add_assignment(self, ctx, *, assignment_details: str):
        """
        Add a new assignment with Discord event and reminders.
        
        Usage examples:
        !add_assignment Homework 3 | Jan 15 11:59pm | Python loops assignment | 1d,2h
        !new_assignment Midterm Exam | Feb 20 2pm | Chapters 1-5 | 1w,3d,1d
        !assignment Quiz 2 | tomorrow 5pm | Variables and functions
        
        Format: NAME | DUE_DATE | DESCRIPTION | [REMINDERS]
        - NAME: Assignment name
        - DUE_DATE: When it's due (flexible formats like "Jan 15 11:59pm", "tomorrow 5pm", "next Friday")
        - DESCRIPTION: What the assignment is about
        - REMINDERS: Optional comma-separated list (1d=1day, 2h=2hours, 1w=1week, 30m=30minutes)
        """
        try:
            # Parse the assignment details
            parts = [part.strip() for part in assignment_details.split('|')]
            
            if len(parts) < 3:
                await ctx.send(embed=discord.Embed(
                    title="❌ Invalid Format",
                    description="Please use: `!add_assignment NAME | DUE_DATE | DESCRIPTION | [REMINDERS]`\n\n"
                               "**Examples:**\n"
                               "• `!add_assignment Homework 3 | Jan 15 11:59pm | Python loops assignment`\n"
                               "• `!assignment Quiz 2 | tomorrow 5pm | Variables and functions | 1d,2h`\n"
                               "• `!new_assignment Midterm | Feb 20 2pm | Chapters 1-5 | 1w,3d,1d`",
                    color=0xff0000
                ))
                return
            
            name = parts[0]
            due_date_str = parts[1]
            description = parts[2]
            reminder_schedule = None
            
            if len(parts) >= 4 and parts[3].strip():
                reminder_schedule = [r.strip() for r in parts[3].split(',')]
            
            # Parse the due date
            due_date = self._parse_date(due_date_str)
            if not due_date:
                await ctx.send(embed=discord.Embed(
                    title="❌ Invalid Date Format",
                    description=f"Couldn't understand date: '{due_date_str}'\n\n"
                               "**Try formats like:**\n"
                               "• `Jan 15 11:59pm`\n"
                               "• `tomorrow 5pm`\n"
                               "• `next Friday 2pm`\n"
                               "• `Feb 20 2:30pm`\n"
                               "• `12/15 11:59pm`",
                    color=0xff0000
                ))
                return
            
            # Create the assignment
            success, message = await self.assignment_manager.add_assignment(
                ctx.guild, name, due_date, description, reminder_schedule
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Assignment Added!",
                    description=message,
                    color=0x00ff00
                )
                embed.add_field(name="📚 Assignment", value=name, inline=True)
                embed.add_field(name="📅 Due Date", value=f"<t:{int(due_date.timestamp())}:F>", inline=True)
                embed.add_field(name="📝 Description", value=description, inline=False)
                
                if reminder_schedule:
                    embed.add_field(name="⏰ Reminders", value=", ".join(reminder_schedule) + " before due date", inline=False)
                
                embed.set_footer(text="Students can find this in the Events tab and get Discord notifications!")
                
            else:
                embed = discord.Embed(
                    title="❌ Error Adding Assignment",
                    description=message,
                    color=0xff0000
                )
            
            await ctx.send(embed=embed)
            
        except commands.MissingPermissions:
            await ctx.send(embed=discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can add assignments.",
                color=0xff0000
            ))
        except Exception as e:
            logger.error(f"Error in add_assignment command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))
    
    @commands.command(name='remove_assignment', aliases=['delete_assignment', 'del_assignment'])
    @commands.has_permissions(administrator=True)
    async def remove_assignment(self, ctx, *, assignment_name: str):
        """
        Remove an assignment and its Discord event.
        
        Usage:
        !remove_assignment Homework 3
        !delete_assignment Quiz
        !del_assignment Midterm
        
        You can use partial names - it will find the closest match.
        """
        try:
            success, message = await self.assignment_manager.remove_assignment(ctx.guild, assignment_name)
            
            if success:
                embed = discord.Embed(
                    title="✅ Assignment Removed",
                    description=message,
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description=message,
                    color=0xff0000
                )
                
                # Show available assignments if not found
                assignments = self.assignment_manager.list_assignments()
                if assignments:
                    assignment_list = "\n".join([f"• {a['name']}" for a in assignments[:5]])
                    embed.add_field(name="Available Assignments", value=assignment_list, inline=False)
            
            await ctx.send(embed=embed)
            
        except commands.MissingPermissions:
            await ctx.send(embed=discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can remove assignments.",
                color=0xff0000
            ))
        except Exception as e:
            logger.error(f"Error in remove_assignment command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))
    
    @commands.command(name='assignments', aliases=['list_assignments', 'upcoming'])
    async def list_assignments(self, ctx, days_ahead: int = 14):
        """
        View all assignments or upcoming assignments.
        
        Usage:
        !assignments           - Show assignments due in next 14 days
        !assignments 7         - Show assignments due in next 7 days
        !upcoming              - Same as !assignments
        !list_assignments 30   - Show assignments due in next 30 days
        """
        try:
            assignments = self.assignment_manager.get_upcoming_assignments(days_ahead)
            
            if not assignments:
                embed = discord.Embed(
                    title="📅 No Upcoming Assignments",
                    description=f"Great news! No assignments are due in the next {days_ahead} days.",
                    color=0x00ff00
                )
                
                # Add helpful information based on user's role
                if self._has_admin_role(ctx.author):
                    embed.add_field(
                        name="👑 For Admins",
                        value="**Add an assignment:**\n"
                              "`!add_assignment NAME | DUE_DATE | DESCRIPTION | [REMINDERS]`\n\n"
                              "**Example:**\n"
                              "`!add_assignment Homework 1 | tomorrow 11:59pm | Intro to Python`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="😊 Enjoy the Break!",
                        value="No assignments are currently scheduled. Use this time to:\n"
                              "• Review previous material\n"
                              "• Get ahead on reading\n" 
                              "• Ask questions in office hours\n"
                              "• Check back later for new assignments",
                        inline=False
                    )
                
                embed.add_field(
                    name="🔍 Check Different Time Ranges",
                    value="`!assignments 7` - Next 7 days\n"
                          "`!assignments 30` - Next 30 days\n"
                          "`!all_assignments` - Include past assignments",
                    inline=False
                )
                
                embed.set_footer(text="💡 Tip: You can also check the Events tab for Discord notifications!")
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📚 Assignments Due in Next {days_ahead} Days",
                description=f"Found {len(assignments)} upcoming assignment(s)",
                color=0x0099ff
            )
            
            current_time = datetime.now()
            
            for i, assignment in enumerate(assignments[:10]):  # Limit to 10 to avoid embed limits
                due_date = assignment["due_date"]
                time_until = assignment["time_until_due"]
                
                # Format time until due
                if time_until.days > 0:
                    time_str = f"{time_until.days} day(s)"
                elif time_until.seconds > 3600:
                    hours = time_until.seconds // 3600
                    time_str = f"{hours} hour(s)"
                else:
                    minutes = time_until.seconds // 60
                    time_str = f"{minutes} minute(s)"
                
                # Create urgency indicator
                if time_until.days <= 1:
                    urgency = "🚨"  # Due soon
                elif time_until.days <= 3:
                    urgency = "⚠️"   # Due this week
                else:
                    urgency = "📅"   # Normal
                
                field_name = f"{urgency} {assignment['name']}"
                field_value = (
                    f"📝 {assignment['description'][:100]}{'...' if len(assignment['description']) > 100 else ''}\n"
                    f"⏰ Due: <t:{int(due_date.timestamp())}:F>\n"
                    f"⌛ Time left: {time_str}"
                )
                
                embed.add_field(name=field_name, value=field_value, inline=False)
            
            if len(assignments) > 10:
                embed.set_footer(text=f"Showing first 10 of {len(assignments)} assignments. Use !assignments {days_ahead} to see all.")
            else:
                embed.set_footer(text="💡 Tip: Click on assignments in the Events tab to get Discord notifications!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in list_assignments command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))
    
    @commands.command(name='set_reminder_channel', aliases=['reminder_channel'])
    @commands.has_permissions(administrator=True)
    async def set_reminder_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Set the channel where assignment reminders will be posted.
        
        Usage:
        !set_reminder_channel #announcements
        !reminder_channel #general
        !set_reminder_channel    (uses current channel)
        """
        try:
            if channel is None:
                channel = ctx.channel
            
            self.assignment_manager.set_reminder_channel(channel.id)
            
            embed = discord.Embed(
                title="✅ Reminder Channel Set",
                description=f"Assignment reminders will be posted in {channel.mention}",
                color=0x00ff00
            )
            embed.set_footer(text="The bot will automatically post reminders based on each assignment's schedule")
            
            await ctx.send(embed=embed)
            
        except commands.MissingPermissions:
            await ctx.send(embed=discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can set the reminder channel.",
                color=0xff0000
            ))
        except Exception as e:
            logger.error(f"Error in set_reminder_channel command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))
    
    @commands.command(name='assignment_help', aliases=['help_assignments'])
    async def assignment_help(self, ctx):
        """Show detailed help for assignment commands."""
        embed = discord.Embed(
            title="📚 Assignment System Help",
            description="Manage assignments with Discord events and automatic reminders!",
            color=0x0099ff
        )
        
        if self._has_admin_role(ctx.author):
            embed.add_field(
                name="👑 Admin Commands",
                value=(
                    "**Add Assignment:**\n"
                    "`!add_assignment NAME | DUE_DATE | DESCRIPTION | [REMINDERS]`\n\n"
                    "**Examples:**\n"
                    "• `!add_assignment Homework 3 | Jan 15 11:59pm | Python loops`\n"
                    "• `!assignment Quiz 2 | tomorrow 5pm | Variables | 1d,2h`\n"
                    "• `!new_assignment Midterm | Feb 20 2pm | Ch 1-5 | 1w,3d,1d`\n\n"
                    "**Remove Assignment:**\n"
                    "`!remove_assignment NAME` or `!delete_assignment NAME`\n\n"
                    "**Set Reminder Channel:**\n"
                    "`!set_reminder_channel #announcements`\n\n"
                    "**Test Reminders:**\n"
                    "`!test_reminder` - Send a test reminder message"
                ),
                inline=False
            )
        
        embed.add_field(
            name="👥 Student Commands",
            value=(
                "**View Assignments:**\n"
                "`!assignments` - Next 14 days\n"
                "`!assignments 7` - Next 7 days\n"
                "`!upcoming` - Same as assignments\n"
                "`!list_assignments 30` - Next 30 days\n"
                "`!all_assignments` - All assignments including past\n"
                "`!next_assignment` - Just the next assignment due"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📅 Date Formats",
            value=(
                "• `Jan 15 11:59pm`\n"
                "• `tomorrow 5pm`\n" 
                "• `next Friday 2pm`\n"
                "• `Feb 20 2:30pm`\n"
                "• `12/15 11:59pm`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="⏰ Reminder Formats",
            value=(
                "• `1d` = 1 day before\n"
                "• `2h` = 2 hours before\n"
                "• `30m` = 30 minutes before\n"
                "• `1w` = 1 week before\n"
                "• `1d,2h` = Both 1 day and 2 hours"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🎯 Features",
            value=(
                "✅ Creates Discord Events automatically\n"
                "✅ Students get native Discord notifications\n"
                "✅ Automated announcement reminders\n"
                "✅ Flexible date and time parsing\n"
                "✅ Customizable reminder schedules"
            ),
            inline=False
        )
        
        embed.set_footer(text="💡 Pro tip: Students can click 'Interested' on Discord events to get notifications!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='all_assignments')
    async def all_assignments(self, ctx):
        """View all assignments including completed and overdue ones."""
        try:
            assignments = self.assignment_manager.list_assignments(include_completed=True)
            
            if not assignments:
                embed = discord.Embed(
                    title="📅 No Assignments Found",
                    description="No assignments have been created yet.",
                    color=0x0099ff
                )
                
                # Add helpful information based on user's role
                if self._has_admin_role(ctx.author):
                    embed.add_field(
                        name="👑 Get Started",
                        value="**Create your first assignment:**\n"
                              "`!add_assignment NAME | DUE_DATE | DESCRIPTION | [REMINDERS]`\n\n"
                              "**Quick Examples:**\n"
                              "• `!assignment Quiz 1 | Friday 5pm | Chapter 1-3`\n"
                              "• `!add_assignment Homework 1 | Jan 15 11:59pm | Python basics | 1d,2h`\n"
                              "• `!new_assignment Project | next Monday 2pm | Final project proposal`\n\n"
                              "**Need help?** Use `!assignment_help` for detailed instructions.",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🔧 Setup Reminders",
                        value="Don't forget to set up the reminder system:\n"
                              "1. `!set_reminder_channel #announcements`\n"
                              "2. `!test_reminder` to verify it works",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="😊 Nothing Here Yet",
                        value="Your instructor hasn't added any assignments yet.\n\n"
                              "**In the meantime:**\n"
                              "• Review course materials\n"
                              "• Check the syllabus for upcoming topics\n"
                              "• Ask questions in class or office hours\n"
                              "• Check back later for new assignments",
                        inline=False
                    )
                
                embed.set_footer(text="💡 Assignments will appear in the Discord Events tab and announcement channels!")
                await ctx.send(embed=embed)
                return
            
            # Separate assignments by status
            upcoming = []
            overdue = []
            completed = []
            
            for assignment in assignments:
                if assignment.get("completed", False):
                    completed.append(assignment)
                elif assignment["is_overdue"]:
                    overdue.append(assignment)
                else:
                    upcoming.append(assignment)
            
            embed = discord.Embed(
                title="📚 All Assignments",
                description=f"**Upcoming:** {len(upcoming)} | **Overdue:** {len(overdue)} | **Completed:** {len(completed)}",
                color=0x0099ff
            )
            
            # Show upcoming assignments
            if upcoming:
                upcoming_text = []
                for assignment in upcoming[:5]:
                    due_date = assignment["due_date"]
                    time_until = assignment["time_until_due"]
                    
                    if time_until.days > 0:
                        time_str = f"{time_until.days}d"
                    else:
                        hours = time_until.seconds // 3600
                        time_str = f"{hours}h"
                    
                    upcoming_text.append(f"📅 **{assignment['name']}** - {time_str}")
                
                embed.add_field(
                    name="⏰ Upcoming Assignments",
                    value="\n".join(upcoming_text),
                    inline=False
                )
            
            # Show overdue assignments
            if overdue:
                overdue_text = []
                for assignment in overdue[:5]:
                    due_date = assignment["due_date"]
                    overdue_text.append(f"🚨 **{assignment['name']}** - <t:{int(due_date.timestamp())}:R>")
                
                embed.add_field(
                    name="🚨 Overdue Assignments",
                    value="\n".join(overdue_text),
                    inline=False
                )
            
            if len(assignments) > 10:
                embed.set_footer(text=f"Showing overview of {len(assignments)} total assignments. Use !assignments for detailed upcoming view.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in all_assignments command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))
    
    @commands.command(name='next_assignment', aliases=['next'])
    async def next_assignment(self, ctx):
        """Show just the next assignment that's due."""
        try:
            assignments = self.assignment_manager.get_upcoming_assignments(30)
            
            if not assignments:
                embed = discord.Embed(
                    title="🎉 No Upcoming Assignments",
                    description="You're all caught up! No assignments due in the next 30 days.",
                    color=0x00ff00
                )
                
                # Add helpful information based on user's role
                if self._has_admin_role(ctx.author):
                    embed.add_field(
                        name="👑 Admin Options",
                        value="**Add a new assignment:**\n"
                              "`!add_assignment NAME | DUE_DATE | DESCRIPTION`\n\n"
                              "**Quick example:**\n"
                              "`!assignment Quiz 1 | Friday 5pm | Review material`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🌟 Great Work!",
                        value="You're ahead of the game! Use this time wisely:\n"
                              "• Review and reinforce previous lessons\n"
                              "• Work on personal projects\n"
                              "• Help classmates who might be struggling\n"
                              "• Prepare for upcoming topics",
                        inline=False
                    )
                
                embed.add_field(
                    name="🔍 Check for More",
                    value="`!assignments 60` - Look further ahead\n"
                          "`!all_assignments` - See all assignments\n"
                          "`!assignment_help` - Learn about the system",
                    inline=False
                )
                
                embed.set_footer(text="💡 Check the Events tab in Discord for any upcoming events!")
                await ctx.send(embed=embed)
                return
            
            # Get the next assignment (first one since they're sorted by due date)
            next_assignment = assignments[0]
            due_date = next_assignment["due_date"]
            time_until = next_assignment["time_until_due"]
            
            # Format time until due
            if time_until.days > 0:
                time_str = f"{time_until.days} day(s)"
                if time_until.seconds > 3600:
                    hours = time_until.seconds // 3600
                    time_str += f" and {hours} hour(s)"
            elif time_until.seconds > 3600:
                hours = time_until.seconds // 3600
                time_str = f"{hours} hour(s)"
            else:
                minutes = max(1, time_until.seconds // 60)
                time_str = f"{minutes} minute(s)"
            
            # Create urgency indicator
            if time_until.days <= 1:
                urgency = "🚨"
                color = 0xff0000
            elif time_until.days <= 3:
                urgency = "⚠️"
                color = 0xff8800
            else:
                urgency = "📅"
                color = 0x0099ff
            
            embed = discord.Embed(
                title=f"{urgency} Next Assignment Due",
                description=f"**{next_assignment['name']}**",
                color=color
            )
            
            embed.add_field(
                name="📝 Description",
                value=next_assignment["description"],
                inline=False
            )
            
            embed.add_field(
                name="⏰ Due Date",
                value=f"<t:{int(due_date.timestamp())}:F>",
                inline=True
            )
            
            embed.add_field(
                name="⌛ Time Left",
                value=time_str,
                inline=True
            )
            
            # Show additional upcoming assignments if any
            if len(assignments) > 1:
                other_assignments = []
                for assignment in assignments[1:4]:  # Show next 3
                    other_due = assignment["due_date"]
                    other_time = assignment["time_until_due"]
                    if other_time.days > 0:
                        other_time_str = f"{other_time.days}d"
                    else:
                        other_hours = other_time.seconds // 3600
                        other_time_str = f"{other_hours}h"
                    
                    other_assignments.append(f"• **{assignment['name']}** - {other_time_str}")
                
                if other_assignments:
                    embed.add_field(
                        name="📋 Also Coming Up",
                        value="\n".join(other_assignments),
                        inline=False
                    )
            
            embed.set_footer(text="💡 Use !assignments to see all upcoming assignments")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in next_assignment command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))
    
    @commands.command(name='test_reminder')
    @commands.has_permissions(administrator=True)
    async def test_reminder(self, ctx):
        """Send a test reminder to verify the reminder system is working."""
        try:
            reminder_channel_id = self.assignment_manager.get_reminder_channel_id()
            
            if not reminder_channel_id:
                embed = discord.Embed(
                    title="❌ No Reminder Channel Set",
                    description="Please set a reminder channel first using `!set_reminder_channel #channel`",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            reminder_channel = self.bot.get_channel(reminder_channel_id)
            if not reminder_channel:
                embed = discord.Embed(
                    title="❌ Reminder Channel Not Found",
                    description="The configured reminder channel could not be found. Please set it again.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            # Import the reminder system here to avoid circular imports
            from .assignment_reminder_system import AssignmentReminderSystem
            reminder_system = AssignmentReminderSystem(self.bot, self.assignment_manager)
            
            success = await reminder_system.send_test_reminder(reminder_channel, "Test Assignment")
            
            if success:
                embed = discord.Embed(
                    title="✅ Test Reminder Sent",
                    description=f"A test reminder was sent to {reminder_channel.mention}",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="❌ Test Failed",
                    description="Failed to send test reminder. Check the logs for details.",
                    color=0xff0000
                )
            
            await ctx.send(embed=embed)
            
        except commands.MissingPermissions:
            await ctx.send(embed=discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can send test reminders.",
                color=0xff0000
            ))
        except Exception as e:
            logger.error(f"Error in test_reminder command: {e}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            ))

def setup(bot):
    """Setup function for the cog."""
    # This will be called when the cog is loaded
    pass