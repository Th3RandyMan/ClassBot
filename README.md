# 🤖 Class Bot

A Discord bot designed to monitor users without specific roles and prevent them from posting code in channels. Perfect for educational servers where only verified students should be able to share code.

## ✨ Features

- **Code Detection**: Automatically detects code in text messages using advanced pattern matching
- **Image Analysis**: Uses OCR to detect code in uploaded images
- **Role-Based Permissions**: Only users with specified roles can post code
- **Persistent Warning System**: Tracks warnings with automatic 30-day expiration and JSON storage
- **Enhanced Error Recovery**: Automatic reconnection and self-healing capabilities for Render deployment
- **Admin Commands**: Special commands for server administrators to manage users and channels
- **Confirmation Dialogs**: Safety confirmations for destructive actions
- **Performance Optimized**: Fast bulk operations and efficient message processing
- **Logging**: Optional logging channel for admin monitoring

## 🚀 Quick Setup

### 1. Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "Class Bot")
3. Go to the "Bot" section and click "Add Bot"
4. Copy the bot token (you'll need this later)
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent

### 2. Invite the Bot to Your Server

1. In the Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Manage Messages (to delete code posts)
   - Kick Members (for remove_roleless command)
   - Embed Links
   - Attach Files
   - Read Message History
4. Copy and visit the generated URL to invite the bot

### 3. Deploy to Render (Recommended)

**Easy cloud deployment with automatic Tesseract OCR setup:**

1. **Fork/Upload your code** to GitHub
2. **Connect to Render**:
   - Go to [render.com](https://render.com) and sign up
   - Connect your GitHub account
   - Click "New" → "Background Worker"
   - Select your repository

3. **Configure deployment**:
   - **Name**: `class-bot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng && apt-get install -y libgl1-mesa-glx libglib2.0-0
     ```
   - **Start Command**: `python bot.py`

4. **Set Environment Variables** in Render dashboard:
   - `DISCORD_TOKEN`: Your bot token from Discord Developer Portal
   - `GUILD_ID`: Your Discord server ID
   - `ALLOWED_ROLE_NAME`: Leave empty (allows anyone with a role to post code)
   - `ADMIN_ROLE_NAMES`: `Professor,Teaching Assistant (TA)` (comma-separated admin roles)
   - `LOG_CHANNEL_ID`: Your log channel ID (optional)

5. **Deploy**: Click "Create Background Worker"

The bot will automatically install Tesseract OCR and start running in the cloud! 🚀

### 3. Alternative: Local Development

**For local testing and development:**

```bash
pip install -r requirements.txt
```

**Note for Windows users**: You'll need to install Tesseract OCR separately:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to your PATH
3. The bot will automatically detect and configure Tesseract

### 4. Configure Environment Variables (Local Development Only)

**Note**: If you're using Render deployment, environment variables are set in the Render dashboard (step 4 above).

For local development:

1. Copy `.env.example` to `.env`
2. Edit `.env` with your bot's information:

```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_server_id_here
# Leave ALLOWED_ROLE_NAME empty to allow anyone with ANY role to post code
ALLOWED_ROLE_NAME=
# Admin roles (comma-separated for multiple roles)
ADMIN_ROLE_NAMES=Professor,Teaching Assistant (TA)
LOG_CHANNEL_ID=your_log_channel_id_here
```

**How to get these values:**
- **DISCORD_TOKEN**: From the Discord Developer Portal (Bot section)
- **GUILD_ID**: Right-click your server name → Copy Server ID (requires Developer Mode)
- **ALLOWED_ROLE_NAME**: Leave empty to allow anyone with a role to post code, or specify a specific role name
- **ADMIN_ROLE_NAMES**: Comma-separated list of roles that can use admin commands
- **LOG_CHANNEL_ID**: Right-click a channel → Copy Channel ID (optional)

### 5. Run the Bot (Local Development Only)

```bash
python bot.py
```

**Note**: If deployed to Render, the bot runs automatically in the cloud!

## 🎮 Commands

### For Everyone
- `!help_classbot` - Display help information about the bot

### For Administrators
- `!remove_roleless` - Remove all users without any role (shows confirmation dialog)
- `!warnings @user` - Check warnings for a specific user
- `!clear_warnings @user` - Clear all warnings for a specific user
- `!clear_channel #channel [limit]` - Delete all messages in specified channel (with confirmation)

## 🔧 How It Works

### Code Detection

The bot uses multiple methods to detect code:

1. **Text Pattern Matching**: Looks for programming keywords, syntax patterns, and code structures
2. **Image OCR**: Extracts text from uploaded images and analyzes it for code
   - **Fallback Behavior**: When OCR is unavailable, the bot will alert about any image posts from users without roles
   - **Text Detection**: Always works independently of OCR status
3. **Heuristic Analysis**: Considers indentation, punctuation, and formatting patterns

### Detection Patterns Include:
- Programming keywords (def, class, import, function, var, etc.)
- Code syntax (brackets, semicolons, operators)
- Comments (// /* */ #)
- Function calls and variable assignments
- SQL queries
- HTML tags

### User Workflow

1. User without required role posts a message with code
2. Bot detects code and immediately deletes the message
3. Bot sends a warning to the user with their current warning count
4. Action is logged to the admin channel (if configured)

### Enhanced Features for Production

#### 🔄 **Persistent Warning System**
- **File-based Storage**: Warnings saved to `warnings.json` - survives bot restarts and deployment updates
- **Auto-Expiration**: Warnings automatically expire after 30 days to keep system clean
- **Timestamp Tracking**: Each warning includes date/time for admin reference
- **Efficient Cleanup**: Automatic cleanup of expired warnings during operations

#### 🛡️ **Enhanced Error Recovery**
- **Automatic Reconnection**: Bot automatically reconnects if connection drops
- **Graceful Error Handling**: Comprehensive error catching prevents crashes
- **Self-Healing**: Automatic restart with exponential backoff on critical errors
- **Data Safety**: Warnings automatically saved before any restart attempts
- **Production Ready**: Optimized for cloud deployment platforms like Render

#### ⚡ **Performance Optimizations**
- **Fast Channel Clearing**: Bulk delete operations up to 10x faster
- **Efficient OCR Fallback**: Smart handling when image processing unavailable
- **Minimal Memory Usage**: Persistent storage reduces RAM requirements
- **Quick Recovery**: Sub-second reconnection times for brief network issues

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Your bot's token from Discord Developer Portal | Yes |
| `GUILD_ID` | Your Discord server ID | Yes |
| `ALLOWED_ROLE_NAME` | Role name that allows code posting | Yes |
| `ADMIN_ROLE_NAME` | Role name for bot administrators | Yes |
| `LOG_CHANNEL_ID` | Channel ID for logging bot actions | No |

### Customizing Code Detection

You can modify the code detection patterns in `bot.py`:

```python
CODE_PATTERNS = [
    # Add your custom patterns here
    r'your_custom_regex_pattern',
]
```

## 🛡️ Permissions Required

The bot needs the following Discord permissions:
- **View Channels**: To see messages
- **Send Messages**: To send warnings and responses
- **Manage Messages**: To delete code posts
- **Kick Members**: For the remove_roleless command
- **Embed Links**: To send rich embeds
- **Read Message History**: To process messages

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot is online in your server
   - Verify the token in your `.env` file
   - Ensure the bot has the required permissions

2. **Code not being detected**
   - The detection is heuristic-based and may have false negatives
   - Consider adjusting the `CODE_PATTERNS` list
   - Check if the user has the allowed role

3. **Image OCR not working**
   - **Automatic Fallback**: When OCR is unavailable, the bot automatically switches to alert mode for image posts
   - **Text Detection Unaffected**: Text-based code detection continues to work normally
   - **Installation Issues**: Ensure Tesseract is installed and in your PATH
   - Check if the image contains clear, readable text
   - Verify Pillow and pytesseract are installed correctly

4. **Permission errors**
   - Ensure the bot role is higher than the roles it needs to manage
   - Check that the bot has all required permissions

### Error Messages

- `"Bot lacks permission to delete messages"`: The bot role needs "Manage Messages" permission
- `"insufficient permissions"` in remove_roleless: The bot role needs "Kick Members" and must be higher than users being kicked

## 📝 Development

### Project Structure
```
Discord Bot/
├── main.py                     # 🚀 Main entry point
├── requirements.txt           # Python dependencies
├── runtime.txt               # Python version for deployment
├── render.yaml              # Render deployment configuration
├── Aptfile                  # System packages for deployment
├── README.md                # Documentation
│
├── src/                     # 📦 Source code
│   ├── bot/                 # 🤖 Main bot modules
│   │   ├── warning_system.py      # 💾 Persistent warnings with auto-expiration
│   │   ├── error_recovery.py      # 🛡️ Auto-reconnection & error handling
│   │   └── utils/               # 🔧 Utility modules
│   │       └── code_detection.py   # 🔍 Text & image code detection
│   └── config.py           # ⚙️ Configuration management
│
├── data/                   # 💾 Data storage (auto-created)
│   ├── warnings.json      # 📊 User warnings (persistent)
│   └── bot.log            # 📋 Application logs
│
├── tests/                  # 🧪 Test files
│   └── test_*.py          # Various test scripts
│
└── scripts/                # 📜 Deployment scripts
    ├── build.sh           # Build script
    └── start.sh           # Startup script
```

### Adding New Features

1. Code detection patterns can be added to the `CODE_PATTERNS` list
2. New commands should use the `@bot.command()` decorator
3. Admin-only commands should check `class_bot.has_admin_role(ctx.author)`

### Testing

Test the bot in a development server before deploying to production:
1. Create a test Discord server
2. Set up test roles and channels
3. Test code detection with various code samples
4. Test admin commands with appropriate permissions

## ☁️ Cloud Deployment Guide

### Render Deployment (Recommended)

1. **Prepare your repository**:
   ```bash
   # Make sure all files are committed
   git add .
   git commit -m "Initial bot setup"
   git push origin main
   ```

2. **Create Render service**:
   - Go to [render.com](https://render.com)
   - Click "New" → "Background Worker"
   - Connect your GitHub repository
   - Use these settings:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt && apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx libglib2.0-0`
     - **Start Command**: `python bot.py`

3. **Environment variables** (set in Render dashboard):
   ```
   DISCORD_TOKEN=your_bot_token_here
   GUILD_ID=your_server_id
   ALLOWED_ROLE_NAME=Student
   ADMIN_ROLE_NAME=Admin
   LOG_CHANNEL_ID=your_log_channel_id
   ```

4. **Deploy and monitor**:
   - Click "Create Background Worker"
   - Monitor logs in Render dashboard
   - Bot should show "Class Bot is ready!" when successful

### Alternative: Heroku Deployment

1. **Create Heroku app**:
   ```bash
   heroku create your-class-bot
   heroku config:set DISCORD_TOKEN=your_token_here
   heroku config:set GUILD_ID=your_guild_id
   # ... set other environment variables
   ```

2. **Add buildpacks**:
   ```bash
   heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
   heroku buildpacks:add --index 2 heroku/python
   ```

3. **Create Aptfile** for Tesseract:
   ```
   tesseract-ocr
   tesseract-ocr-eng
   libgl1-mesa-glx
   libglib2.0-0
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🐛 Cloud Deployment Troubleshooting

### Python Version Compatibility

**Render Requirements:**
- ✅ **Python 3.11.x**: Recommended and tested
- ✅ **Linux environment**: Render uses Ubuntu-based containers  
- ✅ **Tesseract OCR**: Automatically installed via apt-get
- 📋 **Runtime file**: `runtime.txt` specifies Python 3.11.9

### Common Render Issues

1. **Build fails with Python version error**:
   - Check that `runtime.txt` contains `python-3.11.9`
   - Verify no conflicting Python version specifications
   - Use build command with explicit pip upgrade

2. **Build fails with Tesseract error**:
   - Verify build command includes all apt-get installations
   - Check logs for specific missing packages
   - Ensure `libtesseract-dev` is included in build command

3. **Bot doesn't start**:
   - Verify all environment variables are set correctly
   - Check that DISCORD_TOKEN doesn't have extra spaces
   - Ensure GUILD_ID is numeric (no quotes)
   - Look for Python import errors in logs

4. **OCR not working**:
   - Check logs for Tesseract installation messages
   - The bot will automatically disable image detection if OCR fails
   - Text-based code detection will still work

4. **Bot goes offline randomly**:
   - This can happen with free Render plans
   - Consider upgrading to a paid plan for 24/7 uptime
   - The bot will automatically restart when it receives activity

### Monitoring Your Bot

1. **Check Render logs**:
   - Go to your service dashboard
   - Click on "Logs" to see real-time output
   - Look for "Class Bot is ready!" success message

2. **Discord status**:
   - Your bot should show as "Online" in your server
   - Test with a simple command like `!help_classbot`

3. **Test functionality**:
   - Try posting code without the required role
   - Test image upload detection
   - Verify admin commands work

## 📄 License

This project is provided as-is for educational purposes. Feel free to modify and adapt it to your needs.

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your configuration matches the setup guide
3. Check Render/deployment logs for errors
4. Ensure the bot has proper Discord permissions
5. Test locally first before deploying to cloud

## 🔄 Updates

### Cloud Deployment Updates:
1. Push changes to your GitHub repository
2. Render will automatically redeploy your bot
3. Monitor logs to ensure successful deployment

### Local Development Updates:
1. Pull the latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart the bot

---

**Happy moderating! 🎓**