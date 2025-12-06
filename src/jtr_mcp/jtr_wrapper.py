"""Wrapper for John the Ripper commands"""
import subprocess
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from .config import JOHN_BINARY, UNSHADOW_BINARY, SESSIONS_DIR, logger


class JohnTheRipperWrapper:
    """Wrapper for executing John the Ripper commands"""
    
    def __init__(self):
        self.john_binary = JOHN_BINARY
        self.unshadow_binary = UNSHADOW_BINARY
    
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
                # Parse the output - formats are comma-separated
                formats_text = result.stdout.strip()
                # Extract format names (they're comma-separated)
                formats = [f.strip() for f in formats_text.split(',')]
                # Clean up any that have descriptions in parentheses
                formats = [f.split('(')[0].strip() for f in formats]
                return [f for f in formats if f and not f.startswith('(')]
            else:
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
            
            # Determine success - john considers it successful if:
            # 1. Passwords were cracked in this run (contains "1g", "2g", etc.)
            # 2. Session completed normally
            # 3. No passwords left to crack (already cracked)
            # 4. Shows cracked passwords
            
            success = False
            
            # Check various success indicators
            if "password hash cracked" in output.lower():
                success = True
                logger.info("Success: Found 'password hash cracked' in output")
            elif "session completed" in output.lower():
                success = True
                logger.info("Success: Session completed")
            elif "no password hashes left to crack" in output.lower():
                success = True
                logger.info("Success: No hashes left to crack (already done)")
            elif re.search(r'\d+g ', output):  # Matches "1g ", "2g ", etc.
                success = True
                logger.info("Success: Found password crack indicator (Ng)")
            elif result.returncode == 0:
                # Return code 0 generally means success
                success = True
                logger.info("Success: Return code 0")
            
            return success, output
                
        except subprocess.TimeoutExpired:
            logger.error("Command timed out after 5 minutes")
            return False, "Command timed out after 5 minutes"
        except Exception as e:
            logger.error(f"Error running john: {e}")
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
            
            # Parse output - each line is username:password:...
            lines = output.split('\n')
            cracked = []
            
            for line in lines:
                # Skip summary lines like "1 password hash cracked, 0 left"
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
        Combine /etc/passwd and /etc/shadow files
        
        Returns: (success, message)
        """
        try:
            with open(output_file, 'w') as outfile:
                result = subprocess.run(
                    [self.unshadow_binary, passwd_file, shadow_file],
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0:
                return True, f"Combined file created: {output_file}"
            else:
                return False, f"Error: {result.stderr}"
                
        except Exception as e:
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
            
            # First line has version info
            first_line = result.stdout.split('\n')[0]
            return first_line
            
        except Exception as e:
            return f"Unknown (error: {e})"
