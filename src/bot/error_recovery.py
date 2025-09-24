"""
Enhanced Error Recovery System for Discord Bot
Handles automatic reconnection and error recovery for cloud deployment
"""

import asyncio
import logging
import discord

logger = logging.getLogger(__name__)


class ErrorRecoverySystem:
    """Handles automatic reconnection and error recovery"""
    
    def __init__(self, bot, warning_system):
        self.bot = bot
        self.warning_system = warning_system
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # seconds
        self.is_recovering = False
        
    async def handle_connection_error(self, error):
        """Handle connection-related errors with automatic recovery"""
        if self.is_recovering:
            return  # Already handling recovery
            
        self.is_recovering = True
        logger.error(f"Connection error occurred: {error}")
        
        while self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * self.reconnect_attempts  # Exponential backoff
            
            logger.info(f"Attempting reconnect #{self.reconnect_attempts} in {delay} seconds...")
            await asyncio.sleep(delay)
            
            try:
                # Save warnings before potential restart
                self.warning_system.save_warnings()
                logger.info("Saved warnings before reconnection attempt")
                
                # The bot will automatically try to reconnect
                self.is_recovering = False
                self.reconnect_attempts = 0
                logger.info("Successfully recovered from connection error")
                return
                
            except Exception as e:
                logger.error(f"Reconnection attempt #{self.reconnect_attempts} failed: {e}")
                
        # Max attempts reached
        logger.critical(f"Failed to reconnect after {self.max_reconnect_attempts} attempts")
        self.is_recovering = False
    
    def reset_reconnect_counter(self):
        """Reset reconnection attempts counter on successful connection"""
        self.reconnect_attempts = 0


async def run_bot_with_recovery(bot, token, warning_system):
    """Run bot with enhanced error recovery and automatic restart"""
    max_restarts = 5
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            logger.info(f"Starting bot (attempt {restart_count + 1}/{max_restarts})")
            
            # Ensure warnings are saved before starting
            warning_system.save_warnings()
            
            await bot.start(token)
            
        except discord.LoginFailure:
            logger.critical("Invalid Discord token - cannot start bot")
            break
        except discord.ConnectionClosed:
            logger.error("Discord connection closed - attempting restart")
        except discord.HTTPException as e:
            logger.error(f"Discord HTTP error: {e} - attempting restart")
        except Exception as e:
            logger.error(f"Unexpected error: {e} - attempting restart", exc_info=True)
        
        # Save warnings before restart
        try:
            warning_system.save_warnings()
            logger.info("Saved warnings before restart")
        except Exception as e:
            logger.error(f"Failed to save warnings before restart: {e}")
        
        restart_count += 1
        if restart_count < max_restarts:
            delay = min(30, 5 * restart_count)  # Exponential backoff, max 30 seconds
            logger.info(f"Restarting in {delay} seconds... (attempt {restart_count + 1}/{max_restarts})")
            await asyncio.sleep(delay)
        else:
            logger.critical(f"Maximum restart attempts ({max_restarts}) reached - stopping bot")