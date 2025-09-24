@echo off
REM Windows Discord Bot Deployment Script
echo 🤖 Setting up Discord Bot for Windows deployment...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python from python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing Python packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file from example if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from example...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your actual Discord bot credentials!
)

REM Create startup batch file
echo @echo off > start_bot.bat
echo call venv\Scripts\activate.bat >> start_bot.bat
echo python main.py >> start_bot.bat

REM Create background startup file
echo @echo off > start_bot_background.bat
echo call venv\Scripts\activate.bat >> start_bot_background.bat
echo start /min python main.py >> start_bot_background.bat

echo.
echo 🎉 Windows setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your Discord bot credentials
echo 2. Run start_bot.bat to start the bot
echo 3. Or run start_bot_background.bat to start in background
echo.
pause