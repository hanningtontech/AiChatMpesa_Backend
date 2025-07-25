#!/bin/bash

# AI M-Pesa Backend - Local Docker Deployment Script
# Use this to test your Docker setup before deploying to Coolify

echo "🚀 AI M-Pesa Backend - Docker Deployment"
echo "========================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.production to .env and configure your credentials"
    echo "   cp .env.production .env"
    exit 1
fi

echo "✅ Environment file found"

# Build and start services
echo ""
echo "🔨 Building Docker image..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services!"
    exit 1
fi

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Health check
echo ""
echo "🏥 Checking service health..."

# Check AI Agent API
echo "   🤖 Testing AI Agent API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ AI Agent API is healthy"
else
    echo "   ❌ AI Agent API health check failed"
fi

# Check Webhook Server
echo "   📱 Testing Webhook Server..."
if curl -f http://localhost:5455/whatsapp/test > /dev/null 2>&1; then
    echo "   ✅ Webhook Server is healthy"
else
    echo "   ❌ Webhook Server health check failed"
fi

echo ""
echo "📊 Service Status:"
echo "   🤖 AI Agent API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   📱 Webhook Server: http://localhost:5455"
echo "   🧪 Test Endpoint: http://localhost:5455/whatsapp/test"

echo ""
echo "📝 View logs with:"
echo "   docker-compose logs -f"

echo ""
echo "🛑 Stop services with:"
echo "   docker-compose down"

echo ""
echo "✅ Deployment complete! Your services are running."
echo "   Ready for Coolify deployment! 🚀"
