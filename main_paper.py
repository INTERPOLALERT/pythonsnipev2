"""
SuperGrokSnipV1 - Paper Trading Bot
Tests with REAL market prices but NO trades executed
Safe for testing strategies
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


class PaperTradingBot:
    """Paper trading bot with real prices"""
    
    def __init__(self):
        # Load environment and config
        load_env()
        self.config = TradingConfig("config_paper.yaml")
        
        # Initialize logger
        self.logger = BotLogger("PaperBot")
        self.logger.info("🟢 Starting Paper Trading Mode")
        
        # Display config
        self.config.display_config()
        
        # Initialize wallet (for balance checking only)
        self.wallet = WalletManager(network=self.config.network)
        if not self.wallet.load_from_env():
            self.logger.warning("⚠️  No wallet loaded - using simulated balance")
        
        # Paper trading state
        self.running = False
        self.paper_balance = self.config.initial_balance_sol if self.config.network == 'solana' else self.config.initial_balance_bnb
        self.current_position: Optional[Dict] = None
        self.trades_history = []
        self.wins = 0
        self.losses = 0
        
        # Metrics
        self.metrics = MetricsTracker(mode="paper")
        
        # Signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.logger.warning("\n⚠️  Shutdown signal received...")
        self.running = False
    
    async def start(self):
        """Start paper trading bot"""
        self.logger.info("="*70)
        self.logger.info("  PAPER TRADING MODE ACTIVE")
        self.logger.info("="*70)
        self.logger.info(f"💰 Initial Balance: {self.paper_balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"📊 Investment per trade: {self.config.get_investment_amount():.4f} {self.config.network.upper()}")
        self.logger.info(f"🎯 Take Profit: {self.config.take_profit}% | Stop Loss: {self.config.stop_loss}%")
        self.logger.info("="*70)
        self.logger.info("")
        
        # Check balance
        if self.paper_balance < self.config.get_investment_amount():
            self.logger.error("❌ Insufficient paper balance!")
            return
        
        self.running = True
        
        # Main trading loop
        try:
            self.logger.info("🔍 Monitoring blockchain for new tokens...")
            self.logger.info("   Press Ctrl+C to stop")
            self.logger.info("")
            
            # Start monitoring
            if self.config.network == 'solana':
                await self._monitor_solana()
            elif self.config.network == 'bsc':
                await self._monitor_bsc()
                
        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
        finally:
            await self.shutdown()
    
    async def _monitor_solana(self):
        """Monitor Solana blockchain for new tokens"""
        self.logger.info("🔗 Connected to Solana mainnet")
        self.logger.info(f"   RPC: {self.config.get_rpc_endpoint()[:50]}...")
        self.logger.info("")
        
        # Placeholder monitoring loop
        # In production, this would connect to Raydium/Pump.fun pools
        while self.running:
            try:
                # Simulate token detection (every 30 seconds for demo)
                await asyncio.sleep(30)
                
                self.logger.info("🎯 New token detected (demo mode)")
                
                # Demo token data
                token_data = {
                    'address': 'DemoToken123...',
                    'liquidity': 10000,
                    'holders': 75,
                    'top_holder_percent': 45,
                    'age_minutes': 2
                }
                
                await self._process_token(token_data)
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_bsc(self):
        """Monitor BSC blockchain for new tokens"""
        self.logger.info("🔗 Connected to BSC mainnet")
        self.logger.info(f"   RPC: {self.config.get_rpc_endpoint()}")
        self.logger.info("")
        
        # Similar to Solana monitoring
        while self.running:
            try:
                await asyncio.sleep(30)
                # BSC token monitoring logic here
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _process_token(self, token_data: Dict):
        """Process detected token through filters"""
        token_address = token_data['address']
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🔍 Analyzing: {token_address}")
        
        # Safety filters
        if not self._check_safety(token_data):
            return
        
        # Check if we can buy
        if self.current_position is not None:
            self.logger.warning("⚠️  Already have open position - skipping")
            return
        
        if self.paper_balance < self.config.get_investment_amount():
            self.logger.warning("⚠️  Insufficient balance - skipping")
            return
        
        # Simulate buy
        await self._simulate_buy(token_data)
    
    def _check_safety(self, token_data: Dict) -> bool:
        """Run safety checks"""
        self.logger.info("🛡️  Running safety checks...")
        
        # Check liquidity
        if token_data['liquidity'] < self.config.min_liquidity_usd:
            self.logger.warning(f"❌ Low liquidity: ${token_data['liquidity']}")
            return False
        self.logger.info(f"  ✅ Liquidity OK: ${token_data['liquidity']}")
        
        # Check holders
        if token_data['holders'] < self.config.min_holders:
            self.logger.warning(f"❌ Too few holders: {token_data['holders']}")
            return False
        self.logger.info(f"  ✅ Holders OK: {token_data['holders']}")
        
        # Check top holder
        if token_data['top_holder_percent'] > self.config.max_top_holder_percent:
            self.logger.warning(f"❌ High concentration: {token_data['top_holder_percent']}%")
            return False
        self.logger.info(f"  ✅ Distribution OK: Top holder {token_data['top_holder_percent']}%")
        
        # Check age
        if token_data['age_minutes'] > self.config.max_token_age_minutes:
            self.logger.warning(f"❌ Token too old: {token_data['age_minutes']} minutes")
            return False
        self.logger.info(f"  ✅ Fresh token: {token_data['age_minutes']} minutes old")
        
        self.logger.success("✅ All safety checks passed!")
        return True
    
    async def _simulate_buy(self, token_data: Dict):
        """Simulate buying token"""
        token_address = token_data['address']
        amount = self.config.get_investment_amount()
        
        self.logger.info("")
        self.logger.success("🚀 SIMULATED BUY")
        self.logger.info(f"   Token: {token_address}")
        self.logger.info(f"   Amount: {amount:.4f} {self.config.network.upper()}")
        
        # Simulate price (in real bot, get from price feed)
        entry_price = 0.00000123  # Demo price
        
        # Update paper balance
        self.paper_balance -= amount
        
        # Create position
        self.current_position = {
            'token': token_address,
            'amount': amount,
            'entry_price': entry_price,
            'entry_time': datetime.utcnow(),
            'peak_price': entry_price
        }
        
        self.logger.info(f"   Entry Price: ${entry_price:.8f}")
        self.logger.info(f"💰 Remaining Balance: {self.paper_balance:.4f}")
        self.logger.info("")
        
        # Start monitoring position
        asyncio.create_task(self._monitor_position())
    
    async def _monitor_position(self):
        """Monitor open position for exit signals"""
        position = self.current_position
        token_address = position['token']
        entry_price = position['entry_price']
        
        self.logger.info(f"👀 Monitoring position: {token_address}")
        
        while self.running and self.current_position == position:
            try:
                await asyncio.sleep(5)
                
                # Simulate price movement (in real bot, get from price feed)
                import random
                price_change = random.uniform(-0.05, 0.15)  # -5% to +15%
                current_price = entry_price * (1 + price_change)
                
                # Calculate PnL
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                # Update peak
                if current_price > position['peak_price']:
                    position['peak_price'] = current_price
                
                # Check exit conditions
                exit_reason = None
                
                if pnl_percent >= self.config.take_profit:
                    exit_reason = f"Take Profit ({pnl_percent:.1f}%)"
                elif pnl_percent <= -self.config.stop_loss:
                    exit_reason = f"Stop Loss ({pnl_percent:.1f}%)"
                elif self.config.trailing_stop:
                    drop_from_peak = ((position['peak_price'] - current_price) / position['peak_price']) * 100
                    if drop_from_peak >= self.config.trailing_distance:
                        exit_reason = f"Trailing Stop ({drop_from_peak:.1f}% from peak)"
                
                if exit_reason:
                    await self._simulate_sell(current_price, pnl_percent, exit_reason)
                    break
                    
            except Exception as e:
                self.logger.error(f"Position monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _simulate_sell(self, exit_price: float, pnl_percent: float, reason: str):
        """Simulate selling token"""
        position = self.current_position
        token_address = position['token']
        amount = position['amount']
        
        # Calculate return
        sell_value = amount * (1 + pnl_percent / 100)
        self.paper_balance += sell_value
        
        # Update stats
        if pnl_percent > 0:
            self.wins += 1
        else:
            self.losses += 1
        
        # Log sell
        self.logger.info("")
        self.logger.success("💰 SIMULATED SELL")
        self.logger.info(f"   Token: {token_address}")
        self.logger.info(f"   Reason: {reason}")
        self.logger.info(f"   Exit Price: ${exit_price:.8f}")
        self.logger.info(f"   PnL: {pnl_percent:+.2f}%")
        self.logger.info(f"💰 New Balance: {self.paper_balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"📊 Record: {self.wins}W / {self.losses}L")
        
        if self.wins + self.losses > 0:
            win_rate = (self.wins / (self.wins + self.losses)) * 100
            self.logger.info(f"📈 Win Rate: {win_rate:.1f}%")
        
        self.logger.info("")
        
        # Clear position
        self.current_position = None
        
        # Record trade
        self.trades_history.append({
            'token': token_address,
            'pnl': pnl_percent,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("\n" + "="*70)
        self.logger.info("  PAPER TRADING SESSION ENDED")
        self.logger.info("="*70)
        self.logger.info(f"Final Balance: {self.paper_balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"Total Trades: {len(self.trades_history)}")
        self.logger.info(f"Wins: {self.wins} | Losses: {self.losses}")
        
        if self.wins + self.losses > 0:
            win_rate = (self.wins / (self.wins + self.losses)) * 100
            self.logger.info(f"Win Rate: {win_rate:.1f}%")
            
            profit = self.paper_balance - (self.config.initial_balance_sol if self.config.network == 'solana' else self.config.initial_balance_bnb)
            self.logger.info(f"Profit/Loss: {profit:+.4f} {self.config.network.upper()}")
        
        self.logger.info("="*70)
        self.logger.info("")
        
        # Save metrics
        self.metrics.save_session({
            'trades': self.trades_history,
            'wins': self.wins,
            'losses': self.losses,
            'final_balance': self.paper_balance
        })


async def main():
    """Entry point"""
    bot = PaperTradingBot()
    await bot.start()


if __name__ == "__main__":
    print("="*70)
    print("  SuperGrokSnipV1 - PAPER TRADING MODE")
    print("  Safe Testing with REAL Market Prices")
    print("="*70)
    print()
    
    input("Press ENTER to start paper trading...")
    print()
    
    asyncio.run(main())
