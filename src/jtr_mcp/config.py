from pathlib import Path
from typing import Dict
import shutil
import logging

# full path needed for docker to avoid "Cannot find John home" error
JOHN_BINARY = shutil.which("john") or "/opt/john/john" if Path("/opt/john/john").exists() else "john"
UNSHADOW_BINARY = "unshadow"
UNIQUE_BINARY = "unique"

PROJECT_ROOT = Path(__file__).parent.parent.parent
WORDLISTS_DIR = PROJECT_ROOT / "wordlists" / "common"
SESSIONS_DIR = PROJECT_ROOT / "sessions"
RESULTS_DIR = PROJECT_ROOT / "results"

# detect environment for temp dir
JOHN_SNAP_HOME = Path.home() / "snap" / "john-the-ripper" / "current"

if JOHN_SNAP_HOME.exists():
    TEMP_DIR = JOHN_SNAP_HOME
else:
    TEMP_DIR = PROJECT_ROOT / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = PROJECT_ROOT / "mcp_server.log"

for directory in [SESSIONS_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("jtr-mcp")

env = "snap" if JOHN_SNAP_HOME.exists() else "docker"
logger.debug(f"config: env={env}, temp={TEMP_DIR}")

HASH_FORMATS: Dict[str, str] = {
    "descrypt": "Traditional DES crypt",
    "md5crypt": "MD5-based crypt",
    "sha256crypt": "SHA-256 crypt",
    "sha512crypt": "SHA-512 crypt",
    "bcrypt": "bcrypt",
}

DEFAULT_WORDLISTS = {
    "small": WORDLISTS_DIR / "test-small.txt",
    "medium": WORDLISTS_DIR / "10-million-password-list-top-10000.txt",
    "large": WORDLISTS_DIR / "rockyou.txt",
}
