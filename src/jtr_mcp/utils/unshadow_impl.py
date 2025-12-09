"""Python implementation of unshadow functionality"""
from typing import Tuple


def unshadow(passwd_content: str, shadow_content: str) -> Tuple[bool, str, str]:
    """
    Combine passwd and shadow files (Python implementation)
    
    Args:
        passwd_content: Content of /etc/passwd
        shadow_content: Content of /etc/shadow
        
    Returns:
        (success, combined_content, error_message)
    """
    try:
        # Parse passwd file
        passwd_lines = {}
        for line in passwd_content.strip().split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split(':')
            if len(parts) >= 7:
                username = parts[0]
                passwd_lines[username] = parts
        
        # Parse shadow file
        shadow_lines = {}
        for line in shadow_content.strip().split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split(':')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]
                shadow_lines[username] = password_hash
        
        # Combine them
        combined = []
        for username, passwd_parts in passwd_lines.items():
            if username in shadow_lines:
                # Replace the 'x' in passwd with actual hash from shadow
                passwd_parts[1] = shadow_lines[username]
                combined_line = ':'.join(passwd_parts)
                combined.append(combined_line)
        
        if not combined:
            return False, "", "No matching users found between passwd and shadow files"
        
        combined_content = '\n'.join(combined) + '\n'
        return True, combined_content, ""
        
    except Exception as e:
        return False, "", f"Error combining files: {e}"
