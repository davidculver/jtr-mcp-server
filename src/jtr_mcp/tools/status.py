"""Status checking tool for MCP"""
from typing import Any, Dict
from pathlib import Path
from ..config import logger
import subprocess


async def check_status_tool() -> Dict[str, Any]:
    """
    Check John the Ripper status - shows cracked passwords count
    
    Returns:
        Dictionary with status information
    """
    try:
        logger.info("="*50)
        logger.info("Starting check_status_tool")
        
        # Find john.pot file in snap home
        pot_file_pattern = Path.home() / "snap" / "john-the-ripper" / "*" / ".john" / "john.pot"
        
        # Use glob to find the actual pot file
        import glob
        pot_files = glob.glob(str(pot_file_pattern))
        
        if not pot_files:
            logger.info("No pot file found")
            return {
                "success": True,
                "cracked_count": 0,
                "pot_file": None,
                "message": "No passwords cracked yet"
            }
        
        # Use the first (and usually only) pot file
        pot_file = Path(pot_files[0])
        logger.info(f"Pot file: {pot_file}")
        
        if not pot_file.exists():
            return {
                "success": True,
                "cracked_count": 0,
                "pot_file": str(pot_file),
                "message": "No passwords cracked yet"
            }
        
        # Read pot file and count entries
        with open(pot_file, 'r') as f:
            lines = f.readlines()
        
        # Filter out comments and empty lines
        cracked_entries = [
            line.strip() 
            for line in lines 
            if line.strip() and not line.startswith('#')
        ]
        
        logger.info(f"Found {len(cracked_entries)} cracked passwords")
        
        # Get file size and modification time
        size = pot_file.stat().st_size
        modified = pot_file.stat().st_mtime
        
        import datetime
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
        import traceback
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Exception in check_status: {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }
