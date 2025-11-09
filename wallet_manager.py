"""
Wallet Manager - Handles private keys, seed phrases, and wallet operations
Supports both Solana and BSC wallets
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("⚠️ cryptography not installed. Run: pip install cryptography")
    Fernet = None

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
except ImportError:
    print("⚠️ solders not installed. Run: pip install solders")
    Keypair = None
    Pubkey = None

try:
    from mnemonic import Mnemonic
except ImportError:
    print("⚠️ mnemonic not installed. Run: pip install mnemonic")
    Mnemonic = None

try:
    import base58
except ImportError:
    print("⚠️ base58 not installed. Run: pip install base58")
    base58 = None

try:
    from eth_account import Account
except ImportError:
    print("⚠️ eth-account not installed. Run: pip install eth-account")
    Account = None

try:
    from web3 import Web3
except ImportError:
    print("⚠️ web3 not installed. Run: pip install web3")
    Web3 = None


class WalletManager:
    """Secure wallet management with encryption"""
    
    def __init__(self, network: str = "solana"):
        self.network = network
        # Get project root and create data directory
        project_root = Path(__file__).parent.absolute()
        self.data_dir = project_root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.wallet_file = self.data_dir / "wallet.enc"
        self.cipher = self._init_cipher()
        
        # Wallet objects
        self.solana_keypair: Optional[Keypair] = None
        self.bsc_account: Optional[Account] = None
        self.wallet_address: Optional[str] = None
        
    def _init_cipher(self) -> Fernet:
        """Initialize encryption cipher"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # Generate new key
            key = Fernet.generate_key()
            # Save to .env
            project_root = Path(__file__).parent.absolute()
            env_path = project_root / ".env"
            if env_path.exists():
                with open(env_path, 'a') as f:
                    f.write(f"\nENCRYPTION_KEY={key.decode()}\n")
            os.environ['ENCRYPTION_KEY'] = key.decode()
            print("Generated new encryption key")
        else:
            key = key.encode() if isinstance(key, str) else key

        return Fernet(key)
    
    def load_from_env(self) -> bool:
        """Load wallet from environment variables"""
        private_key = os.getenv('WALLET_PRIVATE_KEY', '').strip()
        seed_phrase = os.getenv('WALLET_SEED_PHRASE', '').strip()
        
        if private_key:
            print("Loading wallet from private key...")
            return self.import_private_key(private_key)
        elif seed_phrase:
            print("Loading wallet from seed phrase...")
            return self.import_seed_phrase(seed_phrase)
        else:
            print("⚠️  No wallet configured in .env file")
            print("   Please add WALLET_PRIVATE_KEY or WALLET_SEED_PHRASE")
            return False
    
    def import_private_key(self, private_key: str) -> bool:
        """Import wallet from private key"""
        try:
            private_key = private_key.strip()
            
            if self.network == "solana":
                if not Keypair:
                    print("❌ Solana libraries not installed")
                    return False
                
                # Try different Solana key formats
                try:
                    # Format 1: Base58 encoded
                    self.solana_keypair = Keypair.from_base58_string(private_key)
                except:
                    try:
                        # Format 2: JSON array [1,2,3,...]
                        key_bytes = bytes(json.loads(private_key))
                        self.solana_keypair = Keypair.from_bytes(key_bytes)
                    except:
                        try:
                            # Format 3: Hex string
                            private_key = private_key.replace('0x', '')
                            key_bytes = bytes.fromhex(private_key)
                            self.solana_keypair = Keypair.from_bytes(key_bytes)
                        except Exception as e:
                            print(f"❌ Failed to parse Solana private key: {e}")
                            return False
                
                self.wallet_address = str(self.solana_keypair.pubkey())
                print(f"✅ Solana wallet loaded: {self.wallet_address[:8]}...{self.wallet_address[-8:]}")
                
            elif self.network == "bsc":
                if not Account:
                    print("❌ Web3 libraries not installed")
                    return False
                
                # BSC/Ethereum private key
                if not private_key.startswith('0x'):
                    private_key = '0x' + private_key
                
                self.bsc_account = Account.from_key(private_key)
                self.wallet_address = self.bsc_account.address
                print(f"✅ BSC wallet loaded: {self.wallet_address[:8]}...{self.wallet_address[-8:]}")
            
            # Save encrypted
            self._save_wallet({'private_key': private_key, 'network': self.network})
            return True
            
        except Exception as e:
            print(f"❌ Failed to import private key: {e}")
            return False
    
    def import_seed_phrase(self, seed_phrase: str) -> bool:
        """Import wallet from seed phrase (12/24 words)"""
        try:
            if not Mnemonic:
                print("❌ Mnemonic library not installed")
                return False
            
            seed_phrase = seed_phrase.strip().lower()
            mnemo = Mnemonic("english")
            
            # Validate seed phrase
            if not mnemo.check(seed_phrase):
                print("❌ Invalid seed phrase")
                return False
            
            # Generate seed
            seed = mnemo.to_seed(seed_phrase)
            
            if self.network == "solana":
                if not Keypair:
                    print("❌ Solana libraries not installed")
                    return False
                
                # Derive Solana keypair from seed
                self.solana_keypair = Keypair.from_seed(seed[:32])
                self.wallet_address = str(self.solana_keypair.pubkey())
                print(f"✅ Solana wallet from seed: {self.wallet_address[:8]}...{self.wallet_address[-8:]}")
                
            elif self.network == "bsc":
                if not Account:
                    print("❌ Web3 libraries not installed")
                    return False
                
                # Derive BSC account from seed
                try:
                    Account.enable_unaudited_hdwallet_features()
                    self.bsc_account = Account.from_mnemonic(seed_phrase)
                    self.wallet_address = self.bsc_account.address
                    print(f"✅ BSC wallet from seed: {self.wallet_address[:8]}...{self.wallet_address[-8:]}")
                except Exception as e:
                    print(f"❌ BSC wallet derivation failed: {e}")
                    return False
            
            # Save encrypted
            self._save_wallet({
                'seed_phrase': seed_phrase,
                'network': self.network
            })
            return True
            
        except Exception as e:
            print(f"❌ Failed to import seed phrase: {e}")
            return False
    
    def _save_wallet(self, data: Dict):
        """Save encrypted wallet data"""
        try:
            encrypted = self.cipher.encrypt(json.dumps(data).encode())
            with open(self.wallet_file, 'wb') as f:
                f.write(encrypted)
            print("💾 Wallet saved (encrypted)")
        except Exception as e:
            print(f"⚠️  Failed to save wallet: {e}")
    
    def _load_wallet(self) -> Optional[Dict]:
        """Load encrypted wallet data"""
        if not self.wallet_file.exists():
            return None
        
        try:
            with open(self.wallet_file, 'rb') as f:
                encrypted = f.read()
            decrypted = self.cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"⚠️  Failed to load wallet: {e}")
            return None
    
    def get_solana_keypair(self) -> Optional[Keypair]:
        """Get Solana keypair for signing transactions"""
        return self.solana_keypair
    
    def get_bsc_account(self) -> Optional[Account]:
        """Get BSC account for signing transactions"""
        return self.bsc_account
    
    def get_address(self) -> Optional[str]:
        """Get wallet address"""
        return self.wallet_address
    
    async def get_balance(self) -> float:
        """Get wallet balance"""
        try:
            if self.network == "solana":
                if not self.solana_keypair:
                    print("⚠️  Solana wallet not loaded")
                    return 0.0
                
                try:
                    from solana.rpc.async_api import AsyncClient
                    
                    rpc_url = os.getenv('HELIUS_RPC_URL', 'https://api.mainnet-beta.solana.com')
                    async with AsyncClient(rpc_url) as client:
                        response = await client.get_balance(self.solana_keypair.pubkey())
                        balance_lamports = response.value
                        balance_sol = balance_lamports / 1e9
                        return balance_sol
                except Exception as e:
                    print(f"⚠️  Failed to get Solana balance: {e}")
                    return 0.0
                
            elif self.network == "bsc":
                if not self.bsc_account or not Web3:
                    print("⚠️  BSC wallet not loaded or Web3 not installed")
                    return 0.0
                
                try:
                    w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))
                    balance_wei = w3.eth.get_balance(self.wallet_address)
                    balance_bnb = float(w3.from_wei(balance_wei, 'ether'))
                    return balance_bnb
                except Exception as e:
                    print(f"⚠️  Failed to get BSC balance: {e}")
                    return 0.0
                
        except Exception as e:
            print(f"⚠️  Failed to get balance: {e}")
            return 0.0
    
    def display_wallet_info(self):
        """Display wallet information"""
        print("\n" + "="*70)
        print("  WALLET INFORMATION")
        print("="*70)
        print(f"Network: {self.network.upper()}")
        print(f"Address: {self.wallet_address}")
        print("="*70 + "\n")


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.absolute()
    load_dotenv(project_root / ".env")

    wallet = WalletManager(network="solana")
    if wallet.load_from_env():
        wallet.display_wallet_info()
