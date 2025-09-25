# 💻 Personal Machine Setup Guide

Quick setup guide for running the Discord bot on your personal computer for development and testing.

## Prerequisites

- Python 3.11 or newer
- Git (for cloning the repository)
- Discord bot token and server access

## Platform-Specific Setup

### Windows

1. **Install Python**:
   - Download from [python.org](https://python.org)
   - ✅ **Important**: Check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **Install Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location
   - Add to PATH: `C:\Program Files\Tesseract-OCR`
   - Verify: `tesseract --version`

3. **Setup bot**:
   ```cmd
   git clone <your-repo-url>
   cd "Discord Bot"
   pip install -r requirements.txt
   ```

### macOS

1. **Install dependencies**:
   ```bash
   # Using Homebrew (install brew first if needed)
   brew install python tesseract git
   ```

2. **Setup bot**:
   ```bash
   git clone <your-repo-url>
   cd "Discord Bot"
   pip3 install -r requirements.txt
   ```

### Linux (Ubuntu/Debian)

1. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip tesseract-ocr tesseract-ocr-eng git libgl1-mesa-glx libglib2.0-0
   ```

2. **Setup bot**:
   ```bash
   git clone <your-repo-url>
   cd "Discord Bot"
   pip3 install -r requirements.txt
   ```

## Configuration

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   GUILD_ID=your_server_id_here
   ALLOWED_ROLE_NAME=
   ADMIN_ROLE_NAMES=Professor,Teaching Assistant (TA)
   LOG_CHANNEL_ID=your_log_channel_id_here
   ```

   **How to get these values**:
   - **DISCORD_TOKEN**: Discord Developer Portal > Your App > Bot > Token
   - **GUILD_ID**: Right-click server name in Discord > Copy Server ID
   - **LOG_CHANNEL_ID**: Right-click channel in Discord > Copy Channel ID

## Running the Bot

**Windows**:
```cmd
python main.py
```

**macOS/Linux**:
```bash
python3 main.py
```

**Success message**: Look for "Class Bot is ready!" in the console.

## Development Tips

### Recommended Development Workflow

1. **Test Server**: Create a separate Discord server for testing
2. **Version Control**: Use git branches for new features
3. **Virtual Environment**: Consider using Python virtual environments
4. **Log Monitoring**: Watch the console output and `bot.log` file

### Virtual Environment (Recommended)

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### IDE Setup

**VS Code Extensions (recommended)**:
- Python
- Discord.py Snippets
- GitLens

### Testing Your Changes

1. **Start the bot** in your test server
2. **Test basic functionality**: `!help`, `!classbot`
3. **Test code detection**: Post code without proper role
4. **Test admin commands**: Use admin commands if you have admin role
5. **Check logs**: Monitor console output for errors

## Common Issues

### Installation Problems

**"Python not found"**:
- Ensure Python is in your PATH
- Try `python3` instead of `python`
- Reinstall Python with PATH option checked

**"Tesseract not found"**:
- Verify Tesseract installation
- Check PATH configuration
- Bot will disable image detection if Tesseract unavailable

**"Permission denied" errors**:
- Use virtual environment
- On Linux/macOS: try `pip3 install --user`
- Check file permissions

### Runtime Issues

**Bot doesn't start**:
- Check `.env` file format (no extra quotes/spaces)
- Verify Discord token is valid
- Ensure bot is in your server

**Commands don't work**:
- Check bot permissions in Discord
- Verify bot can see/send messages in channel
- Check role hierarchy (bot role should be higher)

**OCR not working**:
- This is normal - bot will automatically disable image detection
- Text-based code detection will still work
- Check Tesseract installation if image detection needed

## Updating Your Bot

1. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

2. **Update dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart the bot**:
   - Stop with `Ctrl+C`
   - Start again with `python main.py`

## File Structure

Your local setup will look like:
```
Discord Bot/
├── main.py           # Start the bot
├── .env              # Your credentials (don't commit!)
├── bot.log           # Runtime logs
├── src/              # Bot source code
├── config/           # Configuration files
├── data/             # Runtime data
└── requirements.txt  # Dependencies
```

## Next Steps

Once your bot is running locally:

1. **Test all features** in your development server
2. **Make your changes** to the code
3. **Test thoroughly** before deploying
4. **Deploy to cloud** using the [Deployment Guide](deployment-guide.md)

## Getting Help

If you run into issues:
1. Check the error messages in console
2. Look at `bot.log` for detailed logs  
3. Verify Discord permissions and bot setup
4. See [Deployment Guide](deployment-guide.md) for detailed troubleshooting

---

**Happy coding! 🚀**