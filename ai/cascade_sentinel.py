"""
Cascade Sentinel - Viral Potential Detector
Uses Graph Neural Network concepts to predict viral spread potential
Simplified heuristic version for Python 3.13 compatibility
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class CascadeSentinel:
    """
    Cascade Sentinel - Predict viral potential

    Analyzes social cascade patterns to predict if token will go viral:
    - Holder network effects
    - Liquidity cascade velocity
    - Social momentum indicators
    - Influencer connection mapping
    """

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.enabled = config.cascade_enabled
        self.min_virality = config.cascade_min_virality

        if self.logger and self.enabled:
            self.logger.info("✅ Cascade Sentinel initialized (heuristic mode)")

    async def predict_virality(self, token_data: Dict, social_data: Optional[Dict] = None) -> Dict:
        """
        Predict viral potential

        Returns:
            {
                'virality_score': int (0-100),
                'cascade_signals': {...},
                'recommendation': str,
                'viral_probability': float (0-1)
            }
        """
        if not self.enabled:
            return {
                'virality_score': 0,
                'cascade_signals': {},
                'recommendation': 'Cascade disabled',
                'viral_probability': 0.0
            }

        try:
            # Analyze cascade signals
            signals = {}

            # Signal 1: Network growth velocity
            signals['network_velocity'] = self._analyze_network_growth(token_data)

            # Signal 2: Holder diversity (more diverse = more viral)
            signals['holder_diversity'] = self._analyze_holder_diversity(token_data)

            # Signal 3: Early adopter quality
            signals['early_adopter_quality'] = self._analyze_early_adopters(token_data)

            # Signal 4: Liquidity cascade (rapid liquidity additions)
            signals['liquidity_cascade'] = self._analyze_liquidity_cascade(token_data)

            # Signal 5: Social momentum (if data available)
            signals['social_momentum'] = self._analyze_social_momentum(social_data)

            # Calculate virality score
            virality_score = self._calculate_virality_score(signals)

            # Calculate viral probability
            viral_probability = virality_score / 100.0

            # Generate recommendation
            recommendation = self._generate_recommendation(virality_score)

            result = {
                'virality_score': virality_score,
                'cascade_signals': signals,
                'recommendation': recommendation,
                'viral_probability': viral_probability
            }

            if self.logger and virality_score >= self.min_virality:
                self.logger.info(f"🌊 Cascade: {virality_score}/100 - HIGH VIRAL POTENTIAL")

            return result

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Cascade prediction error: {e}")

            return {
                'virality_score': 0,
                'cascade_signals': {},
                'recommendation': 'Error in prediction',
                'viral_probability': 0.0
            }

    def _analyze_network_growth(self, token_data: Dict) -> Dict:
        """Analyze how fast the holder network is growing"""
        try:
            holders = token_data.get('holders', 0)
            age_minutes = self._get_age_minutes(token_data)

            # Calculate growth rate
            if age_minutes > 0:
                growth_rate = holders / age_minutes
            else:
                growth_rate = 0

            # High growth rate = viral potential
            # >10 holders/minute = strong viral signal
            strong_growth = growth_rate > 10

            score = 0.8 if strong_growth else 0.4

            return {
                'score': score,
                'holders': holders,
                'growth_rate': growth_rate,
                'strong_growth': strong_growth
            }

        except Exception:
            return {'score': 0.5, 'holders': 0, 'growth_rate': 0, 'strong_growth': False}

    def _analyze_holder_diversity(self, token_data: Dict) -> Dict:
        """Analyze holder distribution diversity"""
        try:
            holders = token_data.get('holders', 0)
            top_holder_pct = token_data.get('top_holder_percent', 0)

            # More holders = more diverse network
            good_holder_count = holders >= 100

            # Lower top holder % = more decentralized
            decentralized = top_holder_pct < 50

            score = 0.0
            if good_holder_count:
                score += 0.5
            if decentralized:
                score += 0.5

            return {
                'score': score,
                'holders': holders,
                'top_holder_pct': top_holder_pct,
                'diverse': good_holder_count and decentralized
            }

        except Exception:
            return {'score': 0.5, 'holders': 0, 'top_holder_pct': 0, 'diverse': False}

    def _analyze_early_adopters(self, token_data: Dict) -> Dict:
        """Analyze quality of early adopters"""
        try:
            # In real implementation, would analyze wallet history of early holders
            # Are they experienced traders? Do they have history of finding gems?

            # For now, use holders as proxy
            holders = token_data.get('holders', 0)

            # 50-150 holders = good mix of early adopters
            optimal_early_adopters = 50 <= holders <= 150

            score = 0.7 if optimal_early_adopters else 0.4

            return {
                'score': score,
                'quality': 'high' if optimal_early_adopters else 'medium'
            }

        except Exception:
            return {'score': 0.5, 'quality': 'unknown'}

    def _analyze_liquidity_cascade(self, token_data: Dict) -> Dict:
        """Analyze liquidity addition patterns"""
        try:
            liquidity = token_data.get('liquidity_usd', 0)
            age_minutes = self._get_age_minutes(token_data)

            # Calculate liquidity growth rate
            if age_minutes > 0:
                liq_per_minute = liquidity / age_minutes
            else:
                liq_per_minute = 0

            # High liquidity growth = cascade effect
            # >$1000/minute = strong cascade
            strong_cascade = liq_per_minute > 1000

            score = 0.8 if strong_cascade else 0.4

            return {
                'score': score,
                'liquidity': liquidity,
                'liq_per_minute': liq_per_minute,
                'strong_cascade': strong_cascade
            }

        except Exception:
            return {'score': 0.5, 'liquidity': 0, 'liq_per_minute': 0, 'strong_cascade': False}

    def _analyze_social_momentum(self, social_data: Optional[Dict]) -> Dict:
        """Analyze social media momentum"""
        try:
            if not social_data:
                # No social data available
                return {'score': 0.5, 'momentum': 'unknown'}

            # Analyze mentions, sentiment, influencer activity
            # This would integrate with Twitter/Telegram APIs

            # For now, return neutral score
            return {'score': 0.5, 'momentum': 'neutral'}

        except Exception:
            return {'score': 0.5, 'momentum': 'unknown'}

    def _calculate_virality_score(self, signals: Dict) -> int:
        """Calculate overall virality score (0-100)"""
        try:
            # Weighted average of all signals
            weights = {
                'network_velocity': 0.25,
                'holder_diversity': 0.20,
                'early_adopter_quality': 0.20,
                'liquidity_cascade': 0.25,
                'social_momentum': 0.10
            }

            score = 0.0
            for signal_name, weight in weights.items():
                signal = signals.get(signal_name, {})
                signal_score = signal.get('score', 0.0)
                score += signal_score * weight

            # Convert to 0-100
            return int(score * 100)

        except Exception:
            return 0

    def _generate_recommendation(self, virality_score: int) -> str:
        """Generate recommendation based on virality score"""
        if virality_score >= 90:
            return "VIRAL ALERT - Extremely high viral potential"
        elif virality_score >= 75:
            return "STRONG VIRAL - High viral potential"
        elif virality_score >= 60:
            return "MODERATE VIRAL - Some viral potential"
        elif virality_score >= 40:
            return "LOW VIRAL - Limited viral potential"
        else:
            return "NO VIRAL - Unlikely to go viral"

    def _get_age_minutes(self, token_data: Dict) -> float:
        """Get token age in minutes"""
        try:
            timestamp = token_data.get('timestamp', datetime.utcnow())

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            age = datetime.utcnow() - timestamp
            return age.total_seconds() / 60

        except Exception:
            return 1.0  # Default to 1 minute


# Example usage
if __name__ == "__main__":
    import asyncio
    from config_loader import TradingConfig, load_env

    async def main():
        load_env()
        config = TradingConfig("config_live.yaml")

        sentinel = CascadeSentinel(config)

        # Test prediction
        token_data = {
            'address': 'TestToken123...',
            'liquidity_usd': 20000,
            'holders': 120,
            'top_holder_percent': 40,
            'timestamp': datetime.utcnow()
        }

        result = await sentinel.predict_virality(token_data)
        print(f"\nVirality Prediction: {result}")

    asyncio.run(main())
