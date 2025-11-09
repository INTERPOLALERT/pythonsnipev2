"""
Telegram Alerts - Send notifications to Telegram
"""

import os
import asyncio
from typing import Optional, Dict
from datetime import datetime
import aiohttp


class TelegramAlerts:
    """Send trading alerts to Telegram"""

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger

        # Telegram settings
        self.enabled = config.telegram_enabled
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()

        # Alert settings
        self.alert_on_buy = config.telegram_alert_buy
        self.alert_on_sell = config.telegram_alert_sell
        self.alert_on_rug = config.telegram_alert_rug
        self.alert_on_error = config.telegram_alert_error

        # Validate configuration
        if self.enabled and (not self.bot_token or not self.chat_id):
            if self.logger:
                self.logger.warning("⚠️  Telegram enabled but credentials missing in .env")
                self.logger.warning("   Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
            self.enabled = False

        if self.enabled and self.logger:
            self.logger.info("✅ Telegram alerts enabled")

    async def send_buy_alert(self, token_data: Dict, amount: float, tx_result: Dict):
        """Send buy alert"""
        if not self.enabled or not self.alert_on_buy:
            return

        try:
            network = self.config.network.upper()
            token_address = token_data.get('address', 'Unknown')[:16]
            tx_hash = tx_result.get('tx_hash', 'Unknown')[:16]
            price = tx_result.get('price', 0)

            message = f"""
🚀 <b>BUY EXECUTED</b>

💰 Amount: {amount:.4f} {network}
🪙 Token: <code>{token_address}...</code>
💵 Price: ${price:.8f}
📝 TX: <code>{tx_hash}...</code>

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

            await self._send_message(message)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to send buy alert: {e}")

    async def send_sell_alert(self, token_data: Dict, pnl_percent: float, reason: str, tx_result: Dict):
        """Send sell alert"""
        if not self.enabled or not self.alert_on_sell:
            return

        try:
            network = self.config.network.upper()
            token_address = token_data.get('address', 'Unknown')[:16]
            tx_hash = tx_result.get('tx_hash', 'Unknown')[:16]
            amount_out = tx_result.get('amount_out', 0)

            # Choose emoji based on profit/loss
            emoji = "💰" if pnl_percent > 0 else "📉"
            status = "PROFIT" if pnl_percent > 0 else "LOSS"

            message = f"""
{emoji} <b>SELL EXECUTED - {status}</b>

📊 PnL: {pnl_percent:+.2f}%
💵 Received: {amount_out:.4f} {network}
🪙 Token: <code>{token_address}...</code>
📝 TX: <code>{tx_hash}...</code>
ℹ️ Reason: {reason}

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

            await self._send_message(message)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to send sell alert: {e}")

    async def send_token_detected_alert(self, token_data: Dict, safety_result: Dict):
        """Send alert when new token is detected and passes safety"""
        if not self.enabled:
            return

        try:
            token_address = token_data.get('address', 'Unknown')[:16]
            source = token_data.get('source', 'Unknown')
            safety_score = safety_result.get('score', 0)
            passed_checks = safety_result.get('passed_checks', 0)
            total_checks = safety_result.get('total_checks', 5)

            message = f"""
🎯 <b>NEW TOKEN DETECTED</b>

🪙 Token: <code>{token_address}...</code>
🔗 Source: {source}
🛡️ Safety: {safety_score}/100 ({passed_checks}/{total_checks} checks)

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

            await self._send_message(message)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to send detection alert: {e}")

    async def send_rug_alert(self, token_data: Dict, reason: str):
        """Send rug pull alert"""
        if not self.enabled or not self.alert_on_rug:
            return

        try:
            token_address = token_data.get('address', 'Unknown')[:16]

            message = f"""
🚨 <b>RUG DETECTED</b>

⚠️ DANGEROUS TOKEN DETECTED
🪙 Token: <code>{token_address}...</code>
❌ Reason: {reason}

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

            await self._send_message(message)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to send rug alert: {e}")

    async def send_error_alert(self, error_message: str, context: Optional[str] = None):
        """Send error alert"""
        if not self.enabled or not self.alert_on_error:
            return

        try:
            message = f"""
❌ <b>BOT ERROR</b>

🔴 Error: {error_message}
"""
            if context:
                message += f"📝 Context: {context}\n"

            message += f"\n⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

            await self._send_message(message)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to send error alert: {e}")

    async def send_session_summary(self, summary: Dict):
        """Send session summary at end"""
        if not self.enabled:
            return

        try:
            mode = summary.get('mode', 'unknown').upper()
            trades = summary.get('total_trades', 0)
            wins = summary.get('wins', 0)
            losses = summary.get('losses', 0)
            win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            final_balance = summary.get('final_balance', 0)
            network = self.config.network.upper()

            message = f"""
📊 <b>SESSION SUMMARY</b>

🎮 Mode: {mode}
📈 Total Trades: {trades}
✅ Wins: {wins}
❌ Losses: {losses}
📊 Win Rate: {win_rate:.1f}%
💰 Final Balance: {final_balance:.4f} {network}

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

            await self._send_message(message)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to send summary alert: {e}")

    async def _send_message(self, text: str):
        """Send message via Telegram Bot API"""
        if not self.enabled:
            return

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status != 200:
                        if self.logger:
                            self.logger.debug(f"Telegram API error: {response.status}")

        except asyncio.TimeoutError:
            if self.logger:
                self.logger.debug("Telegram API timeout")
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Telegram send error: {e}")

    async def test_connection(self) -> bool:
        """Test Telegram connection"""
        if not self.enabled:
            if self.logger:
                self.logger.warning("Telegram alerts not enabled")
            return False

        try:
            message = """
✅ <b>TELEGRAM ALERTS ACTIVE</b>

Your trading bot is connected and will send alerts for:
"""
            if self.alert_on_buy:
                message += "• Buy orders\n"
            if self.alert_on_sell:
                message += "• Sell orders\n"
            if self.alert_on_rug:
                message += "• Rug detections\n"
            if self.alert_on_error:
                message += "• Errors\n"

            message += f"\n⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

            await self._send_message(message)

            if self.logger:
                self.logger.success("✅ Telegram test message sent")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Telegram connection test failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    from config_loader import TradingConfig, load_env

    async def main():
        load_env()
        config = TradingConfig("config_live.yaml")

        alerts = TelegramAlerts(config)

        # Test connection
        await alerts.test_connection()

        # Test alerts
        token_data = {'address': 'TestToken123...'}
        tx_result = {'tx_hash': 'TxHash123...', 'price': 0.00000123}

        await alerts.send_buy_alert(token_data, 0.05, tx_result)
        await asyncio.sleep(2)

        await alerts.send_sell_alert(token_data, 150.5, "Take Profit", tx_result)

    asyncio.run(main())
