"""
Configuration Loader - Load and manage bot settings
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TradingConfig:
    """Trading configuration with all settings"""
    
    def __init__(self, config_file: str = "config_live.yaml"):
        # Get project root directory (parent of src/)
        project_root = Path(__file__).parent.parent.absolute()
        self.config_path = project_root / "config" / config_file

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        # Load YAML
        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Parse configuration
        self._parse_config(data)
    
    def _parse_config(self, data: Dict[str, Any]):
        """Parse configuration from YAML"""
        
        # Paper mode
        self.paper_mode = data.get('paper_mode', {}).get('enabled', False)
        self.initial_balance_sol = data.get('paper_mode', {}).get('initial_balance_sol', 10.0)
        self.initial_balance_bnb = data.get('paper_mode', {}).get('initial_balance_bnb', 1.0)
        self.use_real_prices = data.get('paper_mode', {}).get('use_real_prices', True)
        self.simulate_slippage = data.get('paper_mode', {}).get('simulate_slippage', True)
        
        # Network
        self.network = data.get('network', 'solana')
        
        # Investment
        investment = data.get('investment', {})
        self.amount_sol = investment.get('amount_sol', 0.05)
        self.amount_bnb = investment.get('amount_bnb', 0.01)
        self.min_balance = investment.get('min_balance', 0.1)
        self.max_daily_sol = investment.get('max_daily_sol', 2.0)
        self.max_daily_bnb = investment.get('max_daily_bnb', 0.5)
        
        # Strategy
        strategy = data.get('strategy', {})
        self.take_profit = strategy.get('take_profit', 300)
        self.stop_loss = strategy.get('stop_loss', 20)
        self.trailing_stop = strategy.get('trailing_stop', True)
        self.trailing_distance = strategy.get('trailing_distance', 20)
        
        # Safety
        safety = data.get('safety', {})
        self.max_open_positions = safety.get('max_open_positions', 1)
        self.safety_threshold = safety.get('safety_threshold', 70)
        self.rugcheck_min_score = safety.get('rugcheck_min_score', 7)
        self.min_liquidity_usd = safety.get('min_liquidity_usd', 5000)
        self.min_holders = safety.get('min_holders', 50)
        self.max_top_holder_percent = safety.get('max_top_holder_percent', 60)
        self.max_token_age_minutes = safety.get('max_token_age_minutes', 5)
        self.check_honeypot = safety.get('check_honeypot', True)
        self.check_renounced = safety.get('check_renounced', False)
        
        # Monitoring
        monitoring = data.get('monitoring', {})
        self.poll_interval_sol = monitoring.get('poll_interval_sol', 0.5)
        self.use_websocket_sol = monitoring.get('use_websocket_sol', True)
        self.poll_interval_bsc = monitoring.get('poll_interval_bsc', 3.0)
        self.use_websocket_bsc = monitoring.get('use_websocket_bsc', False)
        
        # Dev analyzer
        dev = data.get('dev_analyzer', {})
        self.dev_analyzer_enabled = dev.get('enabled', True)
        self.dev_min_score = dev.get('min_score', 70)
        self.dev_weights = dev.get('weights', {})
        
        # AI/ML
        lep = data.get('lep', {})
        self.lep_enabled = lep.get('enabled', True)
        self.lep_min_confidence = lep.get('min_confidence', 0.6)
        self.lep_use_heuristics = lep.get('use_heuristics', True)
        
        cascade = data.get('cascade', {})
        self.cascade_enabled = cascade.get('enabled', True)
        self.cascade_min_virality = cascade.get('min_virality_score', 75)
        
        # Execution
        execution = data.get('execution', {})
        self.use_jito = execution.get('use_jito', True)
        self.force_jito = execution.get('force_jito', True)
        self.jito_tip_sol = execution.get('jito_tip_sol', 0.01)
        self.slippage = execution.get('slippage', 5.0)
        self.gas_price_gwei = execution.get('gas_price_gwei', 5)
        self.gas_limit = execution.get('gas_limit', 500000)
        
        # RPC
        rpc = data.get('rpc', {})
        self.solana_endpoints = rpc.get('solana_endpoints', [])
        self.solana_websocket = rpc.get('solana_websocket', '')
        self.bsc_endpoints = rpc.get('bsc_endpoints', [])
        
        # Telegram
        telegram = data.get('telegram', {})
        self.telegram_enabled = telegram.get('enabled', False)
        self.telegram_alert_buy = telegram.get('alert_on_buy', True)
        self.telegram_alert_sell = telegram.get('alert_on_sell', True)
        self.telegram_alert_rug = telegram.get('alert_on_rug_detected', True)
        self.telegram_alert_error = telegram.get('alert_on_error', True)
        
        # Logging
        logging = data.get('logging', {})
        self.console_log_level = logging.get('console_level', 'INFO')
        self.file_log_level = logging.get('file_level', 'DEBUG')
        self.save_trades = logging.get('save_trades', True)
        self.max_log_files = logging.get('max_log_files', 30)
    
    def get_investment_amount(self) -> float:
        """Get investment amount for current network"""
        if self.network == 'solana':
            return self.amount_sol
        elif self.network == 'bsc':
            return self.amount_bnb
        return 0.05
    
    def get_max_daily(self) -> float:
        """Get max daily spend for current network"""
        if self.network == 'solana':
            return self.max_daily_sol
        elif self.network == 'bsc':
            return self.max_daily_bnb
        return 2.0
    
    def get_rpc_endpoint(self) -> str:
        """Get primary RPC endpoint"""
        if self.network == 'solana':
            return self.solana_endpoints[0] if self.solana_endpoints else ''
        elif self.network == 'bsc':
            return self.bsc_endpoints[0] if self.bsc_endpoints else ''
        return ''
    
    def display_config(self):
        """Display configuration summary"""
        print("\n" + "="*70)
        print("  CONFIGURATION SUMMARY")
        print("="*70)
        print(f"Mode: {'PAPER' if self.paper_mode else 'LIVE'} TRADING")
        print(f"Network: {self.network.upper()}")
        print(f"Investment per trade: {self.get_investment_amount()} {self.network.upper()}")
        print(f"Take Profit: {self.take_profit}%")
        print(f"Stop Loss: {self.stop_loss}%")
        print(f"Trailing Stop: {'Enabled' if self.trailing_stop else 'Disabled'}")
        print(f"Safety Threshold: {self.safety_threshold}/100")
        print(f"Max Daily Spend: {self.get_max_daily()} {self.network.upper()}")
        print("="*70 + "\n")


# Load environment variables
def load_env():
    """Load environment variables from .env file"""
    from dotenv import load_dotenv
    # Get project root directory (parent of src/)
    project_root = Path(__file__).parent.parent.absolute()
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment variables loaded")
        return True
    else:
        print(f"⚠️  .env file not found at {env_path}")
        print("   Creating from .env.example...")
        # Try to copy from .env.example
        example_path = project_root / ".env.example"
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print(f"✅ Created .env file. Please edit {env_path} with your wallet details.")
            load_dotenv(env_path)
            return True
        return False


# Get project root directory
def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent.absolute()


# Example usage
if __name__ == "__main__":
    load_env()
    config = TradingConfig("config_live.yaml")
    config.display_config()
