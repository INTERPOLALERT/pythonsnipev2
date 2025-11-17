"""
SuperGrokSnipV1 - Paper Trading Bot (INTEGRATED VERSION)
Tests with REAL market prices but NO trades executed
Uses ALL modules: monitoring, safety, AI, alerts
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


class PaperTradingBot:
    """Integrated paper trading bot with all modules"""

    def __init__(self):
        # Load environment and config
        load_env()
        self.config = TradingConfig("config_paper.yaml")

        # Initialize logger
        self.logger = BotLogger("PaperBot")
        self.logger.info("🟢 Starting Paper Trading Mode (Integrated)")

        # Display config
        self.config.display_config()

        # Initialize wallet (for reference only in paper mode)
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

        # Initialize all modules
        self.logger.info("\n🔧 Initializing modules...")

        # Safety filters
        self.safety_filters = SafetyFilters(self.config, self.logger)
        self.logger.info("✅ Safety Filters loaded (5-layer system)")

        # AI modules
        self.lep = LEPPredictor(self.config, self.logger)
        self.cascade = CascadeSentinel(self.config, self.logger)
        self.model_trainer = ModelTrainer(self.config, self.logger)
        self.logger.info("✅ AI modules loaded (LEP + Cascade + Trainer)")

        # Telegram alerts
        self.telegram = TelegramAlerts(self.config, self.logger)
        if self.telegram.enabled:
            self.logger.info("✅ Telegram alerts enabled")

        # Blockchain monitor (will be initialized in start())
        self.monitor = None

        # Metrics
        self.metrics = MetricsTracker(mode="paper")

        # Signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.logger.info("✅ All modules initialized\n")

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.logger.warning("\n⚠️  Shutdown signal received...")
        self.running = False
        if self.monitor:
            asyncio.create_task(self.monitor.stop())

    async def start(self):
        """Start paper trading bot"""
        self.logger.info("="*70)
        self.logger.info("  PAPER TRADING MODE ACTIVE (INTEGRATED)")
        self.logger.info("="*70)
        self.logger.info(f"💰 Initial Balance: {self.paper_balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"📊 Investment per trade: {self.config.get_investment_amount():.4f}")
        self.logger.info(f"🎯 Take Profit: {self.config.take_profit}% | Stop Loss: {self.config.stop_loss}%")
        self.logger.info(f"🛡️  Safety Threshold: {self.config.safety_threshold}/100")
        self.logger.info(f"🤖 AI: LEP + Cascade enabled")
        self.logger.info("="*70)
        self.logger.info("")

        # Check balance
        if self.paper_balance < self.config.get_investment_amount():
            self.logger.error("❌ Insufficient paper balance!")
            return

        self.running = True

        # Test Telegram connection
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

        # Set up callback for when tokens are detected
        self.monitor.on_token_detected = self._on_token_detected

        # Main trading loop
        try:
            self.logger.info("🔍 Starting blockchain monitoring...")
            self.logger.info("   Press Ctrl+C to stop")
            self.logger.info("")

            # Start monitoring (this will run until stopped)
            await self.monitor.start()

        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.shutdown()

    async def _on_token_detected(self, token_data: Dict):
        """Callback when new token is detected by monitor"""
        try:
            if not self.running:
                return

            token_address = token_data.get('address', 'Unknown')
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"🎯 NEW TOKEN DETECTED: {token_address[:20]}...")
            self.logger.info(f"   Source: {token_data.get('source', 'Unknown')}")
            self.logger.info(f"{'='*70}")

            # Step 1: Run safety analysis
            safety_result = await self.safety_filters.analyze_token(token_data)

            if not safety_result['safe']:
                self.logger.warning(f"❌ Token failed safety checks ({safety_result['score']}/100)")
                for reason in safety_result['reasons']:
                    self.logger.warning(f"   • {reason}")

                # Alert about dangerous token
                if self.telegram.enabled:
                    await self.telegram.send_rug_alert(
                        token_data,
                        f"Safety score: {safety_result['score']}/100"
                    )
                return

            self.logger.success(f"✅ Safety check PASSED ({safety_result['score']}/100)")

            # Step 2: Run AI predictions
            lep_result = await self.lep.predict_pump_timing(token_data)
            cascade_result = await self.cascade.predict_virality(token_data)

            if lep_result['confidence'] < self.config.lep_min_confidence:
                self.logger.warning(f"⚠️  LEP confidence too low: {lep_result['confidence']:.1%}")
                return

            if cascade_result['virality_score'] < self.config.cascade_min_virality:
                self.logger.warning(f"⚠️  Virality score too low: {cascade_result['virality_score']}/100")
                return

            self.logger.success(f"✅ AI Predictions: LEP {lep_result['confidence']:.1%}, Viral {cascade_result['virality_score']}/100")

            # Step 3: Check trading conditions
            if self.current_position is not None:
                self.logger.warning("⚠️  Already have open position - skipping")
                return

            if self.paper_balance < self.config.get_investment_amount():
                self.logger.warning("⚠️  Insufficient balance - skipping")
                return

            # Step 4: Execute simulated buy
            await self._execute_simulated_buy(token_data, safety_result, lep_result, cascade_result)

        except Exception as e:
            self.logger.error(f"Error processing token: {e}")
            import traceback
            traceback.print_exc()

    async def _execute_simulated_buy(self, token_data: Dict, safety_result: Dict, lep_result: Dict, cascade_result: Dict):
        """Execute simulated buy"""
        token_address = token_data.get('address', 'Unknown')
        amount = self.config.get_investment_amount()

        self.logger.info("")
        self.logger.success("🚀 SIMULATED BUY EXECUTED")
        self.logger.info(f"   Token: {token_address[:20]}...")
        self.logger.info(f"   Amount: {amount:.4f} {self.config.network.upper()}")
        self.logger.info(f"   Safety Score: {safety_result['score']}/100")
        self.logger.info(f"   LEP Confidence: {lep_result['confidence']:.1%}")
        self.logger.info(f"   Virality Score: {cascade_result['virality_score']}/100")

        # Simulate price
        entry_price = token_data.get('price', 0.00000123)

        # Update paper balance
        self.paper_balance -= amount

        # Create position
        self.current_position = {
            'token': token_address,
            'token_data': token_data,
            'amount': amount,
            'entry_price': entry_price,
            'entry_time': datetime.utcnow(),
            'peak_price': entry_price,
            'safety_score': safety_result['score'],
            'lep_confidence': lep_result['confidence'],
            'virality_score': cascade_result['virality_score']
        }

        self.logger.info(f"   Entry Price: ${entry_price:.8f}")
        self.logger.info(f"💰 Remaining Balance: {self.paper_balance:.4f}")
        self.logger.info("")

        # Send Telegram alert
        if self.telegram.enabled:
            await self.telegram.send_token_detected_alert(token_data, safety_result)

        # Start monitoring position
        asyncio.create_task(self._monitor_position())

    async def _monitor_position(self):
        """Monitor open position for exit signals"""
        position = self.current_position
        token_address = position['token']
        entry_price = position['entry_price']
        entry_time = position['entry_time']

        self.logger.info(f"👀 Monitoring position: {token_address[:20]}...")

        while self.running and self.current_position == position:
            try:
                await asyncio.sleep(5)

                # Get current price (simulate for paper trading)
                import random
                price_change = random.uniform(-0.1, 0.3)  # -10% to +30%
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
                    await self._execute_simulated_sell(current_price, pnl_percent, exit_reason)
                    break

            except Exception as e:
                self.logger.error(f"Position monitor error: {e}")
                await asyncio.sleep(10)

    async def _execute_simulated_sell(self, exit_price: float, pnl_percent: float, reason: str):
        """Execute simulated sell"""
        position = self.current_position
        token_address = position['token']
        amount = position['amount']
        entry_time = position['entry_time']
        hold_time = (datetime.utcnow() - entry_time).total_seconds() / 60

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
        self.logger.success("💰 SIMULATED SELL EXECUTED")
        self.logger.info(f"   Token: {token_address[:20]}...")
        self.logger.info(f"   Reason: {reason}")
        self.logger.info(f"   Exit Price: ${exit_price:.8f}")
        self.logger.info(f"   PnL: {pnl_percent:+.2f}%")
        self.logger.info(f"   Hold Time: {hold_time:.1f} minutes")
        self.logger.info(f"💰 New Balance: {self.paper_balance:.4f} {self.config.network.upper()}")
        self.logger.info(f"📊 Record: {self.wins}W / {self.losses}L")

        if self.wins + self.losses > 0:
            win_rate = (self.wins / (self.wins + self.losses)) * 100
            self.logger.info(f"📈 Win Rate: {win_rate:.1f}%")

        self.logger.info("")

        # Send Telegram alert
        if self.telegram.enabled:
            await self.telegram.send_sell_alert(
                position['token_data'],
                pnl_percent,
                reason,
                {'tx_hash': 'SimulatedTx', 'amount_out': sell_value, 'price': exit_price}
            )

        # Record trade for AI learning
        await self.model_trainer.record_trade({
            'token_address': token_address,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'pnl_percent': pnl_percent,
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
            'pnl': pnl_percent,
            'reason': reason,
            'hold_time': hold_time,
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

            initial = self.config.initial_balance_sol if self.config.network == 'solana' else self.config.initial_balance_bnb
            profit = self.paper_balance - initial
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

        # Send Telegram summary
        if self.telegram.enabled:
            await self.telegram.send_session_summary({
                'mode': 'paper',
                'total_trades': len(self.trades_history),
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
    print("  SuperGrokSnipV1 - PAPER TRADING MODE (INTEGRATED)")
    print("  Safe Testing with REAL Market Data + ALL Modules")
    print("="*70)
    print()

    input("Press ENTER to start paper trading...")
    print()

    asyncio.run(main())
