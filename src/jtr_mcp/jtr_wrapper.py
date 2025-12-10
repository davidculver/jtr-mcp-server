"""Wrapper for John the Ripper commands"""
import subprocess
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from .config import JOHN_BINARY, SESSIONS_DIR, logger
from .utils.unshadow_impl import unshadow as unshadow_python


class JohnTheRipperWrapper:
    def __init__(self):
        self.john_binary = JOHN_BINARY
    
    def get_formats(self) -> List[str]:
        try:
            result = subprocess.run(
                [self.john_binary, "--list=formats"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout.strip()

                # comma-separated format
                if ',' in output:
                    formats = [f.strip() for f in output.split(',')]
                    formats = [f.split('(')[0].strip() for f in formats]
                    formats = [f for f in formats if f and not f.startswith('(')]
                    return formats

                # line by line
                lines = output.split('\n')
                formats = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if parts:
                            fmt = parts[0].strip()
                            if fmt:
                                formats.append(fmt)

                return formats
            else:
                logger.error(f"get_formats failed: rc={result.returncode}")
                return []
        except Exception as e:
            logger.error(f"get_formats error: {e}")
            return []
    
    def crack_passwords(
        self,
        hash_file: str,
        wordlist: str,
        format_type: Optional[str] = None,
        session_name: Optional[str] = None,
        rules: bool = False
    ) -> Tuple[bool, str]:
        cmd = [self.john_binary]
        cmd.append(f"--wordlist={wordlist}")
        cmd.append(hash_file)

        if format_type:
            cmd.append(f"--format={format_type}")

        if session_name:
            session_path = SESSIONS_DIR / f"{session_name}.rec"
            cmd.append(f"--session={session_path}")

        if rules:
            cmd.append("--rules")
        
        try:
            logger.debug(f"john cmd: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr
            logger.debug(f"john rc: {result.returncode}")

            # TODO: this detection logic is kinda hacky but works
            success = (
                "password hash cracked" in output.lower() or
                "session completed" in output.lower() or
                "no password hashes left to crack" in output.lower() or
                re.search(r'\d+g ', output) or
                result.returncode == 0
            )

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Timed out after 5 minutes"
        except Exception as e:
            logger.error(f"john error: {e}")
            return False, f"Error: {e}"
    
    def show_cracked(self, hash_file: str, format_type: Optional[str] = None) -> Tuple[bool, List[str]]:
        cmd = [self.john_binary, "--show", hash_file]

        if format_type:
            cmd.append(f"--format={format_type}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            output = result.stdout.strip()
            if not output:
                return True, []

            lines = output.split('\n')
            cracked = []

            for line in lines:
                if 'password' in line.lower() and 'cracked' in line.lower():
                    continue
                if line.strip() and ':' in line:
                    cracked.append(line.strip())

            return True, cracked

        except Exception as e:
            logger.error(f"show_cracked error: {e}")
            return False, []
    
    def unshadow(self, passwd_file: str, shadow_file: str, output_file: str) -> Tuple[bool, str]:
        # using python impl instead of john's unshadow binary
        try:
            with open(passwd_file, 'r') as f:
                passwd_content = f.read()

            with open(shadow_file, 'r') as f:
                shadow_content = f.read()

            success, combined_content, error_msg = unshadow_python(passwd_content, shadow_content)

            if success:
                with open(output_file, 'w') as f:
                    f.write(combined_content)
                return True, f"Combined file created: {output_file}"
            else:
                return False, f"Error: {error_msg}"

        except Exception as e:
            logger.error(f"unshadow error: {e}")
            return False, f"Error: {e}"
    
    def get_version(self) -> str:
        try:
            result = subprocess.run(
                [self.john_binary, "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.split('\n')[0]
        except Exception:
            return "Unknown"
