#!/bin/bash
# Odoo Setup Script for Gold Tier AI Employee
# This script sets up Odoo Community Edition with Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Odoo Community Setup for AI Employee"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are available"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p odoo-data odoo-config odoo-addons postgres-data
echo "✓ Directories created"
echo ""

# Check if Odoo is already running
if docker ps | grep -q odoo_community; then
    echo "⚠️  Odoo is already running!"
    echo "   Access it at: http://localhost:8069"
    echo ""
    read -p "Do you want to restart Odoo? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    echo "Stopping Odoo..."
    docker compose down
fi

# Start Odoo
echo "Starting Odoo Community Edition..."
echo "This may take a few minutes on first run..."
echo ""

if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo ""
echo "Waiting for Odoo to start (this takes 2-3 minutes on first run)..."

# Wait for Odoo to be ready
for i in {1..60}; do
    if curl -s http://localhost:8069 > /dev/null 2>&1; then
        echo ""
        echo "✓ Odoo is ready!"
        break
    fi
    if (( i % 10 == 0 )); then
        echo "   Still starting... ($i/60)"
    fi
    sleep 5
done

echo ""
echo "=========================================="
echo "Odoo Setup Complete!"
echo "=========================================="
echo ""
echo "📍 Access Odoo at: http://localhost:8069"
echo ""
echo "🔐 Default Credentials:"
echo "   Database: Create a new database"
echo "   Email: admin@example.com"
echo "   Password: admin"
echo ""
echo "📚 Next Steps:"
echo "   1. Open http://localhost:8069 in your browser"
echo "   2. Create a new database"
echo "   3. Install Accounting and Invoicing modules"
echo "   4. Configure your company settings"
echo "   5. Run the MCP server setup script"
echo ""
echo "🛑 To stop Odoo:"
echo "   cd odoo && docker compose down"
echo ""
echo "📖 Documentation:"
echo "   https://www.odoo.com/documentation/19.0/"
echo "=========================================="
