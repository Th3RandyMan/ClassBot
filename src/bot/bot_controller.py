"""
Bot control system for managing bot state and operations.
Provides commands for disabling, enabling, and shutting down the bot.
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BotController:
    def __init__(self, config_path: str = "config/bot_control.json"):
        """Initialize the bot controller with configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load bot control configuration from JSON file."""
        default_config = {
            "enabled": True,
            "disabled_until": None,
            "disabled_reason": None,
            "disabled_by": None,
            "disabled_timestamp": None,
            "maintenance_mode": False,
            "allowed_commands_when_disabled": [
                "bot_enable",
                "bot_status", 
                "bot_kill",
                "help"
            ]
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return default_config
                
        except Exception as e:
            logger.error(f"Error loading bot control config: {e}")
            return default_config
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving bot control config: {e}")
    
    def is_enabled(self) -> bool:
        """Check if the bot is currently enabled."""
        if not self.config["enabled"]:
            # Check if temporary disable has expired
            if self.config["disabled_until"]:
                try:
                    disable_until = datetime.fromisoformat(self.config["disabled_until"])
                    if datetime.now() >= disable_until:
                        # Auto-enable the bot
                        self.enable_bot("System", "Automatic re-enable after timeout")
                        return True
                except Exception as e:
                    logger.error(f"Error parsing disabled_until timestamp: {e}")
            return False
        return True
    
    def disable_bot(self, duration: Optional[int] = None, reason: str = "Manual disable", user: str = "Unknown"):
        """
        Disable the bot temporarily or permanently.
        
        Args:
            duration: Duration in minutes (None for permanent)
            reason: Reason for disabling
            user: User who disabled the bot
        """
        self.config["enabled"] = False
        self.config["disabled_reason"] = reason
        self.config["disabled_by"] = user
        self.config["disabled_timestamp"] = datetime.now().isoformat()
        
        if duration:
            disable_until = datetime.now() + timedelta(minutes=duration)
            self.config["disabled_until"] = disable_until.isoformat()
        else:
            self.config["disabled_until"] = None
        
        self._save_config()
        logger.info(f"Bot disabled by {user}: {reason} (duration: {duration} minutes)")
    
    def enable_bot(self, user: str = "Unknown", reason: str = "Manual enable"):
        """
        Enable the bot and clear disable settings.
        
        Args:
            user: User who enabled the bot
            reason: Reason for enabling
        """
        self.config["enabled"] = True
        self.config["disabled_until"] = None
        self.config["disabled_reason"] = None
        self.config["disabled_by"] = None
        self.config["disabled_timestamp"] = None
        self.config["maintenance_mode"] = False
        
        self._save_config()
        logger.info(f"Bot enabled by {user}: {reason}")
    
    def set_maintenance_mode(self, enabled: bool, user: str = "Unknown"):
        """
        Enable or disable maintenance mode.
        
        Args:
            enabled: True to enable maintenance mode
            user: User who changed maintenance mode
        """
        self.config["maintenance_mode"] = enabled
        if enabled:
            self.config["enabled"] = False
            self.config["disabled_reason"] = "Maintenance mode"
            self.config["disabled_by"] = user
            self.config["disabled_timestamp"] = datetime.now().isoformat()
        else:
            self.enable_bot(user, "Maintenance mode disabled")
        
        self._save_config()
        logger.info(f"Maintenance mode {'enabled' if enabled else 'disabled'} by {user}")
    
    def can_execute_command(self, command_name: str) -> bool:
        """
        Check if a command can be executed in the current bot state.
        
        Args:
            command_name: Name of the command to check
            
        Returns:
            True if command can be executed
        """
        if self.is_enabled():
            return True
        
        # If bot is disabled, only allow certain commands
        return command_name in self.config["allowed_commands_when_disabled"]
    
    def get_status(self) -> dict:
        """Get current bot status information."""
        status = {
            "enabled": self.is_enabled(),
            "maintenance_mode": self.config.get("maintenance_mode", False),
            "disabled_reason": self.config.get("disabled_reason"),
            "disabled_by": self.config.get("disabled_by"),
            "disabled_timestamp": self.config.get("disabled_timestamp"),
            "disabled_until": self.config.get("disabled_until")
        }
        
        # Add OCR status information
        ocr_status = self.get_ocr_status()
        status["ocr"] = ocr_status
        
        # Calculate remaining time if temporarily disabled
        if status["disabled_until"]:
            try:
                disable_until = datetime.fromisoformat(status["disabled_until"])
                remaining = disable_until - datetime.now()
                if remaining.total_seconds() > 0:
                    status["remaining_minutes"] = int(remaining.total_seconds() / 60)
                else:
                    status["remaining_minutes"] = 0
            except:
                status["remaining_minutes"] = None
        
        return status

    def get_ocr_status(self) -> dict:
        """Get OCR system status information."""
        try:
            # Check OCR availability by testing the code detector
            import sys
            import os
            
            # Add the correct path for imports
            main_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, os.path.join(main_dir, 'src'))
            
            from bot.utils.code_detection import CodeDetector
            
            # Create a temporary detector to check OCR status
            detector = CodeDetector()
            ocr_available = detector.is_ocr_available()
            
            # Try to get version information if available
            version_info = "Unknown"
            if ocr_available:
                try:
                    import pytesseract
                    version_info = str(pytesseract.get_tesseract_version())
                except Exception as e:
                    version_info = "Available (version check failed)"
                    logger.debug(f"OCR version check failed: {e}")
            
            return {
                "available": ocr_available,
                "version": version_info,
                "status": "✅ Working" if ocr_available else "❌ Unavailable"
            }
            
        except Exception as e:
            logger.error(f"Error checking OCR status: {e}")
            return {
                "available": False,
                "version": "Error",
                "status": "❌ Error checking OCR",
                "error": str(e)
            }

# Global bot controller instance
bot_controller = BotController()