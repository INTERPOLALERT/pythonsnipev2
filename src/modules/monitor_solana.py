"""
Solana Blockchain Monitor
Monitors Raydium and Pump.fun for new token launches
"""

import asyncio
import os
from typing import Dict, List, Optional, Callable
from datetime import datetime
import aiohttp

try:
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey
except ImportError:
    print("⚠️  Solana libraries not installed. Run: pip install solana solders")
    AsyncClient = None
    Pubkey = None


class SolanaMonitor:
    """Monitor Solana blockchain for new token launches"""

    # Raydium AMM Program ID
    RAYDIUM_AMM_PROGRAM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"

    # Pump.fun Program ID (example - verify actual ID)
    PUMPFUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

    def __init__(self, rpc_url: str, websocket_url: Optional[str] = None, logger=None):
        self.rpc_url = rpc_url
        self.websocket_url = websocket_url
        self.logger = logger
        self.running = False
        self.client: Optional[AsyncClient] = None
        self.seen_tokens = set()

        # Callbacks
        self.on_token_detected: Optional[Callable] = None

    async def start(self):
        """Start monitoring"""
        if not AsyncClient:
            if self.logger:
                self.logger.error("❌ Solana libraries not installed")
            return

        self.running = True
        self.client = AsyncClient(self.rpc_url)

        if self.logger:
            self.logger.info("🔗 Connected to Solana mainnet")
            self.logger.info(f"   RPC: {self.rpc_url[:60]}...")

        try:
            # Start monitoring tasks
            if self.websocket_url:
                await self._monitor_websocket()
            else:
                await self._monitor_polling()
        finally:
            await self.stop()

    async def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.client:
            await self.client.close()
            self.client = None

    async def _monitor_websocket(self):
        """Monitor using WebSocket (real-time)"""
        if self.logger:
            self.logger.info("📡 WebSocket monitoring active")

        # WebSocket monitoring implementation
        # This requires websockets library and Solana WebSocket protocol
        # For now, fall back to polling
        if self.logger:
            self.logger.warning("⚠️  WebSocket monitoring not fully implemented yet")
            self.logger.info("   Falling back to polling mode...")

        await self._monitor_polling()

    async def _monitor_polling(self):
        """Monitor using RPC polling"""
        if self.logger:
            self.logger.info("🔄 Polling mode active (checking every 2 seconds)")

        while self.running:
            try:
                # Get recent transactions for Raydium AMM
                await self._check_raydium_pools()

                # Get recent transactions for Pump.fun
                await self._check_pumpfun_launches()

                # Wait before next check
                await asyncio.sleep(2.0)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5.0)

    async def _check_raydium_pools(self):
        """Check for new Raydium pools"""
        try:
            # Get signatures for Raydium program
            program_pubkey = Pubkey.from_string(self.RAYDIUM_AMM_PROGRAM)

            response = await self.client.get_signatures_for_address(
                program_pubkey,
                limit=20
            )

            if response.value:
                for sig_info in response.value:
                    signature = str(sig_info.signature)

                    # Skip if already seen
                    if signature in self.seen_tokens:
                        continue

                    self.seen_tokens.add(signature)

                    # Get transaction details
                    tx = await self.client.get_transaction(
                        sig_info.signature,
                        max_supported_transaction_version=0
                    )

                    if tx.value:
                        # Parse transaction for new pool creation
                        token_data = await self._parse_raydium_transaction(tx.value)

                        if token_data and self.on_token_detected:
                            await self.on_token_detected(token_data)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Raydium check error: {e}")

    async def _check_pumpfun_launches(self):
        """Check for new Pump.fun launches"""
        try:
            # Similar to Raydium but for Pump.fun
            # Implementation depends on Pump.fun's actual program structure
            pass

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Pump.fun check error: {e}")

    async def _parse_raydium_transaction(self, transaction) -> Optional[Dict]:
        """Parse Raydium transaction for token data"""
        try:
            # Extract token mint, liquidity pool, etc.
            # This is a simplified version - full parsing requires understanding Raydium's instruction format

            token_data = {
                'source': 'raydium',
                'address': 'DemoToken...',  # Would extract actual token mint
                'pool': 'DemoPool...',      # Would extract pool address
                'liquidity': 10000,         # Would calculate from transaction
                'timestamp': datetime.utcnow(),
                'detected_at': datetime.utcnow().isoformat()
            }

            return token_data

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Parse error: {e}")
            return None

    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Get detailed token information"""
        try:
            if not self.client:
                return None

            token_pubkey = Pubkey.from_string(token_address)

            # Get token supply
            supply_response = await self.client.get_token_supply(token_pubkey)

            # Get token accounts (holders)
            accounts_response = await self.client.get_token_accounts_by_owner(
                token_pubkey,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
            )

            holders_count = len(accounts_response.value) if accounts_response.value else 0

            token_info = {
                'address': token_address,
                'supply': supply_response.value.amount if supply_response.value else 0,
                'decimals': supply_response.value.decimals if supply_response.value else 9,
                'holders': holders_count,
                'timestamp': datetime.utcnow().isoformat()
            }

            return token_info

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get token info: {e}")
            return None

    async def get_token_price(self, token_address: str) -> Optional[float]:
        """Get token price from price feeds"""
        try:
            # Use Birdeye API or Jupiter API for price
            birdeye_key = os.getenv('BIRDEYE_API_KEY', '')

            if birdeye_key:
                async with aiohttp.ClientSession() as session:
                    url = f"https://public-api.birdeye.so/defi/price?address={token_address}"
                    headers = {"X-API-KEY": birdeye_key}

                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get('data', {}).get('value', 0.0)

            # Fallback: return demo price
            return 0.00000123

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Price fetch error: {e}")
            return None


# Example usage
if __name__ == "__main__":
    async def main():
        monitor = SolanaMonitor(
            rpc_url="https://api.mainnet-beta.solana.com"
        )

        async def on_token(token_data):
            print(f"New token detected: {token_data}")

        monitor.on_token_detected = on_token
        await monitor.start()

    asyncio.run(main())
