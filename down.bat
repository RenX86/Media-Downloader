@echo off
echo Setting up Media Downloader...

REM Get the directory where the batch file is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Check if virtualenv is installed, install if not
pip show virtualenv >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing virtualenv...
    pip install virtualenv
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m virtualenv venv
)

REM Activate virtual environment and install requirements
echo Activating virtual environment and installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Start the Flask application
echo Starting Media Downloader...
start /B cmd /c "venv\Scripts\python.exe run.py"

REM Wait for the server to start
echo Waiting for server to start...
timeout /t 3 /nobreak >nul

REM Open the web app in the default browser
echo Opening Media Downloader in your browser...
start http://127.0.0.1:5000

echo Media Downloader is now running. Close this window to stop the application.
pause
taskkill /f /im python.exe >nul 2>&1
echo Application stopped.