#!/bin/bash
# Check if Discord bot is running
LOG_FILE="/mnt/c/Users/rlfowler/Documents/TA/Discord Bot/bot.log"

if screen -list | grep -q "discord-bot"; then
    echo "✅ Discord bot is running"
    echo "📋 Use 'screen -r discord-bot' to view live session"
    echo "📋 Use './view_logs.sh' to view live logs"
    
    # Show last few log entries if available
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "🔍 Recent log entries:"
        tail -5 "$LOG_FILE"
    fi
else
    echo "❌ Discord bot is not running"
    echo "📋 Use './start_bot.sh' to start the bot"
fi
