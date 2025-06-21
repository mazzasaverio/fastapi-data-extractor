#!/bin/bash
# Check Docker and Docker Compose installation

echo "🔍 Checking Docker setup..."

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose (standalone): $(docker-compose --version)"
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    echo "✅ Docker Compose (plugin): $(docker compose version)"
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose not found."
    echo "Please install Docker Compose:"
    echo "  - For Docker Desktop: It's included"
    echo "  - For Linux: sudo apt install docker-compose-plugin"
    exit 1
fi

# Check Docker daemon
if docker info &> /dev/null; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon is not running"
    echo "Please start Docker daemon"
    exit 1
fi

echo ""
echo "🎉 Docker setup is ready!"
echo "You can now run:"
echo "  ./scripts/dev.sh start    # For development"
echo "  ./scripts/prod.sh start   # For production" 