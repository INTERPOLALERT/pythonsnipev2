"""
Model Trainer - Train and update ML models
Simplified version for Python 3.13 compatibility
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ModelTrainer:
    """
    Model Trainer - Learn from trading history

    Continuously improves prediction accuracy by:
    - Analyzing successful trades
    - Identifying winning patterns
    - Adjusting safety thresholds
    - Optimizing entry/exit timing
    """

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger

        # Get project root and create models directory
        project_root = Path(__file__).parent.parent.parent.absolute()
        self.models_dir = project_root / "data" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.performance_file = self.models_dir / "performance_history.json"
        self.patterns_file = self.models_dir / "winning_patterns.json"

        if self.logger:
            self.logger.info("✅ Model Trainer initialized")

    async def record_trade(self, trade_data: Dict):
        """Record trade outcome for learning"""
        try:
            # Load existing history
            history = self._load_performance_history()

            # Add new trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'token': trade_data.get('token_address', 'Unknown'),
                'entry_price': trade_data.get('entry_price', 0),
                'exit_price': trade_data.get('exit_price', 0),
                'pnl_percent': trade_data.get('pnl_percent', 0),
                'win': trade_data.get('pnl_percent', 0) > 0,
                'safety_score': trade_data.get('safety_score', 0),
                'lep_confidence': trade_data.get('lep_confidence', 0),
                'virality_score': trade_data.get('virality_score', 0),
                'hold_time_minutes': trade_data.get('hold_time_minutes', 0)
            }

            history.append(trade_record)

            # Save updated history
            self._save_performance_history(history)

            # Analyze for patterns
            await self._analyze_patterns(history)

            if self.logger:
                self.logger.debug(f"Trade recorded for learning")

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to record trade: {e}")

    async def _analyze_patterns(self, history: List[Dict]):
        """Analyze trade history for winning patterns"""
        try:
            if len(history) < 10:
                # Need at least 10 trades for pattern analysis
                return

            # Separate wins and losses
            wins = [t for t in history if t.get('win', False)]
            losses = [t for t in history if not t.get('win', False)]

            if len(wins) == 0:
                return

            # Analyze winning characteristics
            patterns = {
                'total_trades': len(history),
                'wins': len(wins),
                'losses': len(losses),
                'win_rate': len(wins) / len(history) if history else 0,
                'avg_win': np.mean([t.get('pnl_percent', 0) for t in wins]),
                'avg_loss': np.mean([t.get('pnl_percent', 0) for t in losses]) if losses else 0,
                'optimal_safety_score': self._find_optimal_threshold(wins, 'safety_score'),
                'optimal_lep_confidence': self._find_optimal_threshold(wins, 'lep_confidence'),
                'optimal_virality_score': self._find_optimal_threshold(wins, 'virality_score'),
                'avg_hold_time': np.mean([t.get('hold_time_minutes', 0) for t in wins]),
                'last_updated': datetime.utcnow().isoformat()
            }

            # Save patterns
            self._save_patterns(patterns)

            if self.logger:
                self.logger.info(f"📊 Patterns updated: {patterns['win_rate']:.1%} win rate")

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Pattern analysis error: {e}")

    def _find_optimal_threshold(self, winning_trades: List[Dict], field: str) -> float:
        """Find optimal threshold for a given field"""
        try:
            values = [t.get(field, 0) for t in winning_trades if t.get(field, 0) > 0]

            if not values:
                return 0.0

            # Return median of winning trades (robust to outliers)
            return float(np.median(values))

        except Exception:
            return 0.0

    def get_recommended_thresholds(self) -> Dict:
        """Get AI-recommended thresholds based on learning"""
        try:
            patterns = self._load_patterns()

            if not patterns or patterns.get('total_trades', 0) < 10:
                # Not enough data, return config defaults
                return {
                    'safety_score': self.config.safety_threshold,
                    'lep_confidence': self.config.lep_min_confidence,
                    'virality_score': self.config.cascade_min_virality,
                    'source': 'config_defaults'
                }

            # Return learned thresholds
            return {
                'safety_score': patterns.get('optimal_safety_score', self.config.safety_threshold),
                'lep_confidence': patterns.get('optimal_lep_confidence', self.config.lep_min_confidence),
                'virality_score': patterns.get('optimal_virality_score', self.config.cascade_min_virality),
                'source': 'ai_learned',
                'based_on_trades': patterns.get('total_trades', 0),
                'win_rate': patterns.get('win_rate', 0)
            }

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to get thresholds: {e}")

            return {
                'safety_score': self.config.safety_threshold,
                'lep_confidence': self.config.lep_min_confidence,
                'virality_score': self.config.cascade_min_virality,
                'source': 'error_fallback'
            }

    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        try:
            patterns = self._load_patterns()

            if not patterns:
                return {
                    'total_trades': 0,
                    'win_rate': 0,
                    'message': 'No trading history yet'
                }

            return {
                'total_trades': patterns.get('total_trades', 0),
                'wins': patterns.get('wins', 0),
                'losses': patterns.get('losses', 0),
                'win_rate': patterns.get('win_rate', 0),
                'avg_win': patterns.get('avg_win', 0),
                'avg_loss': patterns.get('avg_loss', 0),
                'avg_hold_time': patterns.get('avg_hold_time', 0),
                'last_updated': patterns.get('last_updated', 'Never')
            }

        except Exception:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'message': 'Error loading performance data'
            }

    def _load_performance_history(self) -> List[Dict]:
        """Load trade history"""
        try:
            if self.performance_file.exists():
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass

        return []

    def _save_performance_history(self, history: List[Dict]):
        """Save trade history"""
        try:
            # Keep only last 1000 trades
            if len(history) > 1000:
                history = history[-1000:]

            with open(self.performance_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to save history: {e}")

    def _load_patterns(self) -> Optional[Dict]:
        """Load learned patterns"""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass

        return None

    def _save_patterns(self, patterns: Dict):
        """Save learned patterns"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to save patterns: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio
    from config_loader import TradingConfig, load_env

    async def main():
        load_env()
        config = TradingConfig("config_live.yaml")

        trainer = ModelTrainer(config)

        # Simulate recording a trade
        trade_data = {
            'token_address': 'TestToken123...',
            'entry_price': 0.00000100,
            'exit_price': 0.00000350,
            'pnl_percent': 250.0,
            'safety_score': 80,
            'lep_confidence': 0.75,
            'virality_score': 85,
            'hold_time_minutes': 45
        }

        await trainer.record_trade(trade_data)

        # Get recommendations
        thresholds = trainer.get_recommended_thresholds()
        print(f"\nRecommended Thresholds: {thresholds}")

        # Get performance summary
        summary = trainer.get_performance_summary()
        print(f"\nPerformance Summary: {summary}")

    asyncio.run(main())
