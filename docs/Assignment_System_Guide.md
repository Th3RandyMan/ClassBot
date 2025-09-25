# 📚 Assignment System - Complete Implementation Guide

## 🎯 Overview

Your Discord bot now has a **complete assignment management system** that combines Discord's native Events with automated announcement reminders. This provides the best of both worlds:

- **Discord Events**: Students can subscribe for native Discord notifications
- **Automated Reminders**: Posted to announcement channels at specified times
- **Intuitive Commands**: Easy-to-use syntax for managing assignments
- **Flexible Scheduling**: Customizable reminder times (1d, 2h, 30m, etc.)

## 🚀 Features

### ✅ **For Students**
- **View assignments** with flexible time ranges
- **See next assignment** due with urgency indicators
- **Native Discord notifications** through Events system
- **Automated reminders** posted to channels
- **Rich embed displays** with due dates and descriptions

### ✅ **For TAs/Admins**
- **Add assignments** with intuitive syntax
- **Remove assignments** easily
- **Set reminder channels** for announcements
- **Test reminder system** to verify functionality
- **Automated Discord Events** creation

### ✅ **System Features**
- **Background reminder system** (checks every 15 minutes)
- **Smart urgency detection** (different colors/emojis based on due date)
- **Flexible date parsing** (tomorrow 5pm, Jan 15 11:59pm, etc.)
- **Customizable reminder schedules** (1w,3d,1d,2h before due)
- **JSON-based configuration** for easy management

## 📋 Command Reference

### 👑 **Admin Commands**

#### Add Assignment
```
!add_assignment NAME | DUE_DATE | DESCRIPTION | [REMINDERS]
```

**Examples:**
```
!add_assignment Homework 3 | Jan 15 11:59pm | Python loops assignment
!assignment Quiz 2 | tomorrow 5pm | Variables and functions | 1d,2h  
!new_assignment Midterm Exam | Feb 20 2pm | Chapters 1-5 | 1w,3d,1d
```

**Date Formats:**
- `Jan 15 11:59pm` - Specific date and time
- `tomorrow 5pm` - Relative date
- `12/25 2pm` - MM/DD format
- `Feb 20 2:30pm` - Month name with time

**Reminder Formats:**
- `1d` = 1 day before
- `2h` = 2 hours before  
- `30m` = 30 minutes before
- `1w` = 1 week before
- `1d,2h` = Multiple reminders

#### Remove Assignment
```
!remove_assignment NAME
!delete_assignment NAME
!del_assignment NAME
```
Uses partial name matching - finds closest match.

#### Set Reminder Channel
```
!set_reminder_channel #announcements
!reminder_channel #general
!set_reminder_channel    (uses current channel)
```

#### Test Reminders
```
!test_reminder
```
Sends a test reminder to verify the system is working.

### 👥 **Student Commands**

#### View Assignments
```
!assignments           # Next 14 days (default)
!assignments 7         # Next 7 days
!upcoming              # Same as !assignments
!list_assignments 30   # Next 30 days
```

#### View All Assignments
```
!all_assignments
```
Shows upcoming, overdue, and completed assignments.

#### Next Assignment
```
!next_assignment
!next
```
Shows just the next assignment due with urgency indicators.

#### Help
```
!assignment_help
!help_assignments
```
Detailed help for the assignment system.

## 🎨 **Visual Examples**

### Assignment Reminder (1 day before)
```
⚠️ Assignment Due Tomorrow!
📚 Homework 3: Python Loops

📝 Description: Complete exercises 1-10 on list comprehensions
⏰ Due Date: January 15, 2024 at 11:59 PM
⌛ Time Remaining: Due tomorrow

💡 Final day reminders:
• Review the requirements  
• Start early if you haven't
• Visit office hours if stuck

💡 Check the Events tab for more details and to get Discord notifications!
```

### Upcoming Assignments List
```
📚 Assignments Due in Next 14 Days
Found 3 upcoming assignment(s)

🚨 Homework 3: Python Loops
📝 Complete exercises 1-10 on list comprehensions
⏰ Due: January 15, 2024 at 11:59 PM
⌛ Time left: 1 day(s)

📅 Quiz 2: Variables and Functions  
📝 Test on variables, functions, and scope
⏰ Due: January 18, 2024 at 5:00 PM
⌛ Time left: 4 day(s)
```

## ⚙️ **Setup Instructions**

### 1. **Initial Setup**
The system is already integrated into your main bot. Just run:
```bash
python main.py
```

### 2. **Set Reminder Channel**
```
!set_reminder_channel #announcements
```

### 3. **Test the System**
```
!test_reminder
```

### 4. **Add Your First Assignment**
```
!add_assignment Test Assignment | tomorrow 5pm | This is a test | 2h
```

## 🔧 **How It Works**

### **Discord Events Integration**
1. When you add an assignment, the bot automatically creates a Discord Event
2. Students see the event in the server's Events tab
3. Students can click "Interested" to get native Discord notifications
4. The event shows the assignment name, description, and due date

### **Automated Reminders**  
1. Background task runs every 15 minutes
2. Checks for assignments with pending reminders
3. Posts formatted announcements to the reminder channel
4. Uses urgency-based styling (colors, emojis) based on time remaining

### **Smart Scheduling**
- **1 week before**: Blue color, planning reminders
- **3 days before**: Yellow color, progress check
- **1 day before**: Orange color, final push reminders  
- **2 hours before**: Red color, urgent last-minute tips

## 📁 **File Structure**

```
src/bot/
├── assignment_manager.py          # Core logic for managing assignments
├── assignment_commands.py         # Discord commands
└── assignment_reminder_system.py  # Background reminder system

config/
└── assignments.json              # Assignment data and settings

docs/
└── Assignment_System_Guide.md    # This documentation
```

## 🚀 **Advanced Features**

### **Configuration Options**
Edit `config/assignments.json`:
```json
{
  "assignments": {},
  "settings": {
    "reminder_channel_id": null,
    "default_reminder_schedule": ["1d", "2h"],
    "timezone": "UTC"
  }
}
```

### **Custom Reminder Schedules**
Different assignments can have different reminder patterns:
- **Homework**: `1d,2h` (1 day and 2 hours before)
- **Exams**: `1w,3d,1d,2h` (1 week, 3 days, 1 day, 2 hours before)
- **Quick quizzes**: `2h` (Just 2 hours before)

### **Multiple Reminder Channels**
While you can only set one reminder channel at a time, you can:
1. Change the reminder channel for different types of assignments
2. Use the test command to verify reminders are working
3. Check the configuration file to see current settings

## 🎯 **Student Benefits**

1. **Never miss assignments** - Multiple reminder systems
2. **Native Discord notifications** - Use Discord's built-in system
3. **Easy assignment viewing** - Multiple ways to check what's due
4. **Visual urgency indicators** - Know what's most important
5. **Rich information display** - See descriptions and due dates clearly

## 👑 **TA/Admin Benefits**

1. **Easy assignment management** - Intuitive command syntax
2. **Automated Discord Events** - No manual event creation
3. **Flexible reminder scheduling** - Customize for different assignment types
4. **Background automation** - Set it and forget it
5. **Test functionality** - Verify reminders are working
6. **JSON configuration** - Easy to backup and modify

## 🎉 **Success! Your Assignment System is Ready**

Your Discord bot now has a professional, full-featured assignment management system that rivals commercial classroom management tools. Students will love the convenience, and you'll love how easy it is to manage!

**Next steps:**
1. Test the system with a few assignments
2. Get feedback from students on reminder timing
3. Adjust reminder schedules as needed
4. Enjoy never having students ask "When is this due?" again! 🎯