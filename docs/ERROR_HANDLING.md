# Error Handling System

## 🛡️ Comprehensive Error Management

The Discord bot now includes robust error handling to prevent crashes and provide user-friendly feedback.

### ✅ Features

**User-Friendly Error Messages:**
- Formatted Discord embeds instead of raw Python errors
- Specific help text for common mistakes
- Usage examples when commands are used incorrectly

**Error Types Handled:**
- `CommandNotFound` - Ignored (reduces spam)
- `MissingPermissions` - User doesn't have required role
- `BotMissingPermissions` - Bot lacks Discord permissions
- `MissingRequiredArgument` - Missing command parameters
- `BadArgument` - Invalid parameter types/values
- `ChannelNotFound` - Channel doesn't exist or not accessible
- `MemberNotFound` - User not found in server
- `CommandOnCooldown` - Command used too frequently

**Admin Features:**
- Detailed error information shown only to admins
- Full error logs sent to configured log channel
- Stack traces in bot logs for debugging

**Stability:**
- Bot continues running after any command error
- Automatic error recovery and logging
- No crashes from user input mistakes

### 📋 Examples

**Before (Bot crashes):**
```
Traceback (most recent call last):
  File "main.py", line 123, in clear_channel
    channel = ctx.guild.get_channel(int(channel_name))
ValueError: invalid literal for int() with base 10: 'invalid'
```

**After (User-friendly message):**
```
❌ Channel Not Found
Could not find the specified channel.

💡 Tip: Make sure to use #channel-name or verify the channel exists.
```

### 🔧 Configuration

Error handling is automatic and requires no additional setup. The system integrates with:
- Admin role checking (`ADMIN_ROLE_NAMES`)
- Log channel notifications (`LOG_CHANNEL_ID`)
- Existing bot logging system

### 🚨 Error Notifications

When errors occur:
1. **User sees** friendly error message with helpful tips
2. **Admins see** detailed error information in the same message
3. **Log channel gets** full error report with context
4. **Bot logs record** complete stack trace for debugging

This ensures users get helpful feedback while admins have full debugging information.