# JTR MCP Server

MCP server that wraps John the Ripper for password cracking.

## Features

- Password cracking with 381+ hash formats
- Combine passwd/shadow files (unshadow)
- Session management for long-running cracks
- Status monitoring
- Docker deployment
- Works with Claude Desktop and other MCP clients

## Quick Start

### Docker
```bash
./scripts/docker_build.sh
./scripts/docker_run.sh
./scripts/docker_test.sh
```

### Local
```bash
pip install -r requirements.txt
sudo snap install john-the-ripper
python -m src.jtr_mcp.server
```

## Tools

1. crack_passwords - crack hashes with wordlists
2. unshadow_files - combine passwd/shadow files
3. manage_session - list/delete/info sessions
4. check_status - view cracked passwords
5. list_hash_formats - show supported formats
6. get_jtr_info - john version and config

## Usage

### STDIO mode
```bash
docker run -i jtr-mcp-server:latest
```

### With MCP Inspector
```bash
npx @modelcontextprotocol/inspector docker run -i jtr-mcp-server:latest
# opens at http://localhost:6274
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
pytest --cov=src/jtr_mcp
```

MCP Inspector:
```bash
npx @modelcontextprotocol/inspector bash ./scripts/run_server.sh
```

## Hash Formats

Supports 381+ formats including:
- Linux: descrypt, md5crypt, sha256crypt, sha512crypt, bcrypt
- Windows: NTLM, NetNTLMv2
- Databases: MySQL, PostgreSQL, Oracle
- Apps: WordPress, Drupal, Django

## Wordlists

- small - 17 passwords (for testing)
- medium - 10k passwords
- large - rockyou.txt (14M)

## License

MIT

## Security Notice

For authorized use only. Intended for pentesting, security research, and password auditing with permission. Unauthorized access is illegal.

## Contributing

PRs welcome
