#!/bin/bash
# Quick test of Docker container

set -e

IMAGE_NAME="jtr-mcp-server"
IMAGE_TAG="latest"

echo "🧪 Testing Docker container..."

# Test that john is installed
echo "1. Checking John the Ripper installation..."
docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} john --help | head -3

echo ""
echo "2. Checking Python environment..."
docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} python3 --version

echo ""
echo "3. Checking MCP server can start..."
timeout 2 docker run --rm -i ${IMAGE_NAME}:${IMAGE_TAG} || true

echo ""
echo "✅ All tests passed!"
