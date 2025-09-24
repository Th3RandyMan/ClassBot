#!/bin/bash
# Start Discord bot in screen session

# Activate virtual environment
source venv/bin/activate

# Set UTF-8 encoding environment variables
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Start bot in detached screen session (unbuffered, proper encoding)
screen -dmS discord-bot python -u main.py

echo "✅ Discord bot started in screen session 'discord-bot'"
echo "📋 Use 'screen -r discord-bot' to attach to the session"
echo "📋 Use 'Ctrl+A, D' to detach from screen session"
echo "📋 Use 'screen -list' to see all sessions"
