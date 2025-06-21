#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/.."
ROOT_DIR="$DOCKER_DIR/.."

cd "$DOCKER_DIR"

case "${1:-start}" in
    start)
        echo "🚀 Starting FastAPI Production"
        docker compose --profile prod up --build -d
        ;;
    stop)
        echo "🛑 Stopping production services"
        docker compose --profile prod down
        ;;
    restart)
        echo "🔄 Restarting production services"
        docker compose --profile prod restart
        ;;
    logs)
        echo "📋 Showing production logs"
        docker compose --profile prod logs -f
        ;;
    shell)
        echo "🐚 Opening shell in production container"
        docker compose --profile prod exec fastapi-prod bash
        ;;
    rebuild)
        echo "🔨 Rebuilding production image"
        docker compose --profile prod build --no-cache
        ;;
    status)
        echo "📊 Showing services status"
        docker compose --profile prod ps
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|shell|rebuild|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start production services (default)"
        echo "  stop    - Stop production services"
        echo "  restart - Restart production services"
        echo "  logs    - Show logs"
        echo "  shell   - Open shell in container"
        echo "  rebuild - Rebuild images from scratch"
        echo "  status  - Show services status"
        exit 1
        ;;
esac