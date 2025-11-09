@echo off
REM SuperGrokSnipV1 - Automatic Setup for Windows
REM Python 3.13 Compatible - Pure Python, No Git Required
REM All files are already in place - this script sets up dependencies

color 0B
title SuperGrokSnipV1 - Setup

echo ============================================================
echo   SUPERGROKSNIPV1 - SETUP
echo   Python 3.13 Edition - Windows Only
echo ============================================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator
    echo Some operations may fail without admin rights
    echo.
    echo Recommendation: Right-click and select "Run as administrator"
    echo.
    pause
)

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Install Python 3.13 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Verify directory structure
echo [2/6] Verifying directory structure...
if not exist "src" (
    echo ERROR: src directory not found!
    echo Please make sure you have all files in the correct location
    pause
    exit /b 1
)
if not exist "config" (
    echo ERROR: config directory not found!
    pause
    exit /b 1
)

REM Create data directories
if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs
if not exist "data\trades" mkdir data\trades
if not exist "data\models" mkdir data\models
if not exist "data\historical" mkdir data\historical

echo Directory structure verified
echo.

REM Check if .env exists
echo [3/6] Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo Created .env from template
        echo ⚠️  IMPORTANT: Edit .env file with your wallet details!
    ) else (
        echo ERROR: .env.example not found
        pause
        exit /b 1
    )
) else (
    echo .env file already exists
)
echo.

REM Create or verify virtual environment
echo [4/6] Setting up virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    echo Creating virtual environment...
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
echo [5/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install dependencies
echo [6/6] Installing Python packages...
echo This may take 5-10 minutes depending on your internet speed...
echo.
echo Installing core packages...

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo.
    echo WARNING: Some packages failed to install
    echo This might happen with Python 3.13 on some systems
    echo.
    echo Trying essential packages individually...
    echo.

    REM Install core packages individually
    echo Installing core dependencies...
    pip install python-dotenv pyyaml aiohttp websockets --quiet

    echo Installing blockchain SDKs...
    pip install solders solana base58 anchorpy --quiet
    pip install web3 eth-account eth-utils hexbytes --quiet

    echo Installing data science packages...
    pip install numpy pandas scikit-learn --quiet

    echo Installing AI/ML packages...
    pip install torch torchvision networkx --quiet

    echo Installing utilities...
    pip install colorama rich python-dateutil --quiet
    pip install cryptography requests mnemonic --quiet

    echo.
    echo Package installation completed
    echo Some packages may have warnings - this is usually OK
) else (
    echo.
    echo ✅ All packages installed successfully!
)
echo.

REM Final summary
color 0A
echo ============================================================
echo   ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo Your bot is ready to use!
echo.
echo NEXT STEPS:
echo.
echo 1. Configure your wallet:
echo    - Edit .env file in this directory
echo    - Add your WALLET_PRIVATE_KEY or WALLET_SEED_PHRASE
echo    - Your Helius API key is already configured
echo.
echo 2. Adjust trading settings:
echo    - Edit config\config_live.yaml for live trading
echo    - Edit config\config_paper.yaml for paper trading
echo    - Set your investment amounts and risk parameters
echo.
echo 3. Test with paper trading (RECOMMENDED):
echo    - Double-click: RUN_PAPER_TRADING.bat
echo    - Uses real market data but NO real trades
echo    - Perfect for testing strategies safely
echo.
echo 4. Go live (when ready):
echo    - Double-click: RUN_LIVE_TRADING.bat
echo    - ⚠️  REAL MONEY - USE WITH CAUTION
echo    - Start with small amounts (0.01-0.05 SOL/BNB)
echo.
echo ============================================================
echo   FILE STRUCTURE
echo ============================================================
echo.
echo Root directory: %CD%
echo   ├── RUN_PAPER_TRADING.bat    (Start paper trading)
echo   ├── RUN_LIVE_TRADING.bat     (Start live trading)
echo   ├── setup.bat                (This file)
echo   ├── .env                     (Your configuration)
echo   ├── config\                  (Trading settings)
echo   ├── src\                     (Bot code)
echo   ├── data\                    (Logs and trades)
echo   └── venv\                    (Python environment)
echo.
echo ============================================================
echo   SAFETY REMINDERS
echo ============================================================
echo.
echo ⚠️  Always start with paper trading first
echo ⚠️  Begin with small amounts (0.01-0.05 SOL/BNB)
echo ⚠️  Never invest more than you can afford to lose
echo ⚠️  Keep your private keys secure and never share them
echo ⚠️  Monitor the bot regularly, especially during live trading
echo ⚠️  Crypto trading is extremely risky
echo.
echo ============================================================
echo.
pause
