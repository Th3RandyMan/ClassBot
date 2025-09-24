#!/bin/bash
# View live bot logs

LOG_FILE="/mnt/c/Users/rlfowler/Documents/TA/Discord Bot/bot.log"

echo "📋 Viewing live Discord bot logs..."
echo "Press Ctrl+C to stop viewing"
echo "=================================="

if [ -f "$LOG_FILE" ]; then
    tail -f "$LOG_FILE"
else
    echo "❌ Log file not found: $LOG_FILE"
    echo "Make sure the bot is running with ./start_bot.sh"
fi