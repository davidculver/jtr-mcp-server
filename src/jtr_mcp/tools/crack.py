"""Crack passwords tool for MCP"""
from typing import Any, Dict
from pathlib import Path
from ..jtr_wrapper import JohnTheRipperWrapper
from ..config import DEFAULT_WORDLISTS, TEMP_DIR, logger
from ..utils.validators import validate_file_exists, validate_hash_format
import tempfile
import traceback


async def crack_passwords_tool(
    hash_file_content: str,
    wordlist: str = "small",
    hash_format: str = None,
    use_rules: bool = False
) -> Dict[str, Any]:
    """
    Crack passwords from a hash file
    
    Args:
        hash_file_content: Content of the hash file (john format)
        wordlist: Wordlist to use (small/medium/large or path to custom file)
        hash_format: Hash format (md5crypt, sha512crypt, etc.) - optional, john will auto-detect
        use_rules: Whether to use word mangling rules
    
    Returns:
        Dictionary with results
    """
    try:
        logger.info("="*50)
        logger.info("Starting crack_passwords_tool")
        logger.info(f"Hash content: {hash_file_content[:80]}...")
        logger.info(f"Wordlist: {wordlist}")
        logger.info(f"Format: {hash_format}")
        logger.info(f"Use rules: {use_rules}")
        
        jtr = JohnTheRipperWrapper()
        
        # Determine wordlist path
        if wordlist in DEFAULT_WORDLISTS:
            wordlist_path = str(DEFAULT_WORDLISTS[wordlist])
            logger.info(f"Using default wordlist: {wordlist_path}")
        else:
            wordlist_path = wordlist
            logger.info(f"Using custom wordlist: {wordlist_path}")
        
        # Validate wordlist exists
        valid, error = validate_file_exists(wordlist_path)
        if not valid:
            logger.error(f"Wordlist validation failed: {error}")
            return {
                "success": False,
                "error": f"Wordlist error: {error}",
                "cracked_passwords": []
            }
        
        logger.info("Wordlist validated successfully")
        
        # Validate hash format if provided
        if hash_format:
            formats = jtr.get_formats()
            logger.info(f"Got {len(formats)} formats from JTR")
            valid, error = validate_hash_format(hash_format, formats)
            if not valid:
                logger.error(f"Format validation failed: {error}")
                return {
                    "success": False,
                    "error": error,
                    "cracked_passwords": []
                }
            logger.info("Format validated successfully")
        
        # Create temporary hash file
        logger.info(f"Creating temp file in: {TEMP_DIR}")
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            dir=TEMP_DIR,
            delete=False
        ) as tmp_file:
            tmp_file.write(hash_file_content)
            hash_file_path = tmp_file.name
        
        logger.info(f"Temp file created: {hash_file_path}")
        
        # Run john
        logger.info("Running john...")
        success, output = jtr.crack_passwords(
            hash_file=hash_file_path,
            wordlist=wordlist_path,
            format_type=hash_format,
            rules=use_rules
        )
        
        logger.info(f"John completed. Success: {success}")
        logger.info(f"Output (first 500 chars): {output[:500]}")
        
        # Get cracked passwords
        logger.info("Getting cracked passwords...")
        show_success, cracked = jtr.show_cracked(
            hash_file=hash_file_path,
            format_type=hash_format
        )
        
        logger.info(f"Show cracked completed. Cracked count: {len(cracked)}")
        logger.info(f"Cracked passwords: {cracked}")
        
        # Clean up temp file
        Path(hash_file_path).unlink(missing_ok=True)
        logger.info("Temp file cleaned up")
        
        result = {
            "success": success,
            "cracked_count": len(cracked),
            "cracked_passwords": cracked,
            "output": output,
            "wordlist_used": wordlist,
            "format_used": hash_format or "auto-detect"
        }
        
        logger.info(f"Returning result: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Exception caught: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "cracked_passwords": []
        }
