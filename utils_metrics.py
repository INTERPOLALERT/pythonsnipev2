"""
Metrics Tracker - Track trading performance
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class MetricsTracker:
    """Track and save trading metrics"""
    
    def __init__(self, mode: str = "live"):
        self.mode = mode
        self.metrics_dir = Path("Z:/pythonSnipe/data/trades")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_start = datetime.utcnow()
        self.session_file = self.metrics_dir / f"{mode}_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
    
    def save_session(self, data: Dict):
        """Save session data"""
        try:
            session_data = {
                'mode': self.mode,
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.utcnow().isoformat(),
                **data
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"💾 Session saved: {self.session_file.name}")
            
        except Exception as e:
            print(f"⚠️  Failed to save session: {e}")
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all saved sessions"""
        sessions = []
        for file in self.metrics_dir.glob(f"{self.mode}_*.json"):
            try:
                with open(file, 'r') as f:
                    sessions.append(json.load(f))
            except:
                pass
        return sessions


# Example usage
if __name__ == "__main__":
    tracker = MetricsTracker(mode="paper")
    
    # Save example session
    tracker.save_session({
        'trades': [
            {'token': 'ABC123', 'pnl': 150.0},
            {'token': 'XYZ789', 'pnl': -10.0}
        ],
        'wins': 1,
        'losses': 1,
        'final_balance': 10.5
    })
