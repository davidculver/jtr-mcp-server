from typing import Any, Dict
from pathlib import Path
from ..jtr_wrapper import JohnTheRipperWrapper
from ..config import TEMP_DIR, logger
import tempfile


async def unshadow_files_tool(
    passwd_content: str,
    shadow_content: str
) -> Dict[str, Any]:
    try:
        jtr = JohnTheRipperWrapper()

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_passwd.txt',
            dir=TEMP_DIR,
            delete=False
        ) as passwd_file:
            passwd_file.write(passwd_content)
            passwd_path = passwd_file.name

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_shadow.txt',
            dir=TEMP_DIR,
            delete=False
        ) as shadow_file:
            shadow_file.write(shadow_content)
            shadow_path = shadow_file.name

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_combined.txt',
            dir=TEMP_DIR,
            delete=False
        ) as output_file:
            output_path = output_file.name

        success, message = jtr.unshadow(
            passwd_file=passwd_path,
            shadow_file=shadow_path,
            output_file=output_path
        )

        combined_content = ""
        if success:
            with open(output_path, 'r') as f:
                combined_content = f.read()

        for path in [passwd_path, shadow_path, output_path]:
            Path(path).unlink(missing_ok=True)

        if success:
            return {
                "success": True,
                "combined_content": combined_content,
                "line_count": len(combined_content.splitlines()),
                "message": "Files combined successfully"
            }
        else:
            return {
                "success": False,
                "error": message,
                "combined_content": ""
            }

    except Exception as e:
        logger.error(f"unshadow error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "combined_content": ""
        }
