import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class RateLimiterService:
    def __init__(self, data_dir: str = "data", max_requests_per_hour: int = 5, admin_user_id: int = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.rate_limit_file = self.data_dir / "rate_limits.json"
        self.max_requests_per_hour = max_requests_per_hour
        self.admin_user_id = admin_user_id
    
    def _load_rate_limits(self) -> Dict[str, List[str]]:
        """Load rate limit data from JSON file."""
        if not self.rate_limit_file.exists():
            return {}
        
        try:
            with open(self.rate_limit_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading rate limits: {e}")
            return {}
    
    def _save_rate_limits(self, rate_limits: Dict[str, List[str]]) -> None:
        """Save rate limit data to JSON file."""
        try:
            with open(self.rate_limit_file, 'w', encoding='utf-8') as f:
                json.dump(rate_limits, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving rate limits: {e}")
    
    def _clean_old_requests(self, timestamps: List[str]) -> List[str]:
        """Remove timestamps older than 1 hour."""
        cutoff_time = datetime.now() - timedelta(hours=1)
        return [
            ts for ts in timestamps 
            if datetime.fromisoformat(ts) > cutoff_time
        ]
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin."""
        if not self.admin_user_id:
            return False
        return str(self.admin_user_id) == str(user_id)
    
    def can_make_request(self, user_id: str, username: str = None) -> bool:
        """Check if user can make a transcription request."""
        # Admin users have no limits
        if self.is_admin(user_id):
            logger.debug(f"Admin user {user_id} bypassing rate limit")
            return True
        
        rate_limits = self._load_rate_limits()
        
        # Get user's request history
        user_requests = rate_limits.get(user_id, [])
        
        # Clean old requests
        user_requests = self._clean_old_requests(user_requests)
        
        # Check if under limit
        return len(user_requests) < self.max_requests_per_hour
    
    def record_request(self, user_id: str, username: str = None) -> None:
        """Record a transcription request for the user."""
        # Don't record for admins to keep data clean
        if self.is_admin(user_id):
            return
        
        rate_limits = self._load_rate_limits()
        
        # Get user's request history
        user_requests = rate_limits.get(user_id, [])
        
        # Clean old requests
        user_requests = self._clean_old_requests(user_requests)
        
        # Add current request
        user_requests.append(datetime.now().isoformat())
        
        # Update and save
        rate_limits[user_id] = user_requests
        self._save_rate_limits(rate_limits)
        
        logger.debug(f"Recorded request for user {user_id}. Total in last hour: {len(user_requests)}")
    
    def get_remaining_requests(self, user_id: str, username: str = None) -> int:
        """Get number of remaining requests for the user."""
        # Admin users have unlimited requests
        if self.is_admin(user_id):
            return float('inf')
        
        rate_limits = self._load_rate_limits()
        
        # Get user's request history
        user_requests = rate_limits.get(user_id, [])
        
        # Clean old requests
        user_requests = self._clean_old_requests(user_requests)
        
        return max(0, self.max_requests_per_hour - len(user_requests))
    
    def get_time_until_next_request(self, user_id: str, username: str = None) -> timedelta:
        """Get time until user can make next request."""
        # Admin users can always make requests
        if self.is_admin(user_id):
            return timedelta(0)
        
        rate_limits = self._load_rate_limits()
        
        # Get user's request history
        user_requests = rate_limits.get(user_id, [])
        
        if len(user_requests) < self.max_requests_per_hour:
            return timedelta(0)
        
        # Find oldest request in the current hour window
        oldest_request = min(user_requests, key=lambda x: datetime.fromisoformat(x))
        oldest_time = datetime.fromisoformat(oldest_request)
        
        # Time when oldest request will be 1 hour old
        next_available = oldest_time + timedelta(hours=1)
        
        return max(timedelta(0), next_available - datetime.now())