#!/bin/bash
# Run JTR MCP Server in Docker with MCP Inspector

set -e

IMAGE_NAME="jtr-mcp-server"
IMAGE_TAG="latest"

echo "🔍 Starting MCP Inspector with Docker container"
echo ""
echo "This will:"
echo "  1. Start the MCP Inspector web UI"
echo "  2. Connect it to the Docker container"
echo "  3. Open http://localhost:6274 in your browser"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run MCP Inspector with docker run command
npx @modelcontextprotocol/inspector docker run -i ${IMAGE_NAME}:${IMAGE_TAG}
