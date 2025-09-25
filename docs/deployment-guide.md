# 🚀 Discord Bot Deployment Guide

This guide covers all deployment options for the Class Bot, including cloud platforms and local setup.

## ☁️ Cloud Deployment (Recommended)

### Render Deployment (Primary Recommendation)

Render provides easy deployment with automatic Tesseract OCR setup and reliable uptime.

#### Step-by-Step Setup

1. **Prepare your repository**:
   ```bash
   # Make sure all files are committed
   git add .
   git commit -m "Initial bot setup"
   git push origin main
   ```

2. **Create Render service**:
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
   - **Start Command**: `python main.py`

4. **Set Environment Variables** in Render dashboard:
   - `DISCORD_TOKEN`: Your bot token from Discord Developer Portal
   - `GUILD_ID`: Your Discord server ID
   - `ALLOWED_ROLE_NAME`: Leave empty (allows anyone with a role to post code)
   - `ADMIN_ROLE_NAMES`: `Professor,Teaching Assistant (TA)` (comma-separated admin roles)
   - `LOG_CHANNEL_ID`: Your log channel ID (optional)

5. **Deploy**: Click "Create Background Worker"

The bot will automatically install Tesseract OCR and start running in the cloud! 🚀

#### Render Configuration Files

The repository includes configuration files for Render:

- **`render.yaml`**: Deployment configuration
- **`Aptfile`**: System packages (Tesseract OCR)
- **`runtime.txt`**: Python version specification
- **`requirements.txt`**: Python dependencies

### Heroku Deployment (Alternative)

Heroku is another reliable cloud platform with good Discord bot support.

#### Setup Steps

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-class-bot-name
   ```

3. **Add buildpacks** (in this order):
   ```bash
   heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
   heroku buildpacks:add --index 2 heroku/python
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set DISCORD_TOKEN=your_token_here
   heroku config:set GUILD_ID=your_guild_id
   heroku config:set ALLOWED_ROLE_NAME=Student
   heroku config:set ADMIN_ROLE_NAMES="Professor,Teaching Assistant (TA)"
   heroku config:set LOG_CHANNEL_ID=your_log_channel_id
   ```

5. **Create Aptfile** for Tesseract (already included):
   ```
   tesseract-ocr
   tesseract-ocr-eng
   libgl1-mesa-glx
   libglib2.0-0
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

7. **Scale up the worker**:
   ```bash
   heroku ps:scale worker=1
   ```

### Other Cloud Platforms

#### Railway

1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Railway will automatically detect and deploy Python applications

#### DigitalOcean App Platform

1. Create a new app from your GitHub repository
2. Choose "Worker" as the component type
3. Set build and run commands similar to Render
4. Configure environment variables

## 💻 Local Development Setup

For testing and development on your personal machine.

### Windows Setup

1. **Install Python 3.11+**:
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to your PATH
   - Verify installation: `tesseract --version`

3. **Clone and setup the project**:
   ```cmd
   git clone <your-repo-url>
   cd Discord Bot
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your Discord bot credentials

5. **Run the bot**:
   ```cmd
   python main.py
   ```

### macOS Setup

1. **Install Python and Tesseract**:
   ```bash
   # Using Homebrew
   brew install python tesseract
   ```

2. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd "Discord Bot"
   pip3 install -r requirements.txt
   ```

3. **Configure and run**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   python3 main.py
   ```

### Linux Setup (Ubuntu/Debian)

1. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx libglib2.0-0
   ```

2. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd "Discord Bot"
   pip3 install -r requirements.txt
   ```

3. **Configure and run**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   python3 main.py
   ```

### Environment Configuration

Create a `.env` file with the following variables:

```env
# Required
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_server_id_here

# Optional - Leave ALLOWED_ROLE_NAME empty to allow anyone with ANY role
ALLOWED_ROLE_NAME=

# Admin roles (comma-separated)
ADMIN_ROLE_NAMES=Professor,Teaching Assistant (TA)

# Optional logging
LOG_CHANNEL_ID=your_log_channel_id_here
```

**How to get these values:**
- **DISCORD_TOKEN**: From Discord Developer Portal > Bot section
- **GUILD_ID**: Right-click your server name → Copy Server ID (requires Developer Mode)
- **ALLOWED_ROLE_NAME**: Leave empty to allow anyone with a role, or specify role name
- **ADMIN_ROLE_NAMES**: Comma-separated list of admin roles
- **LOG_CHANNEL_ID**: Right-click a channel → Copy Channel ID (optional)

## 🐛 Troubleshooting

### Python Version Compatibility

**Cloud Platform Requirements:**
- ✅ **Python 3.11.x**: Recommended and tested
- ✅ **Linux environment**: Most platforms use Ubuntu-based containers  
- ✅ **Tesseract OCR**: Must be installed via system packages
- 📋 **Runtime file**: `runtime.txt` should specify `python-3.11.9`

### Common Cloud Deployment Issues

#### 1. Build Failures

**Python version errors**:
- Ensure `runtime.txt` contains `python-3.11.9`
- Verify no conflicting Python version specifications
- Check platform-specific Python version support

**Tesseract installation errors**:
- Verify build command includes all required apt-get packages
- Check logs for specific missing dependencies
- Ensure build command runs before start command

**Dependency errors**:
- Make sure `requirements.txt` is up to date
- Check for platform-specific package conflicts
- Try pinning specific versions if needed

#### 2. Runtime Issues

**Bot doesn't start**:
- Verify all environment variables are set correctly
- Check that DISCORD_TOKEN doesn't have extra spaces or quotes
- Ensure GUILD_ID is numeric (no quotes in environment variable)
- Look for Python import errors in deployment logs

**Bot goes offline randomly**:
- Free tier limitations on some platforms
- Consider upgrading to paid plans for 24/7 uptime
- Bot will automatically restart when it receives activity

**Permission errors**:
- Ensure bot has all required Discord permissions
- Check that bot role is higher than roles it needs to manage
- Verify OAuth2 URL generator included all necessary permissions

#### 3. Feature-Specific Issues

**OCR not working**:
- Check deployment logs for Tesseract installation messages
- Bot automatically disables image detection if OCR fails
- Text-based code detection continues working independently
- Verify all Tesseract dependencies are installed

**Commands not responding**:
- Check if bot has "Send Messages" permission
- Verify command prefix is correct (default: `!`)
- Ensure bot can see the channel (View Channels permission)

### Local Development Issues

#### 1. Installation Problems

**Windows - Tesseract not found**:
```cmd
# Download and install Tesseract from official source
# Add installation directory to PATH
# Common paths:
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

**macOS - Permission errors**:
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Linux - Package conflicts**:
```bash
# Install system packages first
sudo apt install tesseract-ocr tesseract-ocr-eng
# Then Python packages
pip3 install --user -r requirements.txt
```

#### 2. Runtime Problems

**Import errors**:
- Make sure you're in the correct directory
- Check Python version: `python --version`
- Verify all dependencies installed: `pip list`

**Token errors**:
- Double-check `.env` file exists and has correct format
- Verify no extra spaces in environment variables
- Ensure Discord token is valid and bot is in server

### Monitoring and Maintenance

#### 1. Health Checks

**Verify bot status**:
- Bot shows as "Online" in Discord server member list
- Test basic command: `!help`
- Check admin commands work properly

**Monitor logs**:
- Cloud platforms: Check service dashboard logs
- Local development: Console output and `bot.log` file
- Look for connection issues or error patterns

#### 2. Updates and Maintenance

**Cloud deployment updates**:
1. Push changes to connected repository
2. Platform automatically redeploys
3. Monitor logs during deployment
4. Verify functionality after deployment

**Local development updates**:
1. Pull latest changes: `git pull`
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart bot process
4. Test functionality

#### 3. Performance Monitoring

**Resource usage**:
- Monitor memory usage on cloud platforms
- Check CPU usage during high activity
- Monitor network connectivity stability

**Discord API limits**:
- Bot automatically handles rate limiting
- Monitor for 429 (rate limit) errors in logs
- Consider implementing additional rate limiting if needed

## 🔄 Platform Migration

If you need to migrate between deployment platforms:

1. **Export environment variables** from current platform
2. **Set up new platform** following respective guide above  
3. **Configure environment variables** on new platform
4. **Test deployment** before switching DNS/domains
5. **Monitor logs** for successful migration

## 📞 Support Resources

- **Discord.py Documentation**: https://discordpy.readthedocs.io/
- **Render Support**: https://render.com/docs
- **Heroku Support**: https://devcenter.heroku.com/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract

---

**Happy deploying! 🚀**