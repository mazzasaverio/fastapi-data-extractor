#!/bin/bash
# Clean up Docker resources

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/.."

cd "$DOCKER_DIR"

echo "🧹 Cleaning Docker resources..."

# Stop all services
docker compose --profile dev down 2>/dev/null || true
docker compose --profile prod down 2>/dev/null || true

# Remove images
docker compose --profile dev --profile prod down --rmi all --volumes --remove-orphans 2>/dev/null || true

# Clean system (optional)
echo "🗑️  Cleaning unused Docker resources..."
docker system prune -f

echo "✅ Cleanup completed!" 