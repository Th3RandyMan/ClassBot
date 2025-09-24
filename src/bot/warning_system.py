"""
Persistent Warning System for Discord Bot
Handles user warnings with automatic expiration and JSON storage
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PersistentWarningSystem:
    """Persistent warning system with JSON storage and auto-expiration"""
    
    def __init__(self, filename="data/warnings.json", expiry_days=30):
        self.filename = filename
        self.expiry_days = expiry_days
        self.warnings: Dict[int, List[Dict]] = {}
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        self.load_warnings()
        
    def load_warnings(self):
        """Load warnings from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to int and parse timestamps
                    self.warnings = {}
                    for user_id, warning_list in data.items():
                        self.warnings[int(user_id)] = []
                        for warning in warning_list:
                            if isinstance(warning, dict):
                                # New format with timestamp
                                self.warnings[int(user_id)].append({
                                    'reason': warning['reason'],
                                    'timestamp': datetime.fromisoformat(warning['timestamp'])
                                })
                            else:
                                # Old format - add current timestamp
                                self.warnings[int(user_id)].append({
                                    'reason': warning,
                                    'timestamp': datetime.now()
                                })
                logger.info(f"Loaded {len(self.warnings)} user warning records")
            else:
                logger.info("No existing warnings file found - starting fresh")
        except Exception as e:
            logger.error(f"Error loading warnings: {e}")
            self.warnings = {}
    
    def save_warnings(self):
        """Save warnings to JSON file"""
        try:
            # Clean expired warnings before saving
            self.cleanup_expired_warnings()
            
            # Convert to serializable format
            data = {}
            for user_id, warning_list in self.warnings.items():
                data[str(user_id)] = []
                for warning in warning_list:
                    data[str(user_id)].append({
                        'reason': warning['reason'],
                        'timestamp': warning['timestamp'].isoformat()
                    })
            
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved warnings to {self.filename}")
        except Exception as e:
            logger.error(f"Error saving warnings: {e}")
    
    def cleanup_expired_warnings(self):
        """Remove warnings older than expiry_days"""
        cutoff_date = datetime.now() - timedelta(days=self.expiry_days)
        expired_count = 0
        
        for user_id in list(self.warnings.keys()):
            original_count = len(self.warnings[user_id])
            self.warnings[user_id] = [
                warning for warning in self.warnings[user_id]
                if warning['timestamp'] > cutoff_date
            ]
            expired_count += original_count - len(self.warnings[user_id])
            
            # Remove empty user records
            if not self.warnings[user_id]:
                del self.warnings[user_id]
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired warnings")
    
    def add_warning(self, user_id: int, reason: str) -> int:
        """Add a warning for a user"""
        if user_id not in self.warnings:
            self.warnings[user_id] = []
        
        warning = {
            'reason': reason,
            'timestamp': datetime.now()
        }
        self.warnings[user_id].append(warning)
        self.save_warnings()
        return len(self.warnings[user_id])
    
    def get_warnings(self, user_id: int) -> List[Dict]:
        """Get all warnings for a user"""
        self.cleanup_expired_warnings()
        return self.warnings.get(user_id, [])
    
    def get_warning_count(self, user_id: int) -> int:
        """Get warning count for a user"""
        return len(self.get_warnings(user_id))
    
    def clear_warnings(self, user_id: int) -> bool:
        """Clear all warnings for a user"""
        if user_id in self.warnings:
            del self.warnings[user_id]
            self.save_warnings()
            return True
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get warning system statistics"""
        self.cleanup_expired_warnings()
        total_users = len(self.warnings)
        total_warnings = sum(len(warnings) for warnings in self.warnings.values())
        return {
            'total_users_with_warnings': total_users, 
            'total_active_warnings': total_warnings
        }