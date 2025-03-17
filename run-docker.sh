#!/bin/bash
set -e

# Stop and remove existing container if it exists
if docker ps -a | grep -q bsky-monitor; then
    echo "Stopping and removing existing container..."
    docker stop bsky-monitor >/dev/null 2>&1 || true
    docker rm bsky-monitor >/dev/null 2>&1 || true
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with the required environment variables."
    echo "Required variables: BLUESKY_HANDLE, BLUESKY_PASSWORD, BLUESKY_RECIPIENT_DID"
    exit 1
fi

# Verify .env file format
echo "Verifying .env file format..."
missing_vars=0
for var in BLUESKY_HANDLE BLUESKY_PASSWORD BLUESKY_RECIPIENT_DID; do
    if ! grep -q "^$var=" .env; then
        echo "Error: $var is missing from .env file"
        missing_vars=1
    fi
done

if [ $missing_vars -eq 1 ]; then
    echo "Please fix your .env file. Format should be:"
    echo "BLUESKY_HANDLE=your_handle.bsky.social"
    echo "BLUESKY_PASSWORD=your_app_password"
    echo "BLUESKY_RECIPIENT_DID=did:plc:your_did_here"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
DOCKER_BUILDKIT=1 docker build -t local/bsky-monitor:latest .

# Run the container with environment variables from .env
echo "Starting container with environment variables from .env..."
docker run --name bsky-monitor \
    --restart always \
    --env-file .env \
    -d local/bsky-monitor:latest

echo "Container started. To view logs: docker logs -f bsky-monitor"
echo "To stop: docker stop bsky-monitor" 