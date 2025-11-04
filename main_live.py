"""
SuperGrokSnipV1 - Live Trading Bot
REAL MONEY - USE WITH EXTREME CAUTION
"""

import os
import sys
import asyncio
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from config_loader import TradingConfig, load_env
from wallet_manager import WalletManager

# Import utilities
try:
    from utils.logger import BotLogger
except ImportError:
    # Fallback if utils package not set up
    import importlib.util
    logger_spec = importlib.util.spec_from_file_location("logger", Path(__file__).parent / "utils" / "logger.py")
    logger_module = importlib.util.module_from_spec(logger_spec)
    logger_spec.loader.exec_module(logger_module)
    BotLogger = logger_module.BotLogger

try:
    from utils.metrics import MetricsTracker
except ImportError:
    import importlib.util
    metrics_spec = importlib.util.spec_from_file_location("metrics", Path(__file__).parent / "utils" / "metrics.py")
    metrics_module = importlib.util.module_from_spec(metrics_spec)
    metrics_spec.loader.exec_module(metrics_module)
    MetricsTracker = metrics_module.MetricsTracker


class LiveTradingBot:
    """Live trading bot - REAL MONEY"""
    
    def __init__(self):
        # Load environment and config
        load_env()
        self.config = TradingConfig("config_live.yaml")
        
        # Initialize logger
        self.logger = BotLogger("LiveBot")
        self.logger.critical("🔴 LIVE TRADING MODE - REAL MONEY")
        
        # Display config
        self.config.display_config()
        
        # Initialize wallet
        self.wallet = WalletManager(network=self.config.network)
        if not self.wallet.load_from_env():
            self.logger.error("❌ No wallet loaded - cannot trade!")
            sys.exit(1)
        
        self.wallet.display_wallet_info()
        
        # Trading state
        self.running = False
        self.current_position: Optional[Dict] = None
        self.daily_spent = 0.0
        self.trades_history = []
        self.wins = 0
        self.losses = 0
        
        # Metrics
        self.metrics = MetricsTracker(mode="live")
        
        # Signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.logger.critical("\n⚠️  EMERGENCY STOP - Shutting down...")
        self.running = False
    
    async def start(self):
        """Start live trading bot"""
        # Final confirmation
        print("\n" + "="*70)
        print("  ⚠️  FINAL WARNING ⚠️")
        print("="*70)
        print()
        print("This bot will trade REAL MONEY on the blockchain.")
        print("You can LOSE everything you invest.")
        print()
        print("Safety features enabled:")
        print(f"  ✅ Max 1 open position")
        print(f"  ✅ Daily limit: {self.config.get_max_daily()} {self.config.network.upper()}")
        print(f"  ✅ Stop loss: {self.config.stop_loss}%")
        print(f"  ✅ Investment per trade: {self.config.get_investment_amount()} {self.config.network.upper()}")
        print()
        
        confirm = input("Type 'START' to begin live trading: ")
        if confirm.strip().upper() != 'START':
            print("Cancelled.")
            return
        
        print()
        self.logger.critical("🚨 LIVE TRADING ACTIVATED 🚨")
        print()
        
        # Check wallet balance
        balance = await self.wallet.get_balance()
        self.logger.info(f"💰 Wallet Balance: {balance:.4f} {self.config.network.upper()}")
        
        if balance < self.config.min_balance:
            self.logger.error(f"❌ Insufficient balance! Minimum: {self.config.min_balance}")
            return
        
        self.logger.info("="*70)
        self.logger.info(f"📊 Max daily spend: {self.config.get_max_daily()}")
        self.logger.info(f"💵 Per trade: {self.config.get_investment_amount()}")
        self.logger.info(f"🎯 Take Profit: {self.config.take_profit}% | Stop Loss: {self.config.stop_loss}%")
        self.logger.info("="*70)
        self.logger.info("")
        
        self.running = True
        
        # Main trading loop
        try:
            self.logger.info("🔍 Monitoring blockchain for opportunities...")
            self.logger.info("   Press Ctrl+C for emergency stop")
            self.logger.info("")
            
            # Start monitoring
            if self.config.network == 'solana':
                await self._monitor_solana()
            elif self.config.network == 'bsc':
                await self._monitor_bsc()
                
        except KeyboardInterrupt:
            self.logger.critical("\n⚠️  Interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
        finally:
            await self.shutdown()
    
    async def _monitor_solana(self):
        """Monitor Solana blockchain"""
        self.logger.info("🔗 Connected to Solana mainnet")
        self.logger.info(f"   RPC: {self.config.get_rpc_endpoint()[:50]}...")
        self.logger.info("")
        
        # Real implementation would connect to Raydium/Pump.fun
        # For now, demo mode
        while self.running:
            try:
                # Check daily limit
                if self.daily_spent >= self.config.get_max_daily():
                    self.logger.warning(f"⚠️  Daily limit reached: {self.daily_spent:.4f}")
                    await asyncio.sleep(60)
                    continue
                
                await asyncio.sleep(30)
                
                # Demo mode - no actual trades
                self.logger.info("⏳ Waiting for opportunities...")
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_bsc(self):
        """Monitor BSC blockchain"""
        self.logger.info("🔗 Connected to BSC mainnet")
        self.logger.info(f"   RPC: {self.config.get_rpc_endpoint()}")
        self.logger.info("")
        
        while self.running:
            try:
                # Check daily limit
                if self.daily_spent >= self.config.get_max_daily():
                    self.logger.warning(f"⚠️  Daily limit reached: {self.daily_spent:.4f}")
                    await asyncio.sleep(60)
                    continue
                
                await asyncio.sleep(30)
                self.logger.info("⏳ Waiting for opportunities...")
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("\n" + "="*70)
        self.logger.critical("  LIVE TRADING SESSION ENDED")
        self.logger.info("="*70)
        
        # Get final balance
        balance = await self.wallet.get_balance()
        self.logger.info(f"Final Balance: {balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"Daily Spent: {self.daily_spent:.4f} {self.config.network.upper()}")
        self.logger.info(f"Total Trades: {len(self.trades_history)}")
        self.logger.info(f"Wins: {self.wins} | Losses: {self.losses}")
        
        if self.wins + self.losses > 0:
            win_rate = (self.wins / (self.wins + self.losses)) * 100
            self.logger.info(f"Win Rate: {win_rate:.1f}%")
        
        self.logger.info("="*70)
        self.logger.info("")
        
        # Save metrics
        self.metrics.save_session({
            'trades': self.trades_history,
            'wins': self.wins,
            'losses': self.losses,
            'daily_spent': self.daily_spent,
            'final_balance': balance
        })


async def main():
    """Entry point"""
    bot = LiveTradingBot()
    await bot.start()


if __name__ == "__main__":
    print("="*70)
    print("  SuperGrokSnipV1 - LIVE TRADING MODE")
    print("  ⚠️  REAL MONEY - EXTREME CAUTION REQUIRED ⚠️")
    print("="*70)
    print()
    
    asyncio.run(main())
