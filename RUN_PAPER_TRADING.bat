@echo off
REM SuperGrokSnipV1 - Paper Trading Launcher
REM Windows Python-Only Version

echo ================================================================
echo   SuperGrokSnipV1 - PAPER TRADING MODE
echo   Safe Testing with REAL Market Prices
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
    echo Warning: Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found
    echo Copying from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your wallet details before running again
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Starting Paper Trading Bot...
echo.

REM Run the paper trading bot
python main_paper.py

REM Pause at the end so user can see any errors
echo.
echo Bot stopped.
pause
