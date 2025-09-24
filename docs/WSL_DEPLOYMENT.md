# WSL Discord Bot Deployment Guide

## 🚀 Running Your Discord Bot on WSL with Screen

This guide helps you deploy your Discord bot locally using WSL (Windows Subsystem for Linux) with `screen` for persistent background operation.

### Prerequisites
- Windows 10/11 with WSL2 installed
- Your Discord bot token and server IDs ready

### Quick Setup

1. **Open WSL terminal** and navigate to your bot directory
2. **Run the setup script**:
   ```bash
   chmod +x scripts/wsl_deploy.sh
   ./scripts/wsl_deploy.sh
   ```

3. **Configure your bot**:
   ```bash
   nano .env
   ```
   Add your Discord credentials:
   ```
   DISCORD_TOKEN=your_actual_discord_bot_token
   GUILD_ID=your_server_id
   LOG_CHANNEL_ID=your_log_channel_id
   ```

4. **Start your bot**:
   ```bash
   ./start_bot.sh
   ```

### Managing Your Bot

| Command | Purpose |
|---------|---------|
| `./start_bot.sh` | Start bot in background |
| `./stop_bot.sh` | Stop the bot |
| `./check_bot.sh` | Check if bot is running |
| `screen -r discord-bot` | View live logs |
| `Ctrl+A, D` | Detach from screen (keeps bot running) |
| `screen -list` | See all screen sessions |

### Advantages of WSL Deployment

✅ **No cost** - Runs on your own hardware  
✅ **Always available** - No time limits or usage restrictions  
✅ **Full control** - Direct access to logs and configuration  
✅ **Easy updates** - Instant code changes and restarts  
✅ **Better debugging** - Real-time error tracking  
✅ **OCR support** - Full Tesseract integration  

### Auto-Start on System Boot (Optional)

To automatically start your bot when Windows starts:

1. Create a startup script:
   ```bash
   nano ~/start_discord_bot_on_boot.sh
   ```

2. Add this content:
   ```bash
   #!/bin/bash
   cd "/path/to/your/Discord Bot"
   ./start_bot.sh
   ```

3. Add to your WSL shell profile:
   ```bash
   echo 'bash ~/start_discord_bot_on_boot.sh' >> ~/.bashrc
   ```

### Troubleshooting

**Bot not starting?**
- Check `.env` file has correct credentials
- Verify virtual environment: `source venv/bin/activate`
- Check logs: `screen -r discord-bot`

**Screen session issues?**
- List all sessions: `screen -list`
- Kill hung session: `screen -S discord-bot -X quit`
- Restart: `./start_bot.sh`

**Permission errors?**
- Make scripts executable: `chmod +x *.sh`
- Check file ownership: `ls -la`

### Performance Tips

- **Memory usage**: WSL uses minimal resources for Python bots
- **Network**: Direct connection often faster than cloud hosting
- **Storage**: Unlimited logs and data storage
- **Updates**: `git pull` and restart for instant updates

Your Discord bot will run reliably 24/7 on your local machine! 🎉