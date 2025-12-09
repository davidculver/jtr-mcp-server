# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JTR MCP Server is a Model Context Protocol (MCP) server that exposes John the Ripper password cracking functionality to MCP clients like Claude Desktop. The server runs in STDIO mode and provides 6 MCP tools for password cracking operations.

**Current Status:** ✅ Fully functional with Docker deployment
- Docker image built and tested (1.03GB)
- All 6 MCP tools working
- MCP Inspector integration verified
- Successfully cracking passwords in containerized environment

## Architecture

### Core Components

1. **server.py** - MCP server entry point
   - Registers 6 MCP tools using `@app.list_tools()` and `@app.call_tool()` decorators
   - Runs as STDIO server via `mcp.server.stdio.stdio_server()`
   - Tools: crack_passwords, unshadow_files, manage_session, check_status, list_hash_formats, get_jtr_info

2. **jtr_wrapper.py** - John the Ripper command wrapper
   - Wraps `john`, `unshadow` commands via subprocess
   - Key methods: `crack_passwords()`, `show_cracked()`, `unshadow()`, `get_formats()`, `get_version()`
   - Uses Python unshadow implementation from `utils/unshadow_impl.py` (not john's binary)

3. **config.py** - Global configuration
   - Paths: `TEMP_DIR`, `SESSIONS_DIR`, `RESULTS_DIR`, `WORDLISTS_DIR`
   - Auto-detects environment (Docker vs snap) for temp directory location
   - Configures logging to `mcp_server.log` in project root
   - `DEFAULT_WORDLISTS`: small, medium, large
   - **CRITICAL:** `JOHN_BINARY` uses full path `/opt/john/john` in Docker (uses `shutil.which()` or checks `/opt/john/john` existence) to avoid "Cannot find John home" error

4. **tools/** - Individual tool implementations
   - `crack.py`: crack_passwords_tool() - main cracking logic with validation
   - `unshadow.py`: unshadow_files_tool() - combines passwd/shadow files
   - `session.py`: manage_session_tool() - list/delete/info on .rec session files
   - `status.py`: check_status_tool() - reads john.pot file for cracked passwords

5. **utils/** - Utilities
   - `validators.py`: validate_file_exists(), validate_hash_format()
   - `unshadow_impl.py`: Pure Python unshadow implementation

### Data Flow

1. MCP client calls tool via STDIO → server.py `call_tool()`
2. Tool implementation in `tools/` validates inputs and creates temp files in `TEMP_DIR`
3. `jtr_wrapper.py` executes john subprocess with appropriate flags
4. Results parsed from john output and `--show` command
5. Temp files cleaned up, results returned to MCP client

### Environment Detection

The server auto-detects its environment (snap vs Docker) based on presence of `~/snap/john-the-ripper/current/`. This affects where temp files are stored due to snap's confinement restrictions.

## Development Commands

### Running the Server

```bash
# Local (requires John the Ripper installed)
python -m src.jtr_mcp.server

# Docker (recommended)
./scripts/docker_build.sh
./scripts/docker_run.sh

# With MCP Inspector for debugging
npx @modelcontextprotocol/inspector bash ./scripts/run_server.sh
```

### Testing

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src/jtr_mcp

# Run specific test file
pytest tests/unit/test_specific.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

### Docker Development

```bash
# Build image (takes 5-10 min first time, then uses cache)
./scripts/docker_build.sh

# Run container (STDIO mode)
./scripts/docker_run.sh

# Test container standalone
./scripts/docker_test.sh

# Test with MCP Inspector (opens browser at localhost:6274)
./scripts/docker_inspect.sh

# Interactive mode
docker run -i jtr-mcp-server:latest

# Check container logs (replace CONTAINER_ID)
docker logs <CONTAINER_ID>

# Access container logs file
docker exec <CONTAINER_ID> cat /app/mcp_server.log
```

**Current Docker Image:** `jtr-mcp-server:latest` (1.03GB)
- Based on Ubuntu 24.04
- John the Ripper built from source (bleeding-jumbo branch)
- Installed to `/opt/john/` with full runtime environment
- Python 3.12 with all MCP dependencies
- Wordlists included in `/app/wordlists/common/`

## Docker Architecture

### Dockerfile Structure

The Dockerfile (`/Dockerfile`) performs these steps:

1. **Base Image:** Ubuntu 24.04
2. **Build Dependencies:** Installs compilers, libraries (libssl, zlib, gmp, pcap, nss, krb5)
3. **Build John:** Clones from GitHub, compiles with `./configure && make`, installs to `/opt/john/`
4. **Python Setup:** Creates venv at `/app/venv`, installs requirements
5. **Application:** Copies `src/`, `wordlists/`, `scripts/` to `/app/`
6. **Entry Point:** Runs Python MCP server via venv

### Key Docker Paths

- John binary: `/opt/john/john` (MUST use full path)
- John runtime files: `/opt/john/*` (john.conf, rules, etc.)
- Application root: `/app/`
- Python venv: `/app/venv/`
- Wordlists: `/app/wordlists/common/`
- Temp files: `/app/temp/`
- Sessions: `/app/sessions/`
- Logs: `/app/mcp_server.log`

### Testing with MCP Inspector

MCP Inspector provides a web UI for testing the MCP server:

1. Run `./scripts/docker_inspect.sh`
2. Opens browser at http://localhost:6274
3. Proxy server runs on port 6277
4. Inspector auto-connects to Docker container via STDIO
5. Test tools interactively in browser

**Common Issues:**
- Port 6277 in use: Kill with `lsof -ti:6277 | xargs kill -9`
- Container not connecting: Check `tail -f /tmp/mcp-inspector.log`
- Tools failing: Check container logs with `docker logs <CONTAINER_ID>`

## Important Implementation Details

### Temporary Files

- Hash files are created as temp files in `TEMP_DIR` during cracking operations
- Temp files MUST be cleaned up after use (see `crack.py:109`)
- Environment-dependent: snap uses `~/snap/john-the-ripper/current/`, Docker uses `/app/temp`

### Logging

- All operations are logged to `mcp_server.log` at DEBUG level
- Use `logger.info()` for major operations, `logger.debug()` for details
- Check logs when debugging tool execution

### Hash Format Detection

- John auto-detects formats by default (format_type can be None)
- If format specified, validate against `jtr.get_formats()` output
- Common formats: md5crypt, sha256crypt, sha512crypt, bcrypt, descrypt

### Session Management

- Sessions stored as `.rec` files in `SESSIONS_DIR`
- Session names become filenames: "mysession" → "mysession.rec"
- Sessions allow resuming long-running cracks

### Wordlists

- Three built-in: small (17 words), medium (10k), large (rockyou, 14M)
- Located in `wordlists/common/`
- Custom wordlists accepted as file paths (must exist and be validated)

### Unshadow Implementation

- Uses **Python implementation** in `utils/unshadow_impl.py`, not john's binary
- Reason: Better compatibility across snap/Docker environments
- Combines /etc/passwd and /etc/shadow into john format

## MCP Protocol Notes

- Server uses STDIO transport (stdin/stdout communication)
- All tool results return `list[TextContent]` with formatted markdown
- Tool schemas defined inline in `list_tools()` handler
- Emojis used in responses (✅ ❌ 📊 🔓 etc.) for better UX

## Common Patterns

### Adding a New Tool

1. Create tool implementation in `src/jtr_mcp/tools/new_tool.py`
2. Implement async function returning `Dict[str, Any]`
3. Add tool to `list_tools()` in `server.py` with proper schema
4. Add handler case in `call_tool()` in `server.py`
5. Import tool at top of `server.py`

### Error Handling

All tool functions return dict with `"success": bool` key. On error:
```python
return {
    "success": False,
    "error": "Error message here",
    # ... other fields with safe defaults
}
```

### Subprocess Execution Pattern

```python
result = subprocess.run(
    [self.john_binary, ...args],
    capture_output=True,
    text=True,
    timeout=300  # Always set timeout
)
```

## Known Issues and Solutions

### Issue: "Cannot find John home"

**Symptom:** John the Ripper returns error "Cannot find John home. Invoke the program via full or relative pathname."

**Root Cause:** When John is invoked as just `john`, it can't locate its runtime files (configuration, rules, etc.) even if it's in PATH.

**Solution:** Use full path to John binary. In `config.py`:
```python
import shutil
JOHN_BINARY = shutil.which("john") or "/opt/john/john" if Path("/opt/john/john").exists() else "john"
```

This checks for john in PATH first, then falls back to Docker path `/opt/john/john`.

**Verification:** Check the first few lines of logs in container:
```bash
docker exec <CONTAINER_ID> head -20 /app/mcp_server.log
```
Should NOT see "Cannot find John home" errors.

### Issue: MCP Inspector won't connect

**Symptoms:**
- Browser loads but shows "Connecting..." forever
- No tools appear in UI
- Port 6277 "in use" error

**Solutions:**
```bash
# Kill existing inspector instances
pkill -f "mcp-inspector"

# Clean up ports
lsof -ti:6277 | xargs -r kill -9
lsof -ti:6274 | xargs -r kill -9

# Wait and restart
sleep 3
./scripts/docker_inspect.sh
```

### Issue: Docker build fails

**Common Causes:**
- Network timeout downloading packages
- Insufficient disk space (needs ~2GB)
- Previous build artifacts cached

**Solutions:**
```bash
# Clean build with no cache
docker build --no-cache -t jtr-mcp-server:latest .

# Prune unused images
docker image prune -f

# Check disk space
df -h
```

## Development Workflow

### Making Code Changes

1. Edit Python files in `src/jtr_mcp/`
2. Rebuild Docker image: `./scripts/docker_build.sh` (fast with cache)
3. Restart MCP Inspector: `pkill -f mcp-inspector && ./scripts/docker_inspect.sh`
4. Test in browser at http://localhost:6274
5. Check logs: `docker logs $(docker ps -q -l)` or `tail -f /tmp/mcp-inspector.log`

### Debugging Tips

- **Server logs:** `docker exec <CONTAINER_ID> tail -f /app/mcp_server.log`
- **Inspector logs:** `tail -f /tmp/mcp-inspector.log`
- **Container shell:** `docker exec -it <CONTAINER_ID> bash`
- **Test John directly:** `docker exec <CONTAINER_ID> /opt/john/john --test`
- **Check wordlists:** `docker exec <CONTAINER_ID> ls -lh /app/wordlists/common/`

### Successful Test Example

When crack_passwords works correctly, you'll see:
```
✅ Password cracking completed!

Cracked 1 password(s)
Wordlist: small
Format: md5crypt

Cracked passwords:
  testuser:testpassword
```

In logs:
```
INFO - Executing command: john --wordlist=/app/wordlists/common/test-small.txt /app/temp/tmpXXX.txt
INFO - John returncode: 0
INFO - Cracked count: 1
```
