import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from models.metrics import MonthlyMetrics, MetricsEvent
from loguru import logger

class MetricsService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.metrics_file = self.data_dir / "metrics.json"
        
    def _load_metrics(self) -> Dict[str, Dict]:
        """Load metrics from JSON file."""
        if not self.metrics_file.exists():
            return {}
        
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert unique_users lists back to sets
                for month_key in data:
                    if 'unique_users' in data[month_key]:
                        data[month_key]['unique_users'] = set(data[month_key]['unique_users'])
                return data
        except Exception as e:
            logger.error(f"Error loading metrics: {e}")
            return {}
    
    def _save_metrics(self, metrics: Dict[str, Dict]) -> None:
        """Save metrics to JSON file."""
        try:
            # Convert sets to lists for JSON serialization
            serializable_data = {}
            for month_key, month_data in metrics.items():
                serializable_data[month_key] = month_data.copy()
                if 'unique_users' in serializable_data[month_key]:
                    serializable_data[month_key]['unique_users'] = list(serializable_data[month_key]['unique_users'])
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def _get_month_key(self, date: Optional[datetime] = None) -> str:
        """Get month key in format YYYY-MM."""
        if date is None:
            date = datetime.now()
        return date.strftime("%Y-%m")
    
    def track_event(self, event: MetricsEvent) -> None:
        """Track a metrics event."""
        month_key = self._get_month_key(event.timestamp)
        metrics = self._load_metrics()
        
        # Initialize month if not exists
        if month_key not in metrics:
            metrics[month_key] = {
                'unique_users': set(),
                'transcriptions': 0,
                'llm_calls': {"proofread": 0, "my": 0, "business": 0, "brief": 0}
            }
        
        # Add user to unique users
        metrics[month_key]['unique_users'].add(event.user_id)
        
        # Track event
        if event.event_type == "transcription":
            metrics[month_key]['transcriptions'] += 1
        elif event.event_type == "llm_call" and event.event_subtype:
            if event.event_subtype in metrics[month_key]['llm_calls']:
                metrics[month_key]['llm_calls'][event.event_subtype] += 1
        
        self._save_metrics(metrics)
        logger.debug(f"Tracked event: {event.event_type} for user {event.user_id}")
    
    def get_month_stats(self, month_key: Optional[str] = None) -> Optional[MonthlyMetrics]:
        """Get statistics for a specific month."""
        if month_key is None:
            month_key = self._get_month_key()
        
        metrics = self._load_metrics()
        if month_key not in metrics:
            return None
        
        month_data = metrics[month_key]
        return MonthlyMetrics(
            unique_users=month_data.get('unique_users', set()),
            transcriptions=month_data.get('transcriptions', 0),
            llm_calls=month_data.get('llm_calls', {"proofread": 0, "my": 0, "business": 0, "brief": 0})
        )
    
    def get_all_months(self) -> Dict[str, MonthlyMetrics]:
        """Get statistics for all months."""
        metrics = self._load_metrics()
        result = {}
        
        for month_key, month_data in metrics.items():
            result[month_key] = MonthlyMetrics(
                unique_users=month_data.get('unique_users', set()),
                transcriptions=month_data.get('transcriptions', 0),
                llm_calls=month_data.get('llm_calls', {"proofread": 0, "my": 0, "business": 0, "brief": 0})
            )
        
        return result