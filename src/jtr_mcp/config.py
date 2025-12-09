"""Configuration for JTR MCP Server"""
from pathlib import Path
from typing import Dict
import os

# John the Ripper configuration
# Use full path in Docker, fallback to plain command for local
import shutil
JOHN_BINARY = shutil.which("john") or "/opt/john/john" if Path("/opt/john/john").exists() else "john"
UNSHADOW_BINARY = "unshadow"  # Works when built from source
UNIQUE_BINARY = "unique"

# Command syntax
JOHN_SYNTAX = "double-dash"  # Use --wordlist, --format, etc.

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
WORDLISTS_DIR = PROJECT_ROOT / "wordlists" / "common"
SESSIONS_DIR = PROJECT_ROOT / "sessions"
RESULTS_DIR = PROJECT_ROOT / "results"

# Temp directory - detect environment
# In Docker: use /app/temp (our working directory)
# With snap: use snap home directory
JOHN_SNAP_HOME = Path.home() / "snap" / "john-the-ripper" / "current"

if JOHN_SNAP_HOME.exists():
    # Running with snap installation
    TEMP_DIR = JOHN_SNAP_HOME
else:
    # Running in Docker or from source build
    TEMP_DIR = PROJECT_ROOT / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Log file for debugging
LOG_FILE = PROJECT_ROOT / "mcp_server.log"

# Create necessary directories
for directory in [SESSIONS_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
import logging
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("jtr-mcp")

logger.info(f"Config loaded - TEMP_DIR: {TEMP_DIR}")
logger.info(f"Config loaded - WORDLISTS_DIR: {WORDLISTS_DIR}")
logger.info(f"Config loaded - LOG_FILE: {LOG_FILE}")
logger.info(f"Config loaded - Environment: {'Docker/Source' if not JOHN_SNAP_HOME.exists() else 'Snap'}")

# Common Linux hash formats
HASH_FORMATS: Dict[str, str] = {
    "descrypt": "Traditional DES crypt",
    "md5crypt": "MD5-based crypt (older Linux/BSD)",
    "sha256crypt": "SHA-256 crypt",
    "sha512crypt": "SHA-512 crypt (modern Linux default)",
    "bcrypt": "bcrypt (OpenBSD, some Linux)",
}

# Default wordlists
DEFAULT_WORDLISTS = {
    "small": WORDLISTS_DIR / "test-small.txt",
    "medium": WORDLISTS_DIR / "10-million-password-list-top-10000.txt",
    "large": WORDLISTS_DIR / "rockyou.txt",
}
