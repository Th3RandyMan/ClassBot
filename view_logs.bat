@echo off
chcp 65001 >nul
REM View live Discord bot logs from Windows (UTF-8 support)
echo 📋 Viewing live Discord bot logs...
echo Press Ctrl+C to stop viewing
echo ==================================

if exist "bot.log" (
    powershell -Command "$OutputEncoding = [System.Text.Encoding]::UTF8; Get-Content bot.log -Wait -Tail 10 -Encoding UTF8"
) else (
    echo ❌ Log file not found: bot.log
    echo Make sure the bot is running
    pause
)