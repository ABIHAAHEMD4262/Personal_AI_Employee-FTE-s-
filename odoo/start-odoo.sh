#!/bin/bash
# Odoo Setup Script for AI Employee
# This script starts Odoo Community Edition using Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Odoo Community Edition..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "   Install: https://docs.docker.com/compose/install/"
    exit 1
fi

# Determine which docker-compose command to use
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p odoo-data odoo-config odoo-addons postgres-data

# Check if Odoo is already running
if $DOCKER_COMPOSE ps | grep -q "odoo_community"; then
    echo "⚠️  Odoo is already running!"
    echo "   Access at: http://localhost:8069"
    echo ""
    echo "To restart, run: $DOCKER_COMPOSE restart"
    exit 0
fi

# Start Odoo
echo "🔨 Starting Odoo containers..."
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for Odoo to start (this may take 1-2 minutes)..."

# Wait for Odoo to be ready
MAX_WAIT=120
WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069 | grep -q "200\|303"; then
        echo ""
        echo "✅ Odoo is ready!"
        break
    fi
    echo -n "."
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo ""
    echo "⚠️  Odoo may not have started properly."
    echo "   Check logs with: $DOCKER_COMPOSE logs -f"
fi

echo ""
echo "🎉 Odoo Community Edition is running!"
echo ""
echo "📍 Access Odoo at: http://localhost:8069"
echo ""
echo "📋 Next Steps:"
echo "   1. Open http://localhost:8069 in your browser"
echo "   2. Create a new database (name it 'odoo')"
echo "   3. Set master password: odoo (or change in docker-compose.yml)"
echo "   4. Install Accounting, Invoicing, and Contacts apps"
echo "   5. Enable Developer Mode: Settings → Activate developer mode"
echo "   6. Generate API Key: Settings → Users → Your User → API Keys"
echo "   7. Get User ID from URL (e.g., /web#id=2&action=...)"
echo ""
echo "🔧 After setup, configure Odoo MCP server:"
echo "   cd ../skills/mcp-servers/odoo-mcp"
echo "   cp .env.example .env"
echo "   # Edit .env with your Odoo credentials"
echo ""
echo "📊 Useful Commands:"
echo "   View logs:          $DOCKER_COMPOSE logs -f"
echo "   Stop Odoo:          $DOCKER_COMPOSE down"
echo "   Restart Odoo:       $DOCKER_COMPOSE restart"
echo "   Remove all data:    $DOCKER_COMPOSE down -v"
echo ""
