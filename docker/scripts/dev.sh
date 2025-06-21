#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/.."
ROOT_DIR="$DOCKER_DIR/.."

cd "$DOCKER_DIR"

case "${1:-watch}" in
    watch)
        echo "🚀 Starting FastAPI Development with Watch Mode"
        echo "   Changes to source code will automatically reload the server"
        docker compose --profile dev up --build --watch
        ;;
    start)
        echo "🚀 Starting FastAPI Development (normal mode)"
        docker compose --profile dev up --build -d
        ;;
    stop)
        echo "🛑 Stopping development services"
        docker compose --profile dev down
        ;;
    logs)
        echo "📋 Showing development logs"
        docker compose --profile dev logs -f fastapi-dev
        ;;
    shell)
        echo "🐚 Opening shell in development container"
        docker compose --profile dev exec fastapi-dev bash
        ;;
    rebuild)
        echo "🔨 Rebuilding development image"
        docker compose --profile dev build --no-cache
        ;;
    *)
        echo "Usage: $0 {watch|start|stop|logs|shell|rebuild}"
        echo ""
        echo "Commands:"
        echo "  watch   - Start with file watching (default)"
        echo "  start   - Start services in background"
        echo "  stop    - Stop all services"
        echo "  logs    - Show logs"
        echo "  shell   - Open shell in container"
        echo "  rebuild - Rebuild images from scratch"
        exit 1
        ;;
esac