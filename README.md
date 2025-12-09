# JTR MCP Server

Model Context Protocol (MCP) server for John the Ripper password cracking tool.

## Features

- 🔓 **Password Cracking** - Dictionary attacks with 381+ hash formats
- 🔗 **Unshadow Support** - Combine /etc/passwd and /etc/shadow files
- 📊 **Session Management** - Save and restore cracking sessions
- 📈 **Status Monitoring** - Track cracking progress
- 🐳 **Docker Ready** - Containerized deployment
- 🔌 **MCP Compatible** - Works with Claude Desktop and other MCP clients

## Quick Start

### Using Docker (Recommended)
```bash
# Build the image
./scripts/docker_build.sh

# Run the server
./scripts/docker_run.sh

# Test the container
./scripts/docker_test.sh
```

### Local Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install John the Ripper (Ubuntu/Debian)
sudo snap install john-the-ripper

# Run the server
python -m src.jtr_mcp.server
```

## Available Tools

1. **crack_passwords** - Crack password hashes using dictionary attacks
2. **unshadow_files** - Combine passwd and shadow files
3. **manage_session** - List, delete, or get info on cracking sessions
4. **check_status** - View cracking statistics and recent cracks
5. **list_hash_formats** - Show all 381 supported hash formats
6. **get_jtr_info** - Get John the Ripper version and configuration

## Docker Usage

### STDIO Mode (Current)
```bash
# Interactive mode
docker run -i jtr-mcp-server:latest

# With MCP Inspector
npx @modelcontextprotocol/inspector docker run -i jtr-mcp-server:latest
```

### HTTP/SSE Mode (TODO)

Coming soon! See [TODO.md](TODO.md) for implementation plan.

## Development

### Running Tests
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src/jtr_mcp
```

### Using MCP Inspector
```bash
# Start inspector
npx @modelcontextprotocol/inspector bash ./scripts/run_server.sh

# Opens browser at http://localhost:6274
```

## Supported Hash Formats

- **Linux:** descrypt, md5crypt, sha256crypt, sha512crypt, bcrypt
- **Windows:** NTLM, NetNTLMv2
- **Databases:** MySQL, PostgreSQL, Oracle
- **Applications:** WordPress, Drupal, Django
- **And 370+ more formats**

## Wordlists Included

- `small` - 17 common passwords (testing)
- `medium` - 10,000 passwords
- `large` - rockyou.txt (14M passwords)

## License

MIT License - See [LICENSE](LICENSE) for details

## Security Notice

⚠️ **For Authorized Use Only**

This tool is intended for:
- Authorized penetration testing
- Security research
- Password strength auditing with permission

Unauthorized access to computer systems is illegal.

## Contributing

Contributions welcome! See [TODO.md](TODO.md) for planned features.

## Support

- Report issues on GitHub
- Check documentation in `docs/`
- Review examples in `examples/`
