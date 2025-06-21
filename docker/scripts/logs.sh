#!/bin/bash
# Show logs for different environments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/.."

cd "$DOCKER_DIR"

# Detect docker compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

case "${1:-dev}" in
    dev)
        echo "📋 Development logs:"
        $DOCKER_COMPOSE --profile dev logs -f
        ;;
    prod)
        echo "📋 Production logs:"
        $DOCKER_COMPOSE --profile prod logs -f
        ;;
    all)
        echo "📋 All logs:"
        $DOCKER_COMPOSE logs -f
        ;;
    *)
        echo "Usage: $0 {dev|prod|all}"
        exit 1
        ;;
esac 