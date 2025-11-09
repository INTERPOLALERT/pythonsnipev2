#!/usr/bin/env python3
"""
Quick test to verify bot components work
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("  SuperGrokSnipV1 - Component Test")
print("="*70)
print()

# Test 1: Config Loader
print("Test 1: Config Loader...")
try:
    from config_loader import load_env, TradingConfig
    load_env()
    config = TradingConfig("config_paper.yaml")
    print(f"  ✅ Config loaded successfully")
    print(f"  Network: {config.network}")
    print(f"  Investment: {config.get_investment_amount()}")
except Exception as e:
    print(f"  ❌ Failed: {e}")
    sys.exit(1)

print()

# Test 2: Logger
print("Test 2: Logger...")
try:
    from utils.logger import BotLogger
    logger = BotLogger("TestBot")
    logger.info("Logger test message")
    print(f"  ✅ Logger working")
except Exception as e:
    print(f"  ❌ Failed: {e}")
    sys.exit(1)

print()

# Test 3: Metrics
print("Test 3: Metrics Tracker...")
try:
    from utils.metrics import MetricsTracker
    metrics = MetricsTracker("test")
    print(f"  ✅ Metrics tracker working")
except Exception as e:
    print(f"  ❌ Failed: {e}")
    sys.exit(1)

print()

# Test 4: Wallet Manager (optional - may fail if crypto libs not installed)
print("Test 4: Wallet Manager...")
try:
    from wallet_manager import WalletManager
    print(f"  ✅ Wallet manager imports (blockchain libs may still be missing)")
except Exception as e:
    print(f"  ⚠️  Wallet manager import failed: {e}")
    print(f"     This is okay for paper trading mode")

print()
print("="*70)
print("  Core components are working!")
print("  Bot is ready for paper trading (demo mode)")
print("="*70)
print()
print("Note: For full functionality with real blockchain connections,")
print("additional dependencies may be needed (solana, web3, etc.)")
print()
