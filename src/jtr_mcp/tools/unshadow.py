"""Unshadow tool - Combine passwd and shadow files for MCP"""
from typing import Any, Dict
from pathlib import Path
from ..jtr_wrapper import JohnTheRipperWrapper
from ..config import TEMP_DIR, logger
import tempfile


async def unshadow_files_tool(
    passwd_content: str,
    shadow_content: str
) -> Dict[str, Any]:
    """
    Combine /etc/passwd and /etc/shadow files for use with John the Ripper
    
    Args:
        passwd_content: Content of /etc/passwd file
        shadow_content: Content of /etc/shadow file
    
    Returns:
        Dictionary with combined file content
    """
    try:
        logger.info("="*50)
        logger.info("Starting unshadow_files_tool")
        logger.info(f"Passwd lines: {len(passwd_content.splitlines())}")
        logger.info(f"Shadow lines: {len(shadow_content.splitlines())}")
        
        jtr = JohnTheRipperWrapper()
        
        # Create temporary files for passwd and shadow
        logger.info(f"Creating temp files in: {TEMP_DIR}")
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_passwd.txt',
            dir=TEMP_DIR,
            delete=False
        ) as passwd_file:
            passwd_file.write(passwd_content)
            passwd_path = passwd_file.name
        
        logger.info(f"Passwd temp file: {passwd_path}")
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_shadow.txt',
            dir=TEMP_DIR,
            delete=False
        ) as shadow_file:
            shadow_file.write(shadow_content)
            shadow_path = shadow_file.name
        
        logger.info(f"Shadow temp file: {shadow_path}")
        
        # Create output file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_combined.txt',
            dir=TEMP_DIR,
            delete=False
        ) as output_file:
            output_path = output_file.name
        
        logger.info(f"Output temp file: {output_path}")
        
        # Run unshadow
        logger.info("Running unshadow...")
        success, message = jtr.unshadow(
            passwd_file=passwd_path,
            shadow_file=shadow_path,
            output_file=output_path
        )
        
        logger.info(f"Unshadow completed. Success: {success}")
        logger.info(f"Message: {message}")
        
        # Read the combined file
        combined_content = ""
        if success:
            with open(output_path, 'r') as f:
                combined_content = f.read()
            logger.info(f"Combined file has {len(combined_content.splitlines())} lines")
        
        # Clean up temp files
        for path in [passwd_path, shadow_path, output_path]:
            Path(path).unlink(missing_ok=True)
        
        logger.info("Temp files cleaned up")
        
        if success:
            return {
                "success": True,
                "combined_content": combined_content,
                "line_count": len(combined_content.splitlines()),
                "message": "Files combined successfully. Use this output with crack_passwords tool."
            }
        else:
            return {
                "success": False,
                "error": message,
                "combined_content": ""
            }
        
    except Exception as e:
        import traceback
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Exception in unshadow: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "combined_content": ""
        }
