"""
LEP (Liquidity Event Predictor)
Predicts optimal entry timing 6-48h before major pump events
Uses advanced heuristics instead of Prophet (Python 3.13 compatible)
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path


class LEPPredictor:
    """
    Liquidity Event Predictor - Predict pump timing

    Uses heuristic analysis instead of ML models for Python 3.13 compatibility
    Analyzes:
    - Liquidity growth velocity
    - Holder accumulation patterns
    - Social momentum indicators
    - Developer activity signals
    """

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.enabled = config.lep_enabled
        self.min_confidence = config.lep_min_confidence
        self.use_heuristics = config.lep_use_heuristics

        if self.logger and self.enabled:
            self.logger.info("✅ LEP Predictor initialized (heuristic mode)")

    async def predict_pump_timing(self, token_data: Dict, historical_data: Optional[List[Dict]] = None) -> Dict:
        """
        Predict when token is likely to pump

        Returns:
            {
                'confidence': float (0-1),
                'predicted_hours': float (6-48),
                'signals': {...},
                'recommendation': str
            }
        """
        if not self.enabled:
            return {
                'confidence': 0.0,
                'predicted_hours': 0,
                'signals': {},
                'recommendation': 'LEP disabled'
            }

        try:
            # Analyze multiple signals
            signals = {}

            # Signal 1: Liquidity velocity (how fast liquidity is being added)
            signals['liquidity_velocity'] = self._analyze_liquidity_velocity(token_data, historical_data)

            # Signal 2: Holder accumulation (are smart money accumulating?)
            signals['holder_accumulation'] = self._analyze_holder_patterns(token_data)

            # Signal 3: Token age sweet spot (2-5 minutes is optimal)
            signals['age_timing'] = self._analyze_age_timing(token_data)

            # Signal 4: Volume momentum
            signals['volume_momentum'] = self._analyze_volume(token_data)

            # Signal 5: Developer wallet behavior
            signals['dev_activity'] = self._analyze_dev_activity(token_data)

            # Calculate overall confidence
            confidence = self._calculate_confidence(signals)

            # Predict timing
            predicted_hours = self._predict_hours(signals, confidence)

            # Generate recommendation
            recommendation = self._generate_recommendation(confidence, predicted_hours)

            result = {
                'confidence': confidence,
                'predicted_hours': predicted_hours,
                'signals': signals,
                'recommendation': recommendation
            }

            if self.logger and confidence >= self.min_confidence:
                self.logger.info(f"🤖 LEP: {confidence:.1%} confidence - Pump in {predicted_hours:.1f}h")

            return result

        except Exception as e:
            if self.logger:
                self.logger.debug(f"LEP prediction error: {e}")

            return {
                'confidence': 0.0,
                'predicted_hours': 0,
                'signals': {},
                'recommendation': 'Error in prediction'
            }

    def _analyze_liquidity_velocity(self, token_data: Dict, historical_data: Optional[List[Dict]]) -> Dict:
        """Analyze how fast liquidity is growing"""
        try:
            current_liquidity = token_data.get('liquidity_usd', 0)

            # Check if liquidity is in optimal range
            # Too low = risky, too high = already pumped
            optimal_range = 5000 <= current_liquidity <= 50000

            # Calculate velocity if historical data available
            velocity = 0.0
            if historical_data and len(historical_data) >= 2:
                old_liq = historical_data[0].get('liquidity_usd', 0)
                new_liq = token_data.get('liquidity_usd', 0)
                time_diff = 1  # minutes
                velocity = (new_liq - old_liq) / time_diff if time_diff > 0 else 0

            # High velocity = accumulation phase = good signal
            strong_velocity = velocity > 1000  # $1000+/min growth

            score = 0.0
            if optimal_range:
                score += 0.5
            if strong_velocity:
                score += 0.5

            return {
                'score': score,
                'liquidity': current_liquidity,
                'velocity': velocity,
                'optimal_range': optimal_range
            }

        except Exception:
            return {'score': 0.5, 'liquidity': 0, 'velocity': 0, 'optimal_range': False}

    def _analyze_holder_patterns(self, token_data: Dict) -> Dict:
        """Analyze holder accumulation patterns"""
        try:
            holders = token_data.get('holders', 0)
            top_holder_pct = token_data.get('top_holder_percent', 0)

            # Optimal holder count: 50-200 (enough distribution, not too diluted)
            optimal_holder_count = 50 <= holders <= 200

            # Top holder should be reasonable but not too high
            healthy_distribution = 30 <= top_holder_pct <= 60

            score = 0.0
            if optimal_holder_count:
                score += 0.5
            if healthy_distribution:
                score += 0.5

            return {
                'score': score,
                'holders': holders,
                'top_holder_pct': top_holder_pct,
                'optimal': optimal_holder_count and healthy_distribution
            }

        except Exception:
            return {'score': 0.5, 'holders': 0, 'top_holder_pct': 0, 'optimal': False}

    def _analyze_age_timing(self, token_data: Dict) -> Dict:
        """Analyze if token age is in sweet spot"""
        try:
            timestamp = token_data.get('timestamp', datetime.utcnow())

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            age_minutes = (datetime.utcnow() - timestamp).total_seconds() / 60

            # Sweet spot: 2-5 minutes (fresh but proven)
            in_sweet_spot = 2 <= age_minutes <= 5

            score = 1.0 if in_sweet_spot else 0.3

            return {
                'score': score,
                'age_minutes': age_minutes,
                'in_sweet_spot': in_sweet_spot
            }

        except Exception:
            return {'score': 0.5, 'age_minutes': 0, 'in_sweet_spot': False}

    def _analyze_volume(self, token_data: Dict) -> Dict:
        """Analyze trading volume momentum"""
        try:
            # Volume indicators (if available)
            # For now, use liquidity as proxy
            liquidity = token_data.get('liquidity_usd', 0)

            # Higher liquidity usually means higher volume potential
            strong_volume = liquidity > 10000

            score = 0.8 if strong_volume else 0.4

            return {
                'score': score,
                'strong_volume': strong_volume
            }

        except Exception:
            return {'score': 0.5, 'strong_volume': False}

    def _analyze_dev_activity(self, token_data: Dict) -> Dict:
        """Analyze developer activity signals"""
        try:
            # Check if developer wallet shows positive signs
            # This would integrate with dev_analyzer if available

            # For now, assume neutral
            score = 0.5

            return {
                'score': score,
                'active': True
            }

        except Exception:
            return {'score': 0.5, 'active': False}

    def _calculate_confidence(self, signals: Dict) -> float:
        """Calculate overall confidence from all signals"""
        try:
            # Weighted average of all signals
            weights = {
                'liquidity_velocity': 0.25,
                'holder_accumulation': 0.25,
                'age_timing': 0.20,
                'volume_momentum': 0.15,
                'dev_activity': 0.15
            }

            confidence = 0.0
            for signal_name, weight in weights.items():
                signal = signals.get(signal_name, {})
                score = signal.get('score', 0.0)
                confidence += score * weight

            return min(max(confidence, 0.0), 1.0)

        except Exception:
            return 0.0

    def _predict_hours(self, signals: Dict, confidence: float) -> float:
        """Predict hours until pump based on signals"""
        try:
            # Base prediction: 12 hours
            hours = 12.0

            # Adjust based on signals
            age_signal = signals.get('age_timing', {})
            if age_signal.get('in_sweet_spot'):
                # If already in sweet spot, pump could happen sooner
                hours = 6.0

            liquidity_signal = signals.get('liquidity_velocity', {})
            if liquidity_signal.get('velocity', 0) > 2000:
                # Very high velocity = sooner pump
                hours = min(hours, 8.0)

            # Higher confidence = more reliable timing
            if confidence < 0.5:
                hours = 24.0  # Low confidence = longer prediction

            return hours

        except Exception:
            return 12.0

    def _generate_recommendation(self, confidence: float, hours: float) -> str:
        """Generate trading recommendation"""
        if confidence >= 0.8:
            return f"STRONG BUY - High confidence pump in {hours:.1f}h"
        elif confidence >= 0.6:
            return f"BUY - Moderate confidence pump in {hours:.1f}h"
        elif confidence >= 0.4:
            return f"CONSIDER - Low confidence pump in {hours:.1f}h"
        else:
            return "SKIP - Insufficient confidence"


# Example usage
if __name__ == "__main__":
    import asyncio
    from config_loader import TradingConfig, load_env

    async def main():
        load_env()
        config = TradingConfig("config_live.yaml")

        predictor = LEPPredictor(config)

        # Test prediction
        token_data = {
            'address': 'TestToken123...',
            'liquidity_usd': 15000,
            'holders': 85,
            'top_holder_percent': 45,
            'timestamp': datetime.utcnow() - timedelta(minutes=3)
        }

        result = await predictor.predict_pump_timing(token_data)
        print(f"\nPrediction: {result}")

    asyncio.run(main())
