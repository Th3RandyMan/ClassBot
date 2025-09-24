"""
Test script to verify the new role logic works correctly
"""

class MockRole:
    def __init__(self, name):
        self.name = name

class MockMember:
    def __init__(self, role_names):
        self.roles = [MockRole(name) for name in role_names]

def test_role_logic():
    """Test the updated role checking logic"""
    
    # Simulate the bot's environment variables
    ALLOWED_ROLE_NAME = ""  # Empty means any role allowed
    ADMIN_ROLE_NAMES = ["Professor", "Teaching Assistant (TA)"]
    
    def has_allowed_role(member):
        """Check if member has any role (anyone with a role can post code)"""
        if not member.roles:
            return False
        
        # If ALLOWED_ROLE_NAME is empty/None, anyone with ANY role can post code
        if not ALLOWED_ROLE_NAME:
            # Check if user has any role other than @everyone
            user_roles = [role for role in member.roles if role.name != "@everyone"]
            return len(user_roles) > 0
        else:
            # Check for specific role
            return any(role.name == ALLOWED_ROLE_NAME for role in member.roles)
    
    def has_admin_role(member):
        """Check if member has any of the admin roles"""
        if not member.roles:
            return False
        
        member_role_names = [role.name for role in member.roles]
        return any(admin_role in member_role_names for admin_role in ADMIN_ROLE_NAMES)
    
    # Test cases
    test_cases = [
        # Member with no roles (only @everyone)
        (["@everyone"], False, False, "No roles (only @everyone)"),
        
        # Member with Professor role
        (["@everyone", "Professor"], True, True, "Professor role"),
        
        # Member with TA role
        (["@everyone", "Teaching Assistant (TA)"], True, True, "TA role"),
        
        # Member with Lab Assistant role (should be able to post code, not admin)
        (["@everyone", "Lab Assistant (LA)"], True, False, "Lab Assistant role"),
        
        # Member with Outside Help PLA role
        (["@everyone", "Outside Help (PLA)"], True, False, "Outside Help PLA role"),
        
        # Member with Outside Help PTA role
        (["@everyone", "Outside Help (PTA)"], True, False, "Outside Help PTA role"),
        
        # Member with multiple roles including admin
        (["@everyone", "Professor", "Lab Assistant (LA)"], True, True, "Multiple roles with Professor"),
        
        # Member with no roles at all
        ([], False, False, "No roles at all"),
    ]
    
    print("🧪 Testing Updated Role Logic")
    print("=" * 60)
    print("Current Configuration:")
    print(f"  - ALLOWED_ROLE_NAME: '{ALLOWED_ROLE_NAME}' (empty = any role)")
    print(f"  - ADMIN_ROLE_NAMES: {ADMIN_ROLE_NAMES}")
    print("=" * 60)
    
    for roles, expected_allowed, expected_admin, description in test_cases:
        member = MockMember(roles)
        
        can_post = has_allowed_role(member)
        is_admin = has_admin_role(member)
        
        status_allowed = "✅" if can_post == expected_allowed else "❌"
        status_admin = "✅" if is_admin == expected_admin else "❌"
        
        print(f"{description}:")
        print(f"  Roles: {[r for r in roles if r != '@everyone']}")
        print(f"  Can post code: {can_post} {status_allowed}")
        print(f"  Is admin: {is_admin} {status_admin}")
        print()

if __name__ == "__main__":
    test_role_logic()