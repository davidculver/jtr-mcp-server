from typing import Any, Dict
from pathlib import Path
from ..config import SESSIONS_DIR, logger
from ..utils.validators import sanitize_session_name
import datetime


async def manage_session_tool(
    action: str,
    session_name: str = "default"
) -> Dict[str, Any]:
    try:
        safe_session_name = sanitize_session_name(session_name)

        if action == "list":
            session_files = list(SESSIONS_DIR.glob("*.rec"))
            sessions = []

            for session_file in session_files:
                sessions.append({
                    "name": session_file.stem,
                    "size_bytes": session_file.stat().st_size,
                    "file": str(session_file)
                })

            return {
                "success": True,
                "action": "list",
                "sessions": sessions,
                "count": len(sessions)
            }

        elif action == "delete":
            session_file = SESSIONS_DIR / f"{safe_session_name}.rec"

            if session_file.exists():
                session_file.unlink()
                return {
                    "success": True,
                    "action": "delete",
                    "message": f"Session '{safe_session_name}' deleted"
                }
            else:
                return {
                    "success": False,
                    "action": "delete",
                    "error": f"Session '{safe_session_name}' not found"
                }

        elif action == "info":
            session_file = SESSIONS_DIR / f"{safe_session_name}.rec"

            if session_file.exists():
                size = session_file.stat().st_size
                modified = session_file.stat().st_mtime
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
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        logger.error(f"session error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
