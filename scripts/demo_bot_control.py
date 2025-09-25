#!/usr/bin/env python3
"""
Demonstration of the bot control system
Shows how to manage bot state and operations
"""
import sys
import os

# Add src directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.bot_controller import BotController

def demonstrate_bot_control():
    """Comprehensive demonstration of the bot control system."""
    
    print("🤖 ClassBot Control System Demo")
    print("=" * 50)
    print()
    
    # Initialize controller
    controller = BotController()
    
    print("📊 Available Bot Control Commands:")
    print("-" * 40)
    print("  !bot_disable [minutes] [reason]     # Disable bot temporarily or indefinitely")
    print("  !bot_enable [reason]                # Re-enable the bot")
    print("  !bot_status                         # Check bot status")
    print("  !bot_maintenance [on/off/toggle]    # Toggle maintenance mode")
    print("  !bot_kill                           # Completely shutdown bot")
    print()
    
    print("💡 Usage Examples:")
    print("-" * 40)
    print("  !bot_disable                        # Disable indefinitely")
    print("  !bot_disable 30                     # Disable for 30 minutes") 
    print("  !bot_disable 60 Server maintenance  # Disable for 1 hour with reason")
    print("  !bot_enable                         # Re-enable bot")
    print("  !bot_maintenance on                 # Enable maintenance mode")
    print("  !bot_kill                           # Shutdown completely")
    print()
    
    # Demonstrate functionality
    print("🧪 Control System Test:")
    print("-" * 40)
    
    # Test 1: Check initial status
    print("1. Initial bot status:")
    status = controller.get_status()
    print(f"   Enabled: {status['enabled']}")
    print(f"   Maintenance Mode: {status['maintenance_mode']}")
    print()
    
    # Test 2: Disable bot temporarily
    print("2. Disabling bot for 5 minutes...")
    controller.disable_bot(duration=5, reason="Demo test", user="System Demo")
    status = controller.get_status()
    print(f"   Enabled: {status['enabled']}")
    print(f"   Reason: {status['disabled_reason']}")
    print(f"   Disabled By: {status['disabled_by']}")
    print(f"   Remaining Time: {status.get('remaining_minutes', 'N/A')} minutes")
    print()
    
    # Test 3: Check command availability when disabled
    print("3. Command availability when disabled:")
    test_commands = ["help_classbot", "remove_roleless", "bot_enable", "bot_status", "check_usernames"]
    for cmd in test_commands:
        can_execute = controller.can_execute_command(cmd)
        status_icon = "✅" if can_execute else "❌"
        print(f"   {status_icon} {cmd}")
    print()
    
    # Test 4: Re-enable bot
    print("4. Re-enabling bot...")
    controller.enable_bot(user="System Demo", reason="Demo completed")
    status = controller.get_status()
    print(f"   Enabled: {status['enabled']}")
    print(f"   All commands available: {'Yes' if status['enabled'] else 'No'}")
    print()
    
    # Test 5: Maintenance mode
    print("5. Testing maintenance mode...")
    controller.set_maintenance_mode(True, user="System Demo")
    status = controller.get_status()
    print(f"   Maintenance Mode: {status['maintenance_mode']}")
    print(f"   Bot Enabled: {status['enabled']}")
    
    controller.set_maintenance_mode(False, user="System Demo")
    status = controller.get_status()
    print(f"   After disabling maintenance:")
    print(f"   Maintenance Mode: {status['maintenance_mode']}")
    print(f"   Bot Enabled: {status['enabled']}")
    print()
    
    print("🔒 What Happens When Bot is Disabled:")
    print("-" * 40)
    print("  • Most commands return 'Bot Temporarily Disabled' message")
    print("  • Only essential admin commands work (!bot_enable, !bot_status, !bot_kill)")
    print("  • Code monitoring continues to work (safety first!)")
    print("  • New member username checking still functions")
    print("  • Admin notifications still sent")
    print()
    
    print("⚙️ Disable Modes:")
    print("-" * 40)
    print("  🕐 Temporary: Automatically re-enables after specified minutes")
    print("  ♾️  Indefinite: Requires manual !bot_enable command")
    print("  🔧 Maintenance: Special mode for updates/maintenance")
    print("  ☠️  Kill: Complete shutdown, requires manual script restart")
    print()
    
    print("👥 Permission Requirements:")
    print("-" * 40)
    print("  • All control commands require Admin/TA roles")
    print("  • Same permissions as other admin commands")
    print("  • Actions are logged with user attribution")
    print()
    
    print("📝 Use Cases:")
    print("-" * 40)
    print("  • Server maintenance windows")
    print("  • Testing new features safely")
    print("  • Temporarily reducing bot activity")
    print("  • Emergency shutdown if needed")
    print("  • Scheduled downtime for updates")
    print()
    
    print("✅ Bot Control System Ready!")
    print("   All commands are now available for bot management.")
    print("   The system maintains safety features even when disabled.")

if __name__ == "__main__":
    demonstrate_bot_control()