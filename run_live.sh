#!/bin/bash
# SuperGrokSnipV1 - Live Trading Launcher
# ⚠️  REAL MONEY - USE WITH EXTREME CAUTION ⚠️

echo "===================================================================="
echo "  SuperGrokSnipV1 - LIVE TRADING MODE"
echo "  ⚠️  REAL MONEY - EXTREME CAUTION REQUIRED ⚠️"
echo "===================================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Warning
echo "⚠️  WARNING: This will trade REAL MONEY!"
echo "   Make sure you:"
echo "   1. Tested thoroughly with paper trading first"
echo "   2. Configured your wallet in .env"
echo "   3. Set appropriate investment amounts"
echo "   4. Understand the risks involved"
echo ""
read -p "Press ENTER to continue or Ctrl+C to cancel..."
echo ""

# Run live trading bot
python3 main_live.py

echo ""
echo "Session ended. Check logs in data/logs/ directory."
