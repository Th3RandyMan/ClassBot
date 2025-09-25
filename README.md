# 🤖 Class Bot

A Discord bot designed to monitor users without specific roles and prevent them from posting code in channels. Perfect for educational servers where only verified students should be able to share code.

## ✨ Features

- **Code Detection**: Automatically detects code in text messages using advanced pattern matching
- **Image Analysis**: Uses OCR to detect code in uploaded images  
- **Role-Based Permissions**: Only users with specified roles can post code
- **Assignment Management**: Create and track assignments with automated Discord events and reminders
- **Persistent Warning System**: Tracks warnings with automatic 30-day expiration and JSON storage
- **Enhanced Error Recovery**: Automatic reconnection and self-healing capabilities
- **Admin Commands**: Comprehensive commands for server administrators
- **Confirmation Dialogs**: Safety confirmations for destructive actions
- **Performance Optimized**: Fast bulk operations and efficient message processing
- **Modular Architecture**: Well-organized codebase with separated concerns

## 🚀 Quick Start

### 1. Create Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "Class Bot")
3. Go to the "Bot" section and click "Add Bot" 
4. Copy the bot token (you'll need this later)
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent

### 2. Invite Bot to Server

1. In Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Manage Messages (to delete code posts)
   - Kick Members (for admin commands)
   - Embed Links
   - Attach Files
   - Read Message History
   - Manage Events (for assignment system)
4. Copy and visit the generated URL to invite the bot

### 3. Deploy Your Bot

**For cloud deployment** (recommended for production), see our comprehensive **[Deployment Guide](docs/deployment-guide.md)** which covers:
- ☁️ Cloud platforms (Render, Heroku, Railway, DigitalOcean)
- 💻 Local development setup for Windows, macOS, and Linux
- 🐛 Troubleshooting guides
- 📊 Monitoring and maintenance

**For quick local testing**:
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your bot credentials
4. Run: `python main.py`

## 🎮 Commands

### For Everyone
- `!help` - Display help information and available commands
- `!classbot` - Friendly greeting and bot information
- `!assignments` - View upcoming assignments (next 14 days)
- `!all_assignments` - View all assignments including completed ones
- `!next_assignment` - Show the next assignment due
- `!assignment_help` - Detailed help for assignment system

### For Administrators  
- `!add_assignment` - Create new assignment with Discord event and reminders
- `!remove_assignment` - Remove assignment and its Discord event
- `!set_reminder_channel` - Configure reminder notification channel
- `!test_reminder` - Test the reminder system
- `!remove_roleless` - Remove all users without roles (with confirmation)
- `!clear_channel #channel [limit]` - Delete messages from channel (with confirmation)
- `!check_usernames [action]` - Check for inappropriate usernames
- `!username_whitelist [add|remove|list]` - Manage username whitelist
- `!bot_disable [duration] [reason]` - Temporarily disable bot
- `!bot_enable [reason]` - Re-enable disabled bot
- `!bot_status` - Check current bot status and health
- `!bot_maintenance [on|off|toggle]` - Control maintenance mode

## 🔧 How It Works

### Code Detection

The bot uses multiple sophisticated methods to detect code:

1. **Text Pattern Matching**: Advanced regex patterns detect:
   - Programming keywords (`def`, `class`, `import`, `function`, `var`, etc.)
   - Code syntax (brackets, semicolons, operators)
   - Comments (`//`, `/* */`, `#`)
   - Function calls and variable assignments
   - SQL queries and HTML tags

2. **Image OCR Analysis**: 
   - Extracts text from uploaded images using Tesseract OCR
   - Analyzes extracted text for code patterns
   - **Fallback Behavior**: When OCR unavailable, alerts about image posts from unauthorized users
   - **Independent Operation**: Text detection always works regardless of OCR status

3. **Heuristic Analysis**: Considers formatting patterns like indentation and structure

### Assignment Management

The bot includes a comprehensive assignment tracking system:

- **Discord Events Integration**: Creates native Discord events for assignments
- **Automated Reminders**: Configurable reminders (24h, 1h, etc.) with urgency indicators
- **Natural Language Parsing**: Flexible date/time input ("tomorrow 5pm", "next Friday", etc.)
- **Role-Based Access**: Admins manage assignments, everyone can view
- **Persistent Storage**: Assignments saved to JSON with automatic cleanup

### User Workflow

1. **Code Detection**: User without required role posts code
2. **Immediate Action**: Bot detects and deletes the message
3. **User Warning**: Bot sends warning with current count and helpful information  
4. **Admin Logging**: Action logged to configured admin channel
5. **Persistence**: Warnings stored with automatic 30-day expiration

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Bot token from Discord Developer Portal | `MTxxx...` |
| `GUILD_ID` | Your Discord server ID | `123456789012345678` |
| `ALLOWED_ROLE_NAME` | Role that allows code posting (empty = any role) | `Student` or leave empty |
| `ADMIN_ROLE_NAMES` | Comma-separated admin roles | `Professor,Teaching Assistant (TA)` |
| `LOG_CHANNEL_ID` | Channel for admin notifications (optional) | `123456789012345678` |

### File Structure

```
Discord Bot/
├── main.py                     # 🚀 Main entry point (streamlined)
├── main_backup.py              # Original main.py backup
├── requirements.txt            # Python dependencies
├── runtime.txt                # Python version for deployment
├── render.yaml                # Render deployment config
├── Aptfile                    # System packages
│
├── src/                       # 📦 Source code modules
│   ├── config.py              # ⚙️ Configuration management
│   └── bot/                   # 🤖 Bot modules
│       ├── commands.py        # 💬 Command definitions
│       ├── events.py          # 📡 Event handlers
│       ├── error_handlers.py  # 🛡️ Error management
│       ├── assignment_manager.py      # 📚 Assignment logic
│       ├── assignment_commands.py     # 📝 Assignment commands
│       ├── assignment_reminder_system.py  # ⏰ Automated reminders
│       ├── warning_system.py          # ⚠️ Persistent warnings
│       ├── error_recovery.py          # 🔄 Auto-reconnection
│       ├── username_filter.py         # 🚫 Username monitoring
│       ├── bot_controller.py          # 🎛️ Bot state management
│       └── utils/             # 🔧 Utility modules
│           └── code_detection.py      # 🔍 Code detection engine
│
├── config/                    # 📋 Configuration files
│   └── assignments.json       # Assignment storage
│
├── data/                      # 💾 Runtime data
│   ├── warnings.json          # User warnings (auto-created)
│   └── bot.log               # Application logs
│
├── tests/                     # 🧪 Test files
│   └── test_*.py             # Various test scripts
│
├── scripts/                   # 📜 Utility scripts
│   └── demo_*.py             # Demo and utility scripts
│
└── docs/                      # 📖 Documentation
    ├── deployment-guide.md    # 🚀 Complete deployment guide
    └── reorganization_summary.md  # 📝 Refactoring details
```

## 🛡️ Security & Permissions

### Required Discord Permissions
- **View Channels** - See messages and channels
- **Send Messages** - Send warnings and responses  
- **Manage Messages** - Delete unauthorized code posts
- **Kick Members** - For remove_roleless command
- **Embed Links** - Send rich message embeds
- **Read Message History** - Process existing messages
- **Manage Events** - Create assignment events

### Safety Features
- **Confirmation dialogs** for all destructive operations
- **Protected user exclusions** (bots, server owner) from bulk actions
- **Rate limiting** to prevent API abuse
- **Comprehensive logging** for audit trails
- **Automatic data cleanup** to prevent storage bloat

## 🧪 Development & Testing

### Local Development
1. Follow the setup guide in [docs/deployment-guide.md](docs/deployment-guide.md)
2. Use a test Discord server for development
3. Test with various code samples and edge cases
4. Verify admin commands with appropriate permissions

### Code Architecture
- **Modular Design**: Separated concerns across multiple modules
- **Error Handling**: Comprehensive error recovery and logging
- **Configuration**: Centralized config management
- **Extensibility**: Easy to add new commands and features

### Testing
- Unit tests in `tests/` directory
- Integration tests for Discord API interactions
- Manual testing scenarios for edge cases

## 📚 Documentation

- **[Deployment Guide](docs/deployment-guide.md)** - Complete setup for cloud and local deployment
- **[Reorganization Summary](docs/reorganization_summary.md)** - Details about code structure improvements

## 🐛 Troubleshooting

### Common Issues
- **Bot not responding**: Check token, permissions, and online status
- **Code not detected**: Review detection patterns and user roles  
- **OCR issues**: Bot automatically falls back to text-only detection
- **Permission errors**: Ensure bot role hierarchy and permissions

For detailed troubleshooting, see the **[Deployment Guide](docs/deployment-guide.md)**.

## 🔄 Updates & Maintenance

### Cloud Deployments
- Push changes to connected repository
- Platform automatically redeploys
- Monitor deployment logs

### Local Development  
- `git pull` for latest changes
- `pip install -r requirements.txt --upgrade` for dependencies
- Restart bot process

## 📄 License

This project is provided as-is for educational purposes. Feel free to modify and adapt it to your needs.

---

**Happy moderating! 🎓**

For deployment instructions, see **[docs/deployment-guide.md](docs/deployment-guide.md)**