"""Wrapper for John the Ripper commands"""
import subprocess
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from .config import JOHN_BINARY, SESSIONS_DIR, logger
from .utils.unshadow_impl import unshadow as unshadow_python


class JohnTheRipperWrapper:
    """Wrapper for executing John the Ripper commands"""
    
    def __init__(self):
        self.john_binary = JOHN_BINARY
    
    def get_formats(self) -> List[str]:
        """Get list of supported hash formats"""
        try:
            result = subprocess.run(
                [self.john_binary, "--list=formats"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.debug(f"Formats output (first 500 chars): {output[:500]}")
                
                # Try comma-separated parsing first
                if ',' in output:
                    formats = [f.strip() for f in output.split(',')]
                    formats = [f.split('(')[0].strip() for f in formats]
                    formats = [f for f in formats if f and not f.startswith('(')]
                    return formats
                
                # Try line-by-line parsing
                lines = output.split('\n')
                formats = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract format name (first word)
                        parts = line.split()
                        if parts:
                            fmt = parts[0].strip()
                            if fmt:
                                formats.append(fmt)
                
                return formats
            else:
                logger.error(f"get_formats failed with return code: {result.returncode}")
                logger.error(f"stderr: {result.stderr}")
                return []
        except Exception as e:
            logger.error(f"Error getting formats: {e}")
            return []
    
    def crack_passwords(
        self,
        hash_file: str,
        wordlist: str,
        format_type: Optional[str] = None,
        session_name: Optional[str] = None,
        rules: bool = False
    ) -> Tuple[bool, str]:
        """
        Run john to crack passwords
        
        Returns: (success, output_message)
        """
        cmd = [self.john_binary]
        
        # Add wordlist
        cmd.append(f"--wordlist={wordlist}")
        
        # Add hash file
        cmd.append(hash_file)
        
        # Add format if specified
        if format_type:
            cmd.append(f"--format={format_type}")
        
        # Add session name if specified
        if session_name:
            session_path = SESSIONS_DIR / f"{session_name}.rec"
            cmd.append(f"--session={session_path}")
        
        # Add rules if requested
        if rules:
            cmd.append("--rules")
        
        try:
            logger.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout + result.stderr
            logger.info(f"John returncode: {result.returncode}")
            logger.debug(f"Full output: {output}")
            
            # Determine success
            success = False
            
            if "password hash cracked" in output.lower():
                success = True
                logger.info("Success: Found 'password hash cracked' in output")
            elif "session completed" in output.lower():
                success = True
                logger.info("Success: Session completed")
            elif "no password hashes left to crack" in output.lower():
                success = True
                logger.info("Success: No hashes left to crack (already done)")
            elif re.search(r'\d+g ', output):
                success = True
                logger.info("Success: Found password crack indicator (Ng)")
            elif result.returncode == 0:
                success = True
                logger.info("Success: Return code 0")
            
            return success, output
                
        except subprocess.TimeoutExpired:
            logger.error("Command timed out after 5 minutes")
            return False, "Command timed out after 5 minutes"
        except Exception as e:
            logger.error(f"Error running john: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, f"Error running john: {e}"
    
    def show_cracked(self, hash_file: str, format_type: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Show cracked passwords from a hash file
        
        Returns: (success, list of cracked password entries)
        """
        cmd = [self.john_binary, "--show", hash_file]
        
        if format_type:
            cmd.append(f"--format={format_type}")
        
        try:
            logger.info(f"Executing show command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout.strip()
            logger.debug(f"Show output: {output}")
            
            if not output:
                return True, []
            
            # Parse output
            lines = output.split('\n')
            cracked = []
            
            for line in lines:
                if 'password' in line.lower() and 'cracked' in line.lower():
                    continue
                if line.strip() and ':' in line:
                    cracked.append(line.strip())
            
            return True, cracked
            
        except Exception as e:
            logger.error(f"Error showing cracked passwords: {e}")
            return False, []
    
    def unshadow(self, passwd_file: str, shadow_file: str, output_file: str) -> Tuple[bool, str]:
        """
        Combine /etc/passwd and /etc/shadow files (using Python implementation)
        
        Returns: (success, message)
        """
        try:
            logger.info("Using Python unshadow implementation")
            
            # Read input files
            with open(passwd_file, 'r') as f:
                passwd_content = f.read()
            
            with open(shadow_file, 'r') as f:
                shadow_content = f.read()
            
            # Combine using Python implementation
            success, combined_content, error_msg = unshadow_python(passwd_content, shadow_content)
            
            if success:
                # Write output file
                with open(output_file, 'w') as f:
                    f.write(combined_content)
                
                logger.info(f"Combined file created: {output_file}")
                return True, f"Combined file created: {output_file}"
            else:
                logger.error(f"Unshadow failed: {error_msg}")
                return False, f"Error: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error in unshadow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, f"Error running unshadow: {e}"
    
    def get_version(self) -> str:
        """Get John the Ripper version"""
        try:
            result = subprocess.run(
                [self.john_binary, "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            first_line = result.stdout.split('\n')[0]
            return first_line
            
        except Exception as e:
            return f"Unknown (error: {e})"
