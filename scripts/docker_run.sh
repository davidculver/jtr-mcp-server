#!/bin/bash
# Run JTR MCP Server in Docker (STDIO mode)

set -e

IMAGE_NAME="jtr-mcp-server"
IMAGE_TAG="latest"

echo "🚀 Starting JTR MCP Server in Docker (STDIO mode)"
echo "Press Ctrl+C to stop"
echo ""

# Run in interactive mode with STDIO
docker run -i \
    --rm \
    --name jtr-mcp-server \
    ${IMAGE_NAME}:${IMAGE_TAG}
