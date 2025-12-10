# JTR MCP Server - Build John from Source
FROM ubuntu:24.04

LABEL maintainer="Your Name"
LABEL description="John the Ripper MCP Server with Jumbo build"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libgmp-dev \
    libpcap-dev \
    libnss3-dev \
    libkrb5-dev \
    pkg-config \
    git \
    wget \
    python3.12 \
    python3-pip \
    python3-venv \
    python3-full \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Build John the Ripper from source
WORKDIR /tmp
RUN git clone --depth 1 https://github.com/openwall/john.git -b bleeding-jumbo && \
    cd john/src && \
    ./configure && \
    make -j$(nproc) && \
    # Install to /opt
    mkdir -p /opt/john && \
    cp -r ../run/* /opt/john/ && \
    # Cleanup
    cd / && rm -rf /tmp/john

# Add John to PATH immediately
ENV PATH="/opt/john:${PATH}"

# Verify John works
RUN john --list=build-info | head -10 && \
    john --list=formats | head -20

# Setup Python app
WORKDIR /app

# Create venv and install packages in one layer to avoid network issues
RUN python3 -m venv /app/venv

COPY requirements.txt .

# Try to install with better error handling
RUN /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt || \
    (echo "WARNING: Package installation failed. Retrying..." && \
     sleep 5 && \
     /app/venv/bin/pip install --no-cache-dir -r requirements.txt)

# Copy application
COPY src/ ./src/
COPY wordlists/ ./wordlists/
COPY scripts/ ./scripts/

# Download rockyou.txt wordlist during build
RUN mkdir -p /app/wordlists/common && \
    cd /app/wordlists/common && \
    wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt && \
    echo "Downloaded rockyou.txt ($(du -h rockyou.txt | cut -f1))"

RUN mkdir -p sessions results temp logs

# Environment
ENV PATH="/app/venv/bin:/opt/john:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV JOHN_BINARY=john

ENTRYPOINT ["/app/venv/bin/python", "-m", "src.jtr_mcp.server"]
