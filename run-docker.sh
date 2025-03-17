#!/bin/bash
set -e

# Stop and remove existing container if it exists
if docker ps -a | grep -q bsky-monitor; then
    echo "Stopping and removing existing container..."
    docker stop bsky-monitor >/dev/null 2>&1 || true
    docker rm bsky-monitor >/dev/null 2>&1 || true
fi

# Build the Docker image with proper caching
echo "Building Docker image..."
DOCKER_BUILDKIT=1 docker build -t local/bsky-monitor:latest .

# Run the container with environment variables from .env
echo "Starting container..."
docker run --name bsky-monitor \
    --restart always \
    --env-file .env \
    -d local/bsky-monitor:latest

echo "Container started. To view logs: docker logs -f bsky-monitor"
echo "To stop: docker stop bsky-monitor" 