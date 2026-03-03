#!/bin/bash
# Meeseeks Box Start Script
# Start the containerized consciousness stack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🥒 Starting Meeseeks Box..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Pull Ollama model if not exists (after container starts)
echo "📦 Starting containers..."
docker-compose up -d

# Wait for ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 5

# Pull the embedding model
echo "🧠 Pulling nomic-embed-text model..."
docker exec meeseeks-ollama ollama pull nomic-embed-text 2>/dev/null || echo "   (Model may already exist)"

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

echo ""
echo "✅ Meeseeks Box is running!"
echo ""
echo "   API:      http://localhost:8080"
echo "   Metrics:  http://localhost:9090"
echo "   Ollama:   http://localhost:11434"
echo ""
echo "Commands:"
echo "   ./meeseeks status   - Check system status"
echo "   ./meeseeks spawn    - Spawn a Meeseeks"
echo "   ./meeseeks dream    - Trigger dream cycle"
echo "   ./meeseeks logs     - View logs"
echo "   ./meeseeks stop     - Stop the box"
