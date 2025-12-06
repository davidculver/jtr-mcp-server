"""Input validation utilities"""
from pathlib import Path
from typing import Optional, Tuple


def validate_file_exists(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate that a file exists and is readable"""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"File does not exist: {file_path}"
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"
        if not path.stat().st_size > 0:
            return False, f"File is empty: {file_path}"
        return True, None
    except Exception as e:
        return False, f"Error accessing file: {e}"


def validate_hash_format(format_name: str, supported_formats: list) -> Tuple[bool, Optional[str]]:
    """Validate that a hash format is supported"""
    if not format_name:
        return True, None  # Format is optional
    
    if format_name not in supported_formats:
        return False, f"Unsupported format: {format_name}. Use one of: {', '.join(supported_formats[:10])}..."
    
    return True, None


def sanitize_session_name(name: str) -> str:
    """Sanitize session name to prevent path traversal"""
    # Remove any path separators and special characters
    safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_'))
    return safe_name[:50]  # Limit length
