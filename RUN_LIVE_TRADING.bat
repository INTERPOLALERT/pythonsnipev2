@echo off
REM SuperGrokSnipV1 - Live Trading Launcher
REM Windows Python-Only Version
REM WARNING: REAL MONEY - USE WITH EXTREME CAUTION

echo ================================================================
echo   SuperGrokSnipV1 - LIVE TRADING MODE
echo   WARNING: REAL MONEY - EXTREME CAUTION REQUIRED
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13 from python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found
    echo Please create .env file with your wallet details
    echo Copy from .env.example and edit it
    pause
    exit /b 1
)

echo LIVE TRADING MODE - REAL MONEY
echo.
echo This bot will trade REAL cryptocurrency on the blockchain.
echo You can LOSE all funds you allocate to trading.
echo.
echo Press Ctrl+C at any time to stop the bot.
echo.
pause

REM Run the live trading bot
python main_live.py

REM Pause at the end so user can see any errors
echo.
echo Bot stopped.
pause
