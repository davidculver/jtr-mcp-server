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
    try:
        logger.debug(f"crack: wordlist={wordlist}, format={hash_format}, rules={use_rules}")
        
        jtr = JohnTheRipperWrapper()

        if wordlist in DEFAULT_WORDLISTS:
            wordlist_path = str(DEFAULT_WORDLISTS[wordlist])
        else:
            wordlist_path = wordlist

        valid, error = validate_file_exists(wordlist_path)
        if not valid:
            return {
                "success": False,
                "error": f"Wordlist error: {error}",
                "cracked_passwords": []
            }

        if hash_format:
            formats = jtr.get_formats()
            valid, error = validate_hash_format(hash_format, formats)
            if not valid:
                return {
                    "success": False,
                    "error": error,
                    "cracked_passwords": []
                }
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            dir=TEMP_DIR,
            delete=False
        ) as tmp_file:
            tmp_file.write(hash_file_content)
            hash_file_path = tmp_file.name

        success, output = jtr.crack_passwords(
            hash_file=hash_file_path,
            wordlist=wordlist_path,
            format_type=hash_format,
            rules=use_rules
        )

        show_success, cracked = jtr.show_cracked(
            hash_file=hash_file_path,
            format_type=hash_format
        )

        Path(hash_file_path).unlink(missing_ok=True)

        return {
            "success": success,
            "cracked_count": len(cracked),
            "cracked_passwords": cracked,
            "output": output,
            "wordlist_used": wordlist,
            "format_used": hash_format or "auto-detect"
        }

    except Exception as e:
        logger.error(f"crack error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "cracked_passwords": []
        }
