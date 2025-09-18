@echo off
REM Virtual Try-On Startup Script for Windows

echo 🎨 Starting Bharat Heritage Virtual Try-On...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️ Setting up environment...
    python setup.py
    echo ❗ Please edit the .env file with your Google Cloud project details before running the app.
    pause
    exit /b 1
)

REM Start the application
echo 🚀 Starting Virtual Try-On application...
python app.py

pause