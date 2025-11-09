"""
Execution Engine - Execute trades with MEV protection
Supports Solana (with Jito) and BSC
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime

try:
    from solana.rpc.async_api import AsyncClient
    from solana.transaction import Transaction
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import transfer, TransferParams
    from solders.instruction import Instruction
except ImportError:
    print("⚠️  Solana libraries not installed")
    AsyncClient = None

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("⚠️  Web3 libraries not installed")
    Web3 = None


class ExecutionEngine:
    """Execute trades with MEV protection"""

    # Jito tip accounts (rotate for load balancing)
    JITO_TIP_ACCOUNTS = [
        "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
        "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
        "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
        "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
        "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
        "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
        "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
        "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
    ]

    def __init__(self, config, wallet_manager, logger=None):
        self.config = config
        self.wallet = wallet_manager
        self.logger = logger
        self.network = config.network

        # Jito settings
        self.use_jito = config.use_jito and self.network == 'solana'
        self.jito_tip = config.jito_tip_sol
        self.jito_tip_account_index = 0

    async def buy_token(self, token_data: Dict, amount: float) -> Optional[Dict]:
        """
        Execute buy order

        Args:
            token_data: Token information
            amount: Amount in SOL/BNB to spend

        Returns:
            {
                'success': bool,
                'tx_hash': str,
                'amount_in': float,
                'amount_out': float,
                'price': float,
                'timestamp': datetime
            }
        """
        if self.logger:
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"🚀 EXECUTING BUY ORDER")
            self.logger.info(f"   Token: {token_data.get('address', 'Unknown')[:20]}...")
            self.logger.info(f"   Amount: {amount:.4f} {self.network.upper()}")

        try:
            if self.network == 'solana':
                return await self._buy_solana(token_data, amount)
            elif self.network == 'bsc':
                return await self._buy_bsc(token_data, amount)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported network: {self.network}")
                return None

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Buy failed: {e}")
            return None

    async def sell_token(self, token_data: Dict, amount: float) -> Optional[Dict]:
        """
        Execute sell order

        Args:
            token_data: Token information
            amount: Amount of tokens to sell

        Returns:
            {
                'success': bool,
                'tx_hash': str,
                'amount_in': float,
                'amount_out': float,
                'price': float,
                'timestamp': datetime
            }
        """
        if self.logger:
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"💰 EXECUTING SELL ORDER")
            self.logger.info(f"   Token: {token_data.get('address', 'Unknown')[:20]}...")

        try:
            if self.network == 'solana':
                return await self._sell_solana(token_data, amount)
            elif self.network == 'bsc':
                return await self._sell_bsc(token_data, amount)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported network: {self.network}")
                return None

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Sell failed: {e}")
            return None

    async def _buy_solana(self, token_data: Dict, amount: float) -> Optional[Dict]:
        """Execute Solana buy via Raydium"""
        try:
            if not AsyncClient:
                if self.logger:
                    self.logger.error("Solana libraries not installed")
                return None

            keypair = self.wallet.get_solana_keypair()
            if not keypair:
                if self.logger:
                    self.logger.error("No Solana wallet loaded")
                return None

            rpc_url = self.config.get_rpc_endpoint()
            client = AsyncClient(rpc_url)

            try:
                # Build Raydium swap instruction
                # This is simplified - real implementation needs:
                # 1. Get pool accounts
                # 2. Calculate amount out with slippage
                # 3. Build swap instruction
                # 4. Add Jito tip if enabled
                # 5. Send transaction

                if self.use_jito:
                    if self.logger:
                        self.logger.info(f"   Using Jito bundle (tip: {self.jito_tip} SOL)")

                    # Add Jito tip
                    tip_account = self._get_jito_tip_account()

                    # Build tip instruction
                    # tip_instruction = transfer(TransferParams(
                    #     from_pubkey=keypair.pubkey(),
                    #     to_pubkey=Pubkey.from_string(tip_account),
                    #     lamports=int(self.jito_tip * 1e9)
                    # ))

                    if self.logger:
                        self.logger.info(f"   Tip account: {tip_account[:16]}...")

                # For demo: simulate transaction
                if self.logger:
                    self.logger.warning("⚠️  DEMO MODE: Transaction not sent")
                    self.logger.info("   Real implementation would:")
                    self.logger.info("   1. Build Raydium swap instruction")
                    self.logger.info("   2. Add Jito tip (if enabled)")
                    self.logger.info("   3. Send as Jito bundle or regular transaction")

                # Simulate result
                result = {
                    'success': True,
                    'tx_hash': 'DemoTxHash123...',
                    'amount_in': amount,
                    'amount_out': amount / 0.00000123,  # Simulated token amount
                    'price': 0.00000123,
                    'timestamp': datetime.utcnow()
                }

                if self.logger:
                    self.logger.success("✅ Buy executed (demo)")
                    self.logger.info(f"   TX: {result['tx_hash'][:20]}...")

                return result

            finally:
                await client.close()

        except Exception as e:
            if self.logger:
                self.logger.error(f"Solana buy error: {e}")
            return None

    async def _sell_solana(self, token_data: Dict, amount: float) -> Optional[Dict]:
        """Execute Solana sell via Raydium"""
        try:
            # Similar to buy but reverse direction
            if self.logger:
                self.logger.warning("⚠️  DEMO MODE: Sell transaction not sent")

            result = {
                'success': True,
                'tx_hash': 'DemoSellTxHash123...',
                'amount_in': amount,
                'amount_out': amount * 0.00000123,  # Simulated SOL amount
                'price': 0.00000123,
                'timestamp': datetime.utcnow()
            }

            if self.logger:
                self.logger.success("✅ Sell executed (demo)")
                self.logger.info(f"   TX: {result['tx_hash'][:20]}...")

            return result

        except Exception as e:
            if self.logger:
                self.logger.error(f"Solana sell error: {e}")
            return None

    async def _buy_bsc(self, token_data: Dict, amount: float) -> Optional[Dict]:
        """Execute BSC buy via PancakeSwap"""
        try:
            if not Web3:
                if self.logger:
                    self.logger.error("Web3 libraries not installed")
                return None

            account = self.wallet.get_bsc_account()
            if not account:
                if self.logger:
                    self.logger.error("No BSC wallet loaded")
                return None

            # Build PancakeSwap swap transaction
            # This is simplified - real implementation needs:
            # 1. Get PancakeSwap router contract
            # 2. Calculate amount out with slippage
            # 3. Build swap transaction
            # 4. Sign and send

            if self.logger:
                self.logger.warning("⚠️  DEMO MODE: Transaction not sent")
                self.logger.info("   Real implementation would:")
                self.logger.info("   1. Build PancakeSwap swap transaction")
                self.logger.info("   2. Set gas price and limit")
                self.logger.info("   3. Sign and broadcast transaction")

            # Simulate result
            result = {
                'success': True,
                'tx_hash': '0xDemoTxHash123...',
                'amount_in': amount,
                'amount_out': amount / 0.00001,  # Simulated token amount
                'price': 0.00001,
                'timestamp': datetime.utcnow()
            }

            if self.logger:
                self.logger.success("✅ Buy executed (demo)")
                self.logger.info(f"   TX: {result['tx_hash'][:20]}...")

            return result

        except Exception as e:
            if self.logger:
                self.logger.error(f"BSC buy error: {e}")
            return None

    async def _sell_bsc(self, token_data: Dict, amount: float) -> Optional[Dict]:
        """Execute BSC sell via PancakeSwap"""
        try:
            # Similar to buy but reverse direction
            if self.logger:
                self.logger.warning("⚠️  DEMO MODE: Sell transaction not sent")

            result = {
                'success': True,
                'tx_hash': '0xDemoSellTxHash123...',
                'amount_in': amount,
                'amount_out': amount * 0.00001,  # Simulated BNB amount
                'price': 0.00001,
                'timestamp': datetime.utcnow()
            }

            if self.logger:
                self.logger.success("✅ Sell executed (demo)")
                self.logger.info(f"   TX: {result['tx_hash'][:20]}...")

            return result

        except Exception as e:
            if self.logger:
                self.logger.error(f"BSC sell error: {e}")
            return None

    def _get_jito_tip_account(self) -> str:
        """Get next Jito tip account (round-robin)"""
        tip_account = self.JITO_TIP_ACCOUNTS[self.jito_tip_account_index]
        self.jito_tip_account_index = (self.jito_tip_account_index + 1) % len(self.JITO_TIP_ACCOUNTS)
        return tip_account


# Example usage
if __name__ == "__main__":
    from config_loader import TradingConfig, load_env
    from wallet_manager import WalletManager

    async def main():
        load_env()
        config = TradingConfig("config_live.yaml")
        wallet = WalletManager(network="solana")
        wallet.load_from_env()

        engine = ExecutionEngine(config, wallet)

        # Test buy
        token_data = {
            'address': 'TestToken123...',
            'source': 'raydium'
        }

        result = await engine.buy_token(token_data, 0.05)
        print(f"\nResult: {result}")

    asyncio.run(main())
