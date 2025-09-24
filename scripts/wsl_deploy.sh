#!/bin/bash
# WSL Discord Bot Deployment Script

echo "🤖 Setting up Discord Bot for WSL deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv screen tesseract-ocr tesseract-ocr-eng

# Install additional OCR languages if needed
# sudo apt install -y tesseract-ocr-all  # Uncomment for all languages

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual Discord bot credentials!"
fi

# Create screen session startup script
cat > start_bot.sh << 'EOF'
#!/bin/bash
# Start Discord bot in screen session

# Activate virtual environment
source venv/bin/activate

# Start bot in detached screen session
screen -dmS discord-bot python main.py

echo "✅ Discord bot started in screen session 'discord-bot'"
echo "📋 Use 'screen -r discord-bot' to attach to the session"
echo "📋 Use 'Ctrl+A, D' to detach from screen session"
echo "📋 Use 'screen -list' to see all sessions"
EOF

chmod +x start_bot.sh

# Create stop script
cat > stop_bot.sh << 'EOF'
#!/bin/bash
# Stop Discord bot screen session
screen -S discord-bot -X quit
echo "🛑 Discord bot stopped"
EOF

chmod +x stop_bot.sh

# Create status check script
cat > check_bot.sh << 'EOF'
#!/bin/bash
# Check if Discord bot is running
if screen -list | grep -q "discord-bot"; then
    echo "✅ Discord bot is running"
    echo "📋 Use 'screen -r discord-bot' to view logs"
else
    echo "❌ Discord bot is not running"
    echo "📋 Use './start_bot.sh' to start the bot"
fi
EOF

chmod +x check_bot.sh

echo ""
echo "🎉 WSL setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Discord bot credentials"
echo "2. Run './start_bot.sh' to start the bot in background"
echo "3. Use './check_bot.sh' to check if bot is running"
echo "4. Use 'screen -r discord-bot' to view live logs"
echo ""
echo "🔧 Useful commands:"
echo "   ./start_bot.sh   - Start bot in background"
echo "   ./stop_bot.sh    - Stop the bot"
echo "   ./check_bot.sh   - Check bot status"
echo "   screen -r discord-bot - View live logs"
echo "   Ctrl+A, D       - Detach from screen (bot keeps running)"