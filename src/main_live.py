"""
SuperGrokSnipV1 - Live Trading Bot (INTEGRATED VERSION)
REAL MONEY - Uses ALL modules with actual trade execution
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

from config_loader import TradingConfig, load_env
from wallet_manager import WalletManager
from utils.logger import BotLogger
from utils.metrics import MetricsTracker

# Import all trading modules
from modules.monitor_solana import SolanaMonitor
from modules.monitor_bsc import BSCMonitor
from modules.safety_filters import SafetyFilters
from modules.execution_engine import ExecutionEngine
from modules.telegram_alerts import TelegramAlerts

# Import AI modules
from ai.lep_predictor import LEPPredictor
from ai.cascade_sentinel import CascadeSentinel
from ai.model_trainer import ModelTrainer


class LiveTradingBot:
    """Integrated live trading bot - REAL MONEY"""

    def __init__(self):
        # Load environment and config
        load_env()
        self.config = TradingConfig("config_live.yaml")

        # Initialize logger
        self.logger = BotLogger("LiveBot")
        self.logger.critical("🔴 LIVE TRADING MODE - REAL MONEY (INTEGRATED)")

        # Display config
        self.config.display_config()

        # Initialize wallet - REQUIRED for live trading
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

        # Initialize all modules
        self.logger.critical("\n🔧 Initializing LIVE trading modules...")

        # Safety filters
        self.safety_filters = SafetyFilters(self.config, self.logger)
        self.logger.info("✅ Safety Filters loaded")

        # Execution engine - REAL TRADES
        self.execution = ExecutionEngine(self.config, self.wallet, self.logger)
        self.logger.info("✅ Execution Engine loaded (REAL TRADES!)")

        # AI modules
        self.lep = LEPPredictor(self.config, self.logger)
        self.cascade = CascadeSentinel(self.config, self.logger)
        self.model_trainer = ModelTrainer(self.config, self.logger)
        self.logger.info("✅ AI modules loaded")

        # Telegram alerts
        self.telegram = TelegramAlerts(self.config, self.logger)
        if self.telegram.enabled:
            self.logger.info("✅ Telegram alerts enabled")

        # Blockchain monitor (will be initialized in start())
        self.monitor = None

        # Metrics
        self.metrics = MetricsTracker(mode="live")

        # Signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.logger.critical("✅ All modules initialized - READY FOR LIVE TRADING\n")

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.logger.critical("\n⚠️  EMERGENCY STOP - Shutting down...")
        self.running = False
        if self.monitor:
            asyncio.create_task(self.monitor.stop())

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
        print(f"  ✅ 5-layer safety system")
        print(f"  ✅ AI predictions (LEP + Cascade)")
        print(f"  ✅ Stop loss: {self.config.stop_loss}%")
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

        # Test Telegram
        if self.telegram.enabled:
            await self.telegram.test_connection()

        # Initialize blockchain monitor
        if self.config.network == 'solana':
            self.monitor = SolanaMonitor(
                rpc_url=self.config.get_rpc_endpoint(),
                websocket_url=self.config.solana_websocket if self.config.use_websocket_sol else None,
                logger=self.logger
            )
        elif self.config.network == 'bsc':
            self.monitor = BSCMonitor(
                rpc_url=self.config.get_rpc_endpoint(),
                logger=self.logger
            )
        else:
            self.logger.error(f"❌ Unsupported network: {self.config.network}")
            return

        # Set up callback
        self.monitor.on_token_detected = self._on_token_detected

        # Main trading loop
        try:
            self.logger.critical("🔍 Monitoring blockchain for opportunities...")
            self.logger.info("   Press Ctrl+C for emergency stop")
            self.logger.info("")

            await self.monitor.start()

        except KeyboardInterrupt:
            self.logger.critical("\n⚠️  Interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.shutdown()

    async def _on_token_detected(self, token_data: Dict):
        """Callback when new token is detected"""
        try:
            if not self.running:
                return

            # Check daily limit
            if self.daily_spent >= self.config.get_max_daily():
                self.logger.warning(f"⚠️  Daily limit reached: {self.daily_spent:.4f}")
                return

            token_address = token_data.get('address', 'Unknown')
            self.logger.critical(f"\n{'='*70}")
            self.logger.critical(f"🎯 NEW TOKEN DETECTED: {token_address[:20]}...")
            self.logger.info(f"   Source: {token_data.get('source', 'Unknown')}")
            self.logger.critical(f"{'='*70}")

            # Step 1: Safety analysis
            safety_result = await self.safety_filters.analyze_token(token_data)

            if not safety_result['safe']:
                self.logger.warning(f"❌ Safety check FAILED ({safety_result['score']}/100)")
                for reason in safety_result['reasons']:
                    self.logger.warning(f"   • {reason}")

                if self.telegram.enabled:
                    await self.telegram.send_rug_alert(token_data, f"Safety: {safety_result['score']}/100")
                return

            self.logger.success(f"✅ Safety check PASSED ({safety_result['score']}/100)")

            # Step 2: AI predictions
            lep_result = await self.lep.predict_pump_timing(token_data)
            cascade_result = await self.cascade.predict_virality(token_data)

            if lep_result['confidence'] < self.config.lep_min_confidence:
                self.logger.warning(f"⚠️  LEP confidence low: {lep_result['confidence']:.1%}")
                return

            if cascade_result['virality_score'] < self.config.cascade_min_virality:
                self.logger.warning(f"⚠️  Virality score low: {cascade_result['virality_score']}/100")
                return

            self.logger.success(f"✅ AI Predictions: LEP {lep_result['confidence']:.1%}, Viral {cascade_result['virality_score']}/100")

            # Step 3: Check trading conditions
            if self.current_position is not None:
                self.logger.warning("⚠️  Already have open position - skipping")
                return

            # Step 4: Execute REAL buy
            await self._execute_real_buy(token_data, safety_result, lep_result, cascade_result)

        except Exception as e:
            self.logger.error(f"Error processing token: {e}")
            import traceback
            traceback.print_exc()

            if self.telegram.enabled:
                await self.telegram.send_error_alert(str(e), "Token processing")

    async def _execute_real_buy(self, token_data: Dict, safety_result: Dict, lep_result: Dict, cascade_result: Dict):
        """Execute REAL buy order"""
        token_address = token_data.get('address', 'Unknown')
        amount = self.config.get_investment_amount()

        self.logger.critical("")
        self.logger.critical("🚀 EXECUTING REAL BUY ORDER")
        self.logger.info(f"   Token: {token_address[:20]}...")
        self.logger.info(f"   Amount: {amount:.4f} {self.config.network.upper()}")
        self.logger.info(f"   Safety: {safety_result['score']}/100")
        self.logger.info(f"   LEP: {lep_result['confidence']:.1%}")
        self.logger.info(f"   Viral: {cascade_result['virality_score']}/100")

        # Execute buy via execution engine
        tx_result = await self.execution.buy_token(token_data, amount)

        if not tx_result or not tx_result.get('success'):
            self.logger.error("❌ Buy order FAILED")
            if self.telegram.enabled:
                await self.telegram.send_error_alert("Buy order failed", f"Token: {token_address[:20]}")
            return

        self.logger.success(f"✅ BUY ORDER EXECUTED")
        self.logger.info(f"   TX: {tx_result.get('tx_hash', 'Unknown')[:20]}...")
        self.logger.info(f"   Entry Price: ${tx_result.get('price', 0):.8f}")

        # Update daily spent
        self.daily_spent += amount

        # Create position
        self.current_position = {
            'token': token_address,
            'token_data': token_data,
            'amount': amount,
            'entry_price': tx_result.get('price', 0),
            'entry_time': datetime.utcnow(),
            'peak_price': tx_result.get('price', 0),
            'tx_hash': tx_result.get('tx_hash'),
            'safety_score': safety_result['score'],
            'lep_confidence': lep_result['confidence'],
            'virality_score': cascade_result['virality_score']
        }

        self.logger.info(f"💰 Daily spent: {self.daily_spent:.4f}/{self.config.get_max_daily()}")
        self.logger.info("")

        # Send Telegram alert
        if self.telegram.enabled:
            await self.telegram.send_buy_alert(token_data, amount, tx_result)

        # Start monitoring position
        asyncio.create_task(self._monitor_position())

    async def _monitor_position(self):
        """Monitor open position for exit signals"""
        position = self.current_position
        token_address = position['token']
        entry_price = position['entry_price']

        self.logger.critical(f"👀 Monitoring LIVE position: {token_address[:20]}...")

        while self.running and self.current_position == position:
            try:
                await asyncio.sleep(5)

                # Get current price from monitor
                current_price = await self.monitor.get_token_price(token_address)
                if not current_price:
                    continue

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
                    await self._execute_real_sell(current_price, pnl_percent, exit_reason)
                    break

            except Exception as e:
                self.logger.error(f"Position monitor error: {e}")
                await asyncio.sleep(10)

    async def _execute_real_sell(self, exit_price: float, pnl_percent: float, reason: str):
        """Execute REAL sell order"""
        position = self.current_position
        token_address = position['token']
        amount = position['amount']
        hold_time = (datetime.utcnow() - position['entry_time']).total_seconds() / 60

        self.logger.critical("")
        self.logger.critical("💰 EXECUTING REAL SELL ORDER")
        self.logger.info(f"   Token: {token_address[:20]}...")
        self.logger.info(f"   Reason: {reason}")
        self.logger.info(f"   Current Price: ${exit_price:.8f}")
        self.logger.info(f"   Expected PnL: {pnl_percent:+.2f}%")

        # Execute sell via execution engine
        tx_result = await self.execution.sell_token(position['token_data'], amount)

        if not tx_result or not tx_result.get('success'):
            self.logger.error("❌ Sell order FAILED")
            if self.telegram.enabled:
                await self.telegram.send_error_alert("Sell order failed", f"Token: {token_address[:20]}")
            return

        actual_pnl = ((tx_result.get('amount_out', 0) - amount) / amount) * 100

        self.logger.success(f"✅ SELL ORDER EXECUTED")
        self.logger.info(f"   TX: {tx_result.get('tx_hash', 'Unknown')[:20]}...")
        self.logger.info(f"   Actual PnL: {actual_pnl:+.2f}%")
        self.logger.info(f"   Hold Time: {hold_time:.1f} minutes")

        # Update stats
        if actual_pnl > 0:
            self.wins += 1
        else:
            self.losses += 1

        self.logger.info(f"📊 Record: {self.wins}W / {self.losses}L")

        if self.wins + self.losses > 0:
            win_rate = (self.wins / (self.wins + self.losses)) * 100
            self.logger.info(f"📈 Win Rate: {win_rate:.1f}%")

        self.logger.info("")

        # Send Telegram alert
        if self.telegram.enabled:
            await self.telegram.send_sell_alert(position['token_data'], actual_pnl, reason, tx_result)

        # Record trade for AI learning
        await self.model_trainer.record_trade({
            'token_address': token_address,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'pnl_percent': actual_pnl,
            'safety_score': position['safety_score'],
            'lep_confidence': position['lep_confidence'],
            'virality_score': position['virality_score'],
            'hold_time_minutes': hold_time
        })

        # Clear position
        self.current_position = None

        # Record trade
        self.trades_history.append({
            'token': token_address,
            'pnl': actual_pnl,
            'reason': reason,
            'hold_time': hold_time,
            'tx_hash': tx_result.get('tx_hash'),
            'timestamp': datetime.utcnow().isoformat()
        })

    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.critical("\n" + "="*70)
        self.logger.critical("  LIVE TRADING SESSION ENDED")
        self.logger.critical("="*70)

        # Get final balance
        balance = await self.wallet.get_balance()
        self.logger.info(f"Final Balance: {balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"Daily Spent: {self.daily_spent:.4f}")
        self.logger.info(f"Total Trades: {len(self.trades_history)}")
        self.logger.info(f"Wins: {self.wins} | Losses: {self.losses}")

        if self.wins + self.losses > 0:
            win_rate = (self.wins / (self.wins + self.losses)) * 100
            self.logger.info(f"Win Rate: {win_rate:.1f}%")

        self.logger.critical("="*70)
        self.logger.info("")

        # Save metrics
        self.metrics.save_session({
            'trades': self.trades_history,
            'wins': self.wins,
            'losses': self.losses,
            'daily_spent': self.daily_spent,
            'final_balance': balance
        })

        # Send Telegram summary
        if self.telegram.enabled:
            await self.telegram.send_session_summary({
                'mode': 'live',
                'total_trades': len(self.trades_history),
                'wins': self.wins,
                'losses': self.losses,
                'final_balance': balance
            })


async def main():
    """Entry point"""
    bot = LiveTradingBot()
    await bot.start()


if __name__ == "__main__":
    print("="*70)
    print("  SuperGrokSnipV1 - LIVE TRADING MODE (INTEGRATED)")
    print("  ⚠️  REAL MONEY - EXTREME CAUTION REQUIRED ⚠️")
    print("="*70)
    print()

    asyncio.run(main())
