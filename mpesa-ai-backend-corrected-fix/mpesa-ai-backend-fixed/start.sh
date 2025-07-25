#!/bin/bash

# AI Chat M-Pesa Backend - Docker Setup Script
# This script sets up and starts everything you need

set -e

echo "🚀 AI Chat M-Pesa Backend - Docker Setup"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker not installed. Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not installed. Install from: https://docs.docker.com/compose/install/"
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Check .env file
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Created .env from .env.example"
        print_warning "Please edit .env with your M-Pesa credentials:"
        echo "  - MPESA_CONSUMER_KEY"
        echo "  - MPESA_CONSUMER_SECRET" 
        echo "  - MPESA_PASSKEY"
        echo "  - GOOGLE_API_KEY"
        echo ""
        read -p "Press Enter after updating .env file..."
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
fi

# Check ngrok config
if [ ! -f ngrok.yml ]; then
    print_error "ngrok.yml not found. Please create it with your ngrok authtoken."
    exit 1
fi

if grep -q "YOUR_NGROK_AUTH_TOKEN_HERE" ngrok.yml; then
    print_warning "Please update ngrok.yml with your actual authtoken from:"
    print_info "https://dashboard.ngrok.com/get-started/your-authtoken"
    read -p "Press Enter after updating ngrok.yml..."
fi

print_status "Configuration files ready"

# Stop any existing containers
print_info "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
print_info "Building Docker images..."
docker-compose build

print_info "Starting services..."
docker-compose up -d

# Wait for backend to be ready
print_info "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8001/health &> /dev/null; then
        print_status "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
    sleep 2
done

# Get ngrok URL
sleep 3
NGROK_URL=""
if curl -s http://localhost:4040/api/tunnels &> /dev/null; then
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        print(tunnels[0]['public_url'])
except:
    pass
" 2>/dev/null || echo "")
fi

echo ""
print_status "🎉 Setup complete!"
echo ""
print_info "Service URLs:"
echo "🌐 Backend: http://localhost:8001"
echo "🏥 Health: http://localhost:8001/health"
echo "📋 Logs: http://localhost:8001/logs"
echo "🔧 Ngrok Dashboard: http://localhost:4040"

if [ ! -z "$NGROK_URL" ]; then
    echo ""
    print_info "Ngrok tunnel: $NGROK_URL"
    print_warning "Update your M-Pesa callback URL to: $NGROK_URL/mpesa/callback"
else
    print_warning "Ngrok tunnel not ready yet. Check http://localhost:4040"
fi

echo ""
print_info "Useful commands:"
echo "• View logs: docker-compose logs -f"
echo "• Stop: docker-compose down"
echo "• Restart: docker-compose restart"
echo "• Shell access: docker-compose exec mpesa-backend bash"

echo ""
print_status "Ready to receive M-Pesa callbacks! 🚀"
