# JTR MCP Server - Simplified with apt-installed John
FROM ubuntu:24.04

LABEL description="John the Ripper MCP Server for password cracking"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive

# Install John the Ripper and Python
RUN apt-get update && apt-get install -y \
    john \
    john-data \
    python3.12 \
    python3-pip \
    python3-venv \
    python3-full \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment
RUN python3 -m venv /app/venv

# Install Python dependencies
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY wordlists/ ./wordlists/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p sessions results temp logs

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV JOHN_BINARY=john

# STDIO transport (default)
ENTRYPOINT ["/app/venv/bin/python", "-m", "src.jtr_mcp.server"]

# TODO: Add HTTP/SSE transport support
# EXPOSE 8000
# CMD ["uvicorn", "src.jtr_mcp.server_http:app", "--host", "0.0.0.0", "--port", "8000"]
