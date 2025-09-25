# Bot Control System - Admin Guide

## Overview

The ClassBot now includes a comprehensive control system that allows administrators to temporarily disable, enable, and manage the bot's operations. This is essential for maintenance, testing, and emergency situations.

## 🎮 Available Commands

### Core Control Commands

#### `!bot_disable [minutes] [reason]`
**Permission**: Admin/TA roles only

Temporarily or permanently disable the bot.

**Examples:**
```
!bot_disable                           # Disable indefinitely  
!bot_disable 30                        # Disable for 30 minutes
!bot_disable 60 Server maintenance     # Disable for 1 hour with custom reason
```

**What happens:**
- Most commands become unavailable
- Users get "Bot Temporarily Disabled" message when trying to use commands
- Only essential admin commands remain active
- Safety features (code monitoring) continue working

---

#### `!bot_enable [reason]`
**Permission**: Admin/TA roles only

Re-enable the bot after it has been disabled.

**Examples:**
```
!bot_enable                           # Basic re-enable
!bot_enable Maintenance completed     # Re-enable with reason
```

---

#### `!bot_status`
**Permission**: Admin/TA roles only

Check the current status of the bot.

**Shows:**
- Current enable/disable state
- Reason for any disable state  
- Who disabled the bot and when
- Time remaining for temporary disables
- Available commands when disabled

---

#### `!bot_maintenance [on/off/toggle]`
**Permission**: Admin/TA roles only

Enable or disable maintenance mode.

**Examples:**
```
!bot_maintenance on                   # Enable maintenance mode
!bot_maintenance off                  # Disable maintenance mode
!bot_maintenance toggle               # Switch current state
```

**Maintenance mode:**
- Special disabled state for updates/maintenance
- Clear indication to users that maintenance is occurring
- Same command restrictions as regular disable

---

#### `!bot_kill`
**Permission**: Admin/TA roles only

**⚠️ DANGER: Complete shutdown of the bot**

This command completely shuts down the bot process. The bot will not restart automatically and requires manually running the Python script again.

**Use cases:**
- Emergency shutdown
- Preparing for major updates
- System maintenance requiring full restart

---

## 🔒 Security Features

### Permission Protection
- All control commands require Admin or TA roles
- Same permission system as other critical commands
- Actions are logged with user attribution

### Command Filtering When Disabled
When the bot is disabled, only these commands work:
- `!bot_enable` - To re-enable the bot
- `!bot_status` - To check current status
- `!bot_kill` - For emergency shutdown
- `!help_classbot` - Basic help information

**All other commands are blocked** and users see a helpful message explaining the bot is disabled.

### Safety First Design
Even when disabled, critical safety features continue:
- **Code monitoring** - Still detects and removes inappropriate code
- **Username filtering** - New members are still screened
- **Admin notifications** - Important alerts still sent
- **Error recovery** - System stability maintained

## ⏰ Disable Modes

### Temporary Disable
- Set with `!bot_disable [minutes]`
- Automatically re-enables after specified time
- Users see countdown of remaining time
- Perfect for scheduled maintenance

### Indefinite Disable  
- Set with `!bot_disable` (no time specified)
- Requires manual `!bot_enable` to restore
- Good for open-ended maintenance or issues

### Maintenance Mode
- Set with `!bot_maintenance on`
- Special state indicating scheduled maintenance
- Clear messaging to users about the situation
- Automatically enables when maintenance is complete

### Complete Shutdown
- Triggered with `!bot_kill`
- Bot process terminates completely
- Requires manual script restart to restore
- For emergencies or major updates

## 💡 Best Practices

### Planned Maintenance
1. Announce maintenance to users beforehand
2. Use `!bot_disable 60 Scheduled maintenance` 
3. Perform your maintenance work
4. Use `!bot_enable Maintenance completed`
5. Confirm all systems working with `!bot_status`

### Emergency Situations
1. Use `!bot_disable Emergency shutdown` immediately
2. Investigate the issue
3. Fix the problem
4. Test in a safe environment first
5. Re-enable with `!bot_enable Issue resolved`

### Testing New Features
1. `!bot_disable 15 Testing new features`
2. Test your changes while bot is safely disabled
3. `!bot_enable Testing completed` when ready
4. Monitor logs for any issues

### Complete Updates
1. Announce downtime to users
2. `!bot_kill` to fully shutdown
3. Update code, restart script
4. Verify all systems operational

## 📊 Status Messages

### When Bot is Disabled
Users attempting to use commands see:
```
🤖 Bot Temporarily Disabled

The bot is currently disabled.
Reason: Server maintenance
Disabled By: Admin Name
Re-enabled In: 25 minutes
Available Commands: !bot_status, !bot_enable, !help_classbot
```

### When Bot is in Maintenance
```
🤖 Bot Temporarily Disabled

The bot is currently in maintenance mode.
Reason: Maintenance mode  
Disabled By: Admin Name
Status: Indefinitely disabled
Available Commands: !bot_status, !bot_enable, !help_classbot
```

## 🔧 Configuration

Bot control settings are stored in `config/bot_control.json`:

```json
{
  "enabled": true,
  "disabled_until": null,
  "disabled_reason": null, 
  "disabled_by": null,
  "disabled_timestamp": null,
  "maintenance_mode": false,
  "allowed_commands_when_disabled": [
    "bot_enable",
    "bot_status", 
    "bot_kill",
    "help_classbot"
  ]
}
```

## 📝 Logging

All control actions are logged:
- `Bot disabled by Admin Name for 30 minutes: Server maintenance`
- `Bot enabled by Admin Name: Maintenance completed`  
- `Maintenance mode enabled by Admin Name`
- `Bot shutdown initiated by Admin Name`

## ⚠️ Important Notes

1. **Safety Features Continue**: Code monitoring and username filtering work even when bot is "disabled"
2. **Admin Access**: Control commands always work for admins, even when bot is disabled
3. **Automatic Recovery**: Temporary disables auto-enable, no admin needed
4. **Graceful Messaging**: Users get helpful information, not confusing errors
5. **Full Logging**: All actions tracked for accountability

---

**System Version**: 1.0  
**Last Updated**: September 25, 2025  
**Compatible with**: ClassBot v2.0+