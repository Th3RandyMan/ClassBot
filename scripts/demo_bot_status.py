#!/usr/bin/env python3
"""
Demo showing exactly what bot_status command displays
"""
import sys
import os
from datetime import datetime, timedelta

# Add src directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.bot_controller import BotController

def demo_bot_status():
    """Show exactly what bot_status displays in different scenarios."""
    
    print("📊 Bot Status Command - What Users See")
    print("=" * 55)
    print()
    
    controller = BotController()
    
    # Scenario 1: Bot is enabled (normal operation)
    print("🟢 Scenario 1: Bot is ENABLED (Normal Operation)")
    print("-" * 50)
    controller.enable_bot("Demo User", "System test")
    status = controller.get_status()
    
    print("Discord Embed Content:")
    print("Title: 🟢 Bot Status: Online")
    print("Description: The bot is running normally")
    print("Color: Green (#00ff00)")
    print()
    print("Fields shown:")
    print("• All Commands: Available")
    print("• Monitoring: Active") 
    print("• Bot Version: ClassBot v2.0")
    print("• Uptime: Started 1 hour ago (example)")
    print()
    print()
    
    # Scenario 2: Bot disabled temporarily
    print("🔴 Scenario 2: Bot DISABLED Temporarily")
    print("-" * 50)
    controller.disable_bot(45, "Server maintenance", "Admin John")
    status = controller.get_status()
    
    print("Discord Embed Content:")
    print("Title: 🔴 Bot Status: Disabled")
    print("Color: Red (#ff0000)")
    print("Description: Bot is temporarily disabled")
    print()
    print("Fields shown:")
    print(f"• Reason: {status['disabled_reason']}")
    print(f"• Disabled By: {status['disabled_by']}")
    print(f"• Disabled At: [Discord timestamp of when disabled]")
    print(f"• Re-enabled In: {status.get('remaining_minutes', 0)} minutes")
    print(f"• Will Re-enable At: [Discord timestamp of auto-enable]")
    print("• Available Commands: !bot_status, !bot_enable, !bot_kill, !help_classbot")
    print("• Bot Version: ClassBot v2.0")
    print("• Uptime: Started 1 hour ago (example)")
    print()
    print()
    
    # Scenario 3: Bot disabled indefinitely 
    print("🔴 Scenario 3: Bot DISABLED Indefinitely")
    print("-" * 50)
    controller.disable_bot(None, "Emergency shutdown", "Admin Sarah")
    status = controller.get_status()
    
    print("Discord Embed Content:")
    print("Title: 🔴 Bot Status: Disabled") 
    print("Color: Red (#ff0000)")
    print("Description: Bot is temporarily disabled")
    print()
    print("Fields shown:")
    print(f"• Reason: {status['disabled_reason']}")
    print(f"• Disabled By: {status['disabled_by']}")
    print("• Disabled At: [Discord timestamp of when disabled]")
    print("• Status: Indefinitely disabled")
    print("• Available Commands: !bot_status, !bot_enable, !bot_kill, !help_classbot")
    print("• Bot Version: ClassBot v2.0")
    print("• Uptime: Started 1 hour ago (example)")
    print()
    print()
    
    # Scenario 4: Maintenance mode
    print("🔧 Scenario 4: Bot in MAINTENANCE MODE")
    print("-" * 50)
    controller.set_maintenance_mode(True, "Admin Mike")
    status = controller.get_status()
    
    print("Discord Embed Content:")
    print("Title: 🔴 Bot Status: Disabled")
    print("Color: Red (#ff0000)")  
    print("Description: Bot is in maintenance mode")
    print()
    print("Fields shown:")
    print(f"• Reason: {status['disabled_reason']}")
    print(f"• Disabled By: {status['disabled_by']}")
    print("• Disabled At: [Discord timestamp of when disabled]")
    print("• Status: Indefinitely disabled")
    print("• Available Commands: !bot_status, !bot_enable, !bot_kill, !help_classbot")
    print("• Bot Version: ClassBot v2.0")
    print("• Uptime: Started 1 hour ago (example)")
    print()
    print()
    
    # Reset to enabled state
    controller.enable_bot("Demo User", "Demo completed")
    
    print("💡 Key Features of !bot_status:")
    print("-" * 50)
    print("✅ Shows current enable/disable state with color coding")
    print("✅ Displays reason for any disable action")
    print("✅ Shows who disabled the bot and when")
    print("✅ For temporary disables: shows remaining time AND exact re-enable time")
    print("✅ Lists available commands when disabled")
    print("✅ Includes bot version and uptime info")
    print("✅ Uses Discord timestamps for proper timezone display")
    print("✅ Clear visual distinction between normal, disabled, and maintenance states")
    print()
    
    print("🎯 Perfect for:")
    print("-" * 50)
    print("• Checking if bot is working normally")
    print("• Seeing how much time left on temporary disables") 
    print("• Finding out why bot was disabled and by whom")
    print("• Getting list of commands that still work when disabled")
    print("• Troubleshooting bot issues")
    print()
    
    print("📱 Real Usage Examples:")
    print("-" * 50)
    print("Admin types: !bot_status")
    print()
    print("If bot is normal:")
    print("  → Green embed: 'Bot Status: Online' with full functionality")
    print()
    print("If bot disabled for 30 min by John for maintenance:")
    print("  → Red embed showing:")
    print("    • Reason: Server maintenance")
    print("    • Disabled By: John")
    print("    • Re-enabled In: 23 minutes")
    print("    • Exact re-enable time as Discord timestamp")
    print()
    print("If bot in maintenance mode:")
    print("  → Red embed with 'maintenance mode' description")

if __name__ == "__main__":
    demo_bot_status()