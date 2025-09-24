#!/bin/bash
# Check if Discord bot is running
if screen -list | grep -q "discord-bot"; then
    echo "✅ Discord bot is running"
    echo "📋 Use 'screen -r discord-bot' to view logs"
else
    echo "❌ Discord bot is not running"
    echo "📋 Use './start_bot.sh' to start the bot"
fi
