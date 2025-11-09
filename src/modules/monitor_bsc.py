"""
BSC (Binance Smart Chain) Blockchain Monitor
Monitors PancakeSwap for new token launches
"""

import asyncio
import os
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
except ImportError:
    print("⚠️  Web3 not installed. Run: pip install web3")
    Web3 = None


class BSCMonitor:
    """Monitor BSC blockchain for new token launches"""

    # PancakeSwap Factory Address
    PANCAKESWAP_FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"

    # PancakeSwap Router Address
    PANCAKESWAP_ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

    # PancakeSwap Factory ABI (simplified - only events we need)
    FACTORY_ABI = json.dumps([{
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "token0", "type": "address"},
            {"indexed": True, "name": "token1", "type": "address"},
            {"indexed": False, "name": "pair", "type": "address"},
            {"indexed": False, "name": "", "type": "uint256"}
        ],
        "name": "PairCreated",
        "type": "event"
    }])

    def __init__(self, rpc_url: str, logger=None):
        self.rpc_url = rpc_url
        self.logger = logger
        self.running = False
        self.w3: Optional[Web3] = None
        self.factory_contract = None
        self.last_block = 0
        self.seen_pairs = set()

        # Callbacks
        self.on_token_detected: Optional[Callable] = None

    async def start(self):
        """Start monitoring"""
        if not Web3:
            if self.logger:
                self.logger.error("❌ Web3 not installed")
            return

        self.running = True

        try:
            # Initialize Web3
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            if not self.w3.is_connected():
                if self.logger:
                    self.logger.error("❌ Failed to connect to BSC")
                return

            if self.logger:
                self.logger.info("🔗 Connected to BSC mainnet")
                self.logger.info(f"   RPC: {self.rpc_url}")

            # Get factory contract
            factory_abi = json.loads(self.FACTORY_ABI)
            self.factory_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.PANCAKESWAP_FACTORY),
                abi=factory_abi
            )

            # Get current block
            self.last_block = self.w3.eth.block_number

            if self.logger:
                self.logger.info(f"📊 Starting from block {self.last_block}")

            # Start monitoring
            await self._monitor_blocks()

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to start BSC monitor: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop monitoring"""
        self.running = False

    async def _monitor_blocks(self):
        """Monitor new blocks for PairCreated events"""
        if self.logger:
            self.logger.info("🔄 Polling mode active (checking every 3 seconds)")

        while self.running:
            try:
                current_block = self.w3.eth.block_number

                # Check for new blocks
                if current_block > self.last_block:
                    # Get events from last_block to current_block
                    await self._check_new_pairs(self.last_block + 1, current_block)
                    self.last_block = current_block

                # Wait before next check
                await asyncio.sleep(3.0)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5.0)

    async def _check_new_pairs(self, from_block: int, to_block: int):
        """Check for new pair creation events"""
        try:
            # Get PairCreated events
            event_filter = self.factory_contract.events.PairCreated.create_filter(
                fromBlock=from_block,
                toBlock=to_block
            )

            events = event_filter.get_all_entries()

            for event in events:
                pair_address = event['args']['pair']

                # Skip if already seen
                if pair_address in self.seen_pairs:
                    continue

                self.seen_pairs.add(pair_address)

                token0 = event['args']['token0']
                token1 = event['args']['token1']

                # Determine which is the actual token (not WBNB)
                WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
                token_address = token1 if token0.lower() == WBNB.lower() else token0

                if self.logger:
                    self.logger.info(f"🎯 New pair detected: {pair_address[:10]}...")

                # Get token data
                token_data = await self._get_token_data(token_address, pair_address)

                if token_data and self.on_token_detected:
                    await self.on_token_detected(token_data)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Event check error: {e}")

    async def _get_token_data(self, token_address: str, pair_address: str) -> Optional[Dict]:
        """Get token and pair data"""
        try:
            # ERC20 ABI (simplified)
            erc20_abi = json.dumps([
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
            ])

            # Get token contract
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=json.loads(erc20_abi)
            )

            # Get token info
            name = token_contract.functions.name().call()
            symbol = token_contract.functions.symbol().call()
            decimals = token_contract.functions.decimals().call()
            total_supply = token_contract.functions.totalSupply().call()

            # Get liquidity from pair
            liquidity_bnb = await self._get_pair_liquidity(pair_address)

            token_data = {
                'source': 'pancakeswap',
                'address': token_address,
                'pair': pair_address,
                'name': name,
                'symbol': symbol,
                'decimals': decimals,
                'total_supply': total_supply,
                'liquidity_bnb': liquidity_bnb,
                'liquidity_usd': liquidity_bnb * 300,  # Rough estimate (BNB price ~$300)
                'timestamp': datetime.utcnow(),
                'detected_at': datetime.utcnow().isoformat()
            }

            return token_data

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Token data error: {e}")
            return None

    async def _get_pair_liquidity(self, pair_address: str) -> float:
        """Get BNB liquidity in pair"""
        try:
            WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
            balance = self.w3.eth.get_balance(Web3.to_checksum_address(pair_address))
            bnb_amount = self.w3.from_wei(balance, 'ether')
            return float(bnb_amount)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Liquidity check error: {e}")
            return 0.0

    async def get_token_holders(self, token_address: str) -> int:
        """Get number of token holders (requires BSCScan API)"""
        try:
            bscscan_key = os.getenv('BSCSCAN_API_KEY', '')

            if not bscscan_key:
                # Cannot get holders without API key
                return 0

            import aiohttp

            async with aiohttp.ClientSession() as session:
                url = f"https://api.bscscan.com/api?module=token&action=tokenholderlist&contractaddress={token_address}&apikey={bscscan_key}"

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            return len(data.get('result', []))

            return 0

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Holders check error: {e}")
            return 0

    async def get_token_price(self, token_address: str) -> Optional[float]:
        """Get token price in USD"""
        try:
            # Use PancakeSwap router to get price
            # This is a simplified version - real implementation needs price oracle
            return 0.00001

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Price fetch error: {e}")
            return None


# Example usage
if __name__ == "__main__":
    async def main():
        monitor = BSCMonitor(
            rpc_url="https://bsc-dataseed1.binance.org"
        )

        async def on_token(token_data):
            print(f"New token detected: {token_data}")

        monitor.on_token_detected = on_token
        await monitor.start()

    asyncio.run(main())
