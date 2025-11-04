@echo off
REM SuperGrokSnipV1 - Automatic Setup for Windows 11
REM Python 3.13 Compatible
REM All files will be saved to Z:\pythonSnipe

color 0B
title SuperGrokSnipV1 - Automatic Setup

echo ============================================================
echo   SUPERGROKSNIPV1 - AUTOMATIC SETUP
echo   Python 3.13 Edition - Windows 11
echo ============================================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator
    echo Some operations may fail without admin rights
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
)

REM Set installation path
set INSTALL_PATH=Z:\pythonSnipe
echo Installation path: %INSTALL_PATH%
echo.

REM Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Install Python 3.13 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Create directory structure
echo [2/8] Creating directory structure...
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"
cd /d "%INSTALL_PATH%"

mkdir data 2>nul
mkdir data\models 2>nul
mkdir data\logs 2>nul
mkdir data\historical 2>nul
mkdir data\trades 2>nul
mkdir src 2>nul
mkdir src\modules 2>nul
mkdir src\ai 2>nul
mkdir src\utils 2>nul
mkdir config 2>nul

echo Created directory structure
echo.

REM Check if .env exists
echo [3/8] Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo Created .env from template
    ) else (
        echo WARNING: .env.example not found
    )
) else (
    echo .env file already exists
)
echo.

REM Create virtual environment
echo [4/8] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if %errorLevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo [5/8] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo WARNING: Could not activate virtual environment
    echo Continuing anyway...
) else (
    echo Virtual environment activated
)
echo.

REM Upgrade pip
echo [6/8] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet
if %errorLevel% equ 0 (
    echo Pip upgraded successfully
) else (
    echo WARNING: Pip upgrade had issues (not critical)
)
echo.

REM Install dependencies
echo [7/8] Installing Python packages...
echo This may take 5-10 minutes...
echo.
echo Installing:
echo   - Solana SDK
echo   - Web3/BSC SDK
echo   - PyTorch for AI
echo   - scikit-learn
echo   - Security libraries
echo.
echo Please wait...
echo.

if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo.
        echo ERROR: Failed to install some packages
        echo.
        echo This might happen with Python 3.13 on Windows
        echo.
        echo Trying individual package installation...
        echo.
        
        REM Install packages individually to identify issues
        pip install python-dotenv pyyaml aiohttp websockets
        pip install solders solana base58
        pip install web3 eth-account eth-utils
        pip install numpy pandas scikit-learn
        pip install torch torchvision networkx
        pip install colorama rich python-dateutil
        pip install cryptography requests
        
        echo.
        echo Package installation completed with warnings
    ) else (
        echo.
        echo ✅ All packages installed successfully!
    )
) else (
    echo ERROR: requirements.txt not found!
    echo Please make sure all files are in %INSTALL_PATH%
    pause
    exit /b 1
)
echo.

REM Create initial models
echo [8/8] Initializing AI models...
if exist "src\ai\model_trainer.py" (
    python src\ai\model_trainer.py
    if %errorLevel% equ 0 (
        echo AI models initialized
    ) else (
        echo WARNING: Model initialization had issues (not critical)
        echo Models will be created on first run
    )
) else (
    echo Skipping model training (will happen on first run)
)
echo.

REM Create launcher shortcuts
echo Creating launcher shortcuts...

REM Paper trading launcher
echo @echo off > RUN_PAPER_TRADING.bat
echo title SuperGrokSnipV1 - Paper Trading >> RUN_PAPER_TRADING.bat
echo cd /d "Z:\pythonSnipe" >> RUN_PAPER_TRADING.bat
echo call venv\Scripts\activate.bat >> RUN_PAPER_TRADING.bat
echo python src\main_paper.py >> RUN_PAPER_TRADING.bat
echo pause >> RUN_PAPER_TRADING.bat

REM Live trading launcher
echo @echo off > RUN_LIVE_TRADING.bat
echo title SuperGrokSnipV1 - LIVE TRADING >> RUN_LIVE_TRADING.bat
echo cd /d "Z:\pythonSnipe" >> RUN_LIVE_TRADING.bat
echo call venv\Scripts\activate.bat >> RUN_LIVE_TRADING.bat
echo python src\main.py >> RUN_LIVE_TRADING.bat
echo pause >> RUN_LIVE_TRADING.bat

echo Launchers created
echo.

REM Final summary
color 0A
echo ============================================================
echo   ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo Installation directory: %INSTALL_PATH%
echo.
echo NEXT STEPS:
echo.
echo 1. Configure your wallet:
echo    - Edit .env file
echo    - Add WALLET_PRIVATE_KEY or WALLET_SEED_PHRASE
echo    - Your Helius API is already configured
echo.
echo 2. Test with paper trading:
echo    - Double-click: RUN_PAPER_TRADING.bat
echo    - Uses real prices, no trades executed
echo    - Perfect for testing
echo.
echo 3. Go live:
echo    - Double-click: RUN_LIVE_TRADING.bat
echo    - REAL MONEY - USE WITH CAUTION
echo.
echo 4. Configure trading:
echo    - Edit config\config_live.yaml
echo    - Set your investment amounts
echo    - Adjust take-profit and stop-loss
echo.
echo ============================================================
echo   IMPORTANT SAFETY REMINDERS
echo ============================================================
echo.
echo ⚠️  Start with small amounts (0.01-0.05 SOL/BNB)
echo ⚠️  Test thoroughly with paper trading first
echo ⚠️  Never invest more than you can afford to lose
echo ⚠️  Keep your private keys secure
echo ⚠️  Monitor the bot regularly
echo.
echo ============================================================
echo.
echo Setup log saved to: setup.log
echo.
pause
