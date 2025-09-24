#!/bin/bash
# Start Discord bot in screen session

# Activate virtual environment
source venv/bin/activate

# Start bot in detached screen session (log to Windows directory)
screen -dmS discord-bot python main.py > "/mnt/c/Users/rlfowler/Documents/TA/Discord Bot/bot.log" 2>&1

echo "✅ Discord bot started in screen session 'discord-bot'"
echo "📋 Use 'screen -r discord-bot' to attach to the session"
echo "📋 Use 'Ctrl+A, D' to detach from screen session"
echo "📋 Use 'screen -list' to see all sessions"
