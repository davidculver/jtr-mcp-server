from typing import Any, Dict
from pathlib import Path
from ..config import logger
import glob
import datetime


async def check_status_tool() -> Dict[str, Any]:
    try:
        # FIXME: hardcoded snap path, should detect env
        pot_file_pattern = Path.home() / "snap" / "john-the-ripper" / "*" / ".john" / "john.pot"
        pot_files = glob.glob(str(pot_file_pattern))

        if not pot_files:
            return {
                "success": True,
                "cracked_count": 0,
                "pot_file": None,
                "message": "No passwords cracked yet"
            }

        pot_file = Path(pot_files[0])

        if not pot_file.exists():
            return {
                "success": True,
                "cracked_count": 0,
                "pot_file": str(pot_file),
                "message": "No passwords cracked yet"
            }

        with open(pot_file, 'r') as f:
            lines = f.readlines()

        cracked_entries = [
            line.strip()
            for line in lines
            if line.strip() and not line.startswith('#')
        ]

        size = pot_file.stat().st_size
        modified = pot_file.stat().st_mtime
        mod_time = datetime.datetime.fromtimestamp(modified)

        return {
            "success": True,
            "cracked_count": len(cracked_entries),
            "pot_file": str(pot_file),
            "pot_file_size": size,
            "last_updated": mod_time.isoformat(),
            "recent_cracks": cracked_entries[-5:] if cracked_entries else [],
            "message": f"Total cracked: {len(cracked_entries)} passwords"
        }

    except Exception as e:
        logger.error(f"status error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
