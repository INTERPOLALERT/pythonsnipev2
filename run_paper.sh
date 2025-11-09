#!/bin/bash
# SuperGrokSnipV1 - Paper Trading Launcher
# Safe testing with REAL prices, NO trades executed

echo "===================================================================="
echo "  SuperGrokSnipV1 - PAPER TRADING MODE"
echo "  Safe Testing with REAL Market Prices"
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

# Run paper trading bot
python3 main_paper.py

echo ""
echo "Session ended. Check logs in data/logs/ directory."
