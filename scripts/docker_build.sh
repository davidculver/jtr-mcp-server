#!/bin/bash
# Build Docker image for JTR MCP Server

set -e

IMAGE_NAME="jtr-mcp-server"
IMAGE_TAG="latest"

echo "🐳 Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "This may take 5-10 minutes on first build..."

docker build \
    -t ${IMAGE_NAME}:${IMAGE_TAG} \
    -f Dockerfile \
    .

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "📏 Size: $(docker images ${IMAGE_NAME}:${IMAGE_TAG} --format '{{.Size}}')"
echo ""
echo "To run the server:"
echo "  ./scripts/docker_run.sh"
echo ""
echo "To test with a hash:"
echo "  echo '{\"hash_file_content\": \"user:\$1\$salt\$hash\", \"wordlist\": \"small\"}' | docker run -i ${IMAGE_NAME}:${IMAGE_TAG}"
