"""
Quick connectivity test for the Discord bot
Tests connection without running the full bot
"""
import asyncio
import discord
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def test_bot_connection():
    """Test if the bot can connect to Discord"""
    
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
    
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in .env file")
        return False
    
    if not GUILD_ID:
        print("❌ GUILD_ID not found in .env file")
        return False
    
    print("🔍 Testing Discord bot connection...")
    print(f"Guild ID: {GUILD_ID}")
    
    # Configure intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    # Create client
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"✅ Bot connected successfully!")
        print(f"Bot name: {client.user.name}")
        print(f"Bot ID: {client.user.id}")
        
        # Try to find the guild
        guild = client.get_guild(GUILD_ID)
        if guild:
            print(f"✅ Found server: {guild.name}")
            print(f"Server member count: {guild.member_count}")
            
            # Check roles
            roles = [role.name for role in guild.roles if role.name != "@everyone"]
            print(f"Server roles: {roles}")
            
            # Check if bot has necessary permissions
            bot_member = guild.get_member(client.user.id)
            if bot_member:
                permissions = bot_member.guild_permissions
                print(f"Bot permissions:")
                print(f"  - Can send messages: {permissions.send_messages}")
                print(f"  - Can manage messages: {permissions.manage_messages}")
                print(f"  - Can kick members: {permissions.kick_members}")
                print(f"  - Can view channels: {permissions.view_channel}")
                print(f"  - Can embed links: {permissions.embed_links}")
        else:
            print(f"❌ Could not find server with ID {GUILD_ID}")
        
        # Disconnect after test
        await client.close()
    
    try:
        await client.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid bot token")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot_connection())