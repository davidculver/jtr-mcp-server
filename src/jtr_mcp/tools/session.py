"""Session management tool for MCP"""
from typing import Any, Dict
from pathlib import Path
from ..config import SESSIONS_DIR, logger
from ..utils.validators import sanitize_session_name


async def manage_session_tool(
    action: str,
    session_name: str = "default"
) -> Dict[str, Any]:
    """
    Manage John the Ripper cracking sessions
    
    Args:
        action: Action to perform (list, delete, info)
        session_name: Name of session (for delete/info actions)
    
    Returns:
        Dictionary with session information
    """
    try:
        logger.info("="*50)
        logger.info(f"Starting manage_session_tool - Action: {action}")
        logger.info(f"Session name: {session_name}")
        
        # Sanitize session name
        safe_session_name = sanitize_session_name(session_name)
        logger.info(f"Sanitized session name: {safe_session_name}")
        
        if action == "list":
            # List all sessions
            session_files = list(SESSIONS_DIR.glob("*.rec"))
            sessions = []
            
            for session_file in session_files:
                name = session_file.stem
                size = session_file.stat().st_size
                modified = session_file.stat().st_mtime
                
                sessions.append({
                    "name": name,
                    "size_bytes": size,
                    "file": str(session_file)
                })
            
            logger.info(f"Found {len(sessions)} sessions")
            
            return {
                "success": True,
                "action": "list",
                "sessions": sessions,
                "count": len(sessions)
            }
        
        elif action == "delete":
            # Delete a specific session
            session_file = SESSIONS_DIR / f"{safe_session_name}.rec"
            
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Deleted session: {session_file}")
                return {
                    "success": True,
                    "action": "delete",
                    "message": f"Session '{safe_session_name}' deleted successfully"
                }
            else:
                logger.warning(f"Session not found: {session_file}")
                return {
                    "success": False,
                    "action": "delete",
                    "error": f"Session '{safe_session_name}' not found"
                }
        
        elif action == "info":
            # Get info about a specific session
            session_file = SESSIONS_DIR / f"{safe_session_name}.rec"
            
            if session_file.exists():
                size = session_file.stat().st_size
                modified = session_file.stat().st_mtime
                
                import datetime
                mod_time = datetime.datetime.fromtimestamp(modified)
                
                return {
                    "success": True,
                    "action": "info",
                    "session_name": safe_session_name,
                    "size_bytes": size,
                    "last_modified": mod_time.isoformat(),
                    "file_path": str(session_file)
                }
            else:
                return {
                    "success": False,
                    "action": "info",
                    "error": f"Session '{safe_session_name}' not found"
                }
        
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}. Use 'list', 'delete', or 'info'"
            }
        
    except Exception as e:
        import traceback
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Exception in session management: {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }
