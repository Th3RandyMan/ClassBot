#!/usr/bin/env python3
"""
Assignment Manager - Discord Events + Custom Reminders System
Combines Discord's native events with automated announcement reminders.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class AssignmentManager:
    """Manages assignments with Discord events and custom reminder announcements."""
    
    def __init__(self, config_path: str = "config/assignments.json"):
        self.config_path = config_path
        self.assignments = self._load_assignments()
        self.reminder_channel_id = None
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    def _load_assignments(self) -> Dict:
        """Load assignments from JSON file."""
        default_config = {
            "assignments": {},
            "settings": {
                "reminder_channel_id": None,
                "default_reminder_schedule": ["1d", "2h"],  # 1 day, 2 hours before
                "timezone": "UTC"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to handle new fields
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # Create default file
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return default_config
                
        except Exception as e:
            logger.error(f"Error loading assignments config: {e}")
            return default_config
    
    def _save_assignments(self):
        """Save assignments to JSON file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.assignments, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving assignments config: {e}")
    
    def _parse_reminder_time(self, reminder_str: str) -> timedelta:
        """Parse reminder time string like '1d', '2h', '30m' into timedelta."""
        reminder_str = reminder_str.lower().strip()
        
        if reminder_str.endswith('d'):
            days = int(reminder_str[:-1])
            return timedelta(days=days)
        elif reminder_str.endswith('h'):
            hours = int(reminder_str[:-1])
            return timedelta(hours=hours)
        elif reminder_str.endswith('m'):
            minutes = int(reminder_str[:-1])
            return timedelta(minutes=minutes)
        elif reminder_str.endswith('w'):
            weeks = int(reminder_str[:-1])
            return timedelta(weeks=weeks)
        else:
            raise ValueError(f"Invalid reminder format: {reminder_str}. Use formats like '1d', '2h', '30m', '1w'")
    
    def _format_reminder_time(self, delta: timedelta) -> str:
        """Format timedelta back to human readable string."""
        if delta.days > 0:
            if delta.days == 1:
                return "1 day"
            elif delta.days == 7:
                return "1 week"
            elif delta.days % 7 == 0:
                return f"{delta.days // 7} weeks"
            else:
                return f"{delta.days} days"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "now"
    
    async def add_assignment(self, guild: discord.Guild, name: str, due_date: datetime, 
                           description: str, reminder_schedule: List[str] = None) -> Tuple[bool, str]:
        """
        Add an assignment with Discord event and reminder schedule.
        
        Args:
            guild: Discord guild to create event in
            name: Assignment name
            due_date: When assignment is due
            description: Assignment description
            reminder_schedule: List of reminder times like ['1d', '2h']
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not name or not name.strip():
                return False, "Assignment name cannot be empty"
            
            if due_date <= datetime.now():
                return False, "Due date must be in the future"
            
            # Use default reminder schedule if none provided
            if reminder_schedule is None:
                reminder_schedule = self.assignments["settings"]["default_reminder_schedule"]
            
            # Parse and validate reminder schedule
            reminder_deltas = []
            for reminder in reminder_schedule:
                try:
                    delta = self._parse_reminder_time(reminder)
                    reminder_deltas.append(delta)
                except ValueError as e:
                    return False, f"Invalid reminder format '{reminder}': {str(e)}"
            
            # Create Discord event
            try:
                # Discord events need start and end time
                start_time = due_date - timedelta(hours=1)  # Event "starts" 1 hour before due
                end_time = due_date
                
                event = await guild.create_scheduled_event(
                    name=f"📚 {name}",
                    description=f"{description}\n\n🗓️ Due: {due_date.strftime('%B %d, %Y at %I:%M %p')}",
                    start_time=start_time,
                    end_time=end_time,
                    privacy_level=discord.PrivacyLevel.guild_only,
                    entity_type=discord.EntityType.external,
                    location="Assignment Submission"
                )
                
                discord_event_id = event.id
                
            except Exception as e:
                logger.error(f"Error creating Discord event: {e}")
                return False, f"Failed to create Discord event: {str(e)}"
            
            # Generate unique assignment ID
            assignment_id = f"{name.lower().replace(' ', '_')}_{int(due_date.timestamp())}"
            
            # Calculate reminder times
            reminder_times = []
            for delta in reminder_deltas:
                reminder_time = due_date - delta
                if reminder_time > datetime.now():  # Only add future reminders
                    reminder_times.append({
                        "time": reminder_time.isoformat(),
                        "sent": False,
                        "description": self._format_reminder_time(delta)
                    })
            
            # Store assignment
            assignment_data = {
                "name": name,
                "description": description,
                "due_date": due_date.isoformat(),
                "created_date": datetime.now().isoformat(),
                "discord_event_id": discord_event_id,
                "guild_id": guild.id,
                "reminder_schedule": reminder_schedule,
                "reminder_times": reminder_times,
                "completed": False
            }
            
            self.assignments["assignments"][assignment_id] = assignment_data
            self._save_assignments()
            
            return True, f"✅ Assignment '{name}' created successfully!\n📅 Discord event created\n⏰ Reminders scheduled: {', '.join([r['description'] + ' before' for r in reminder_times])}"
            
        except Exception as e:
            logger.error(f"Error adding assignment: {e}")
            return False, f"Error creating assignment: {str(e)}"
    
    async def remove_assignment(self, guild: discord.Guild, assignment_name: str) -> Tuple[bool, str]:
        """Remove an assignment and its Discord event."""
        try:
            # Find assignment by name (case insensitive partial match)
            assignment_id = None
            assignment_data = None
            
            for aid, data in self.assignments["assignments"].items():
                if assignment_name.lower() in data["name"].lower():
                    assignment_id = aid
                    assignment_data = data
                    break
            
            if not assignment_id:
                return False, f"Assignment '{assignment_name}' not found"
            
            # Remove Discord event
            try:
                if assignment_data.get("discord_event_id"):
                    event = guild.get_scheduled_event(assignment_data["discord_event_id"])
                    if event:
                        await event.delete()
            except Exception as e:
                logger.warning(f"Could not delete Discord event: {e}")
            
            # Remove from assignments
            del self.assignments["assignments"][assignment_id]
            self._save_assignments()
            
            return True, f"✅ Assignment '{assignment_data['name']}' removed successfully"
            
        except Exception as e:
            logger.error(f"Error removing assignment: {e}")
            return False, f"Error removing assignment: {str(e)}"
    
    def list_assignments(self, include_completed: bool = False) -> List[Dict]:
        """Get list of assignments, optionally including completed ones."""
        assignments = []
        current_time = datetime.now()
        
        for assignment_id, data in self.assignments["assignments"].items():
            if not include_completed and data.get("completed", False):
                continue
                
            due_date = datetime.fromisoformat(data["due_date"])
            
            assignment_info = {
                "id": assignment_id,
                "name": data["name"],
                "description": data["description"],
                "due_date": due_date,
                "discord_event_id": data.get("discord_event_id"),
                "is_overdue": due_date < current_time,
                "time_until_due": due_date - current_time,
                "completed": data.get("completed", False)
            }
            
            assignments.append(assignment_info)
        
        # Sort by due date
        assignments.sort(key=lambda x: x["due_date"])
        return assignments
    
    def get_upcoming_assignments(self, days_ahead: int = 7) -> List[Dict]:
        """Get assignments due within the specified number of days."""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        all_assignments = self.list_assignments()
        
        return [a for a in all_assignments if a["due_date"] <= cutoff_date and not a["is_overdue"]]
    
    def set_reminder_channel(self, channel_id: int):
        """Set the channel where reminders should be posted."""
        self.assignments["settings"]["reminder_channel_id"] = channel_id
        self._save_assignments()
        
    def get_reminder_channel_id(self) -> Optional[int]:
        """Get the reminder channel ID."""
        return self.assignments["settings"].get("reminder_channel_id")
    
    def get_pending_reminders(self) -> List[Tuple[str, Dict]]:
        """Get reminders that need to be sent."""
        current_time = datetime.now()
        pending = []
        
        for assignment_id, assignment_data in self.assignments["assignments"].items():
            if assignment_data.get("completed", False):
                continue
                
            for reminder in assignment_data.get("reminder_times", []):
                if not reminder["sent"]:
                    reminder_time = datetime.fromisoformat(reminder["time"])
                    if reminder_time <= current_time:
                        pending.append((assignment_id, {
                            "assignment": assignment_data,
                            "reminder": reminder
                        }))
        
        return pending
    
    def mark_reminder_sent(self, assignment_id: str, reminder_time: str):
        """Mark a reminder as sent."""
        if assignment_id in self.assignments["assignments"]:
            for reminder in self.assignments["assignments"][assignment_id].get("reminder_times", []):
                if reminder["time"] == reminder_time:
                    reminder["sent"] = True
                    self._save_assignments()
                    break