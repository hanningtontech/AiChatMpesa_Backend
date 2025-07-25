#!/bin/bash

echo "🚀 Starting AI M-Pesa Backend Services..."
echo "=================================================="

# Wait for environment to be ready
sleep 2

echo "📊 Environment Check:"
echo "   🤖 AI Agent API: Will start on port 3343"
echo "   📱 Webhook Server: Will start on port 3344"
echo "   📂 Database: SQLite (mpesa_sessions.db)"
echo "   📝 Logs: /app/logs/"

# Check if .env file exists
if [ -f "/app/.env" ]; then
    echo "   ✅ Environment file found"
else
    echo "   ⚠️  No .env file found - using environment variables"
fi

echo ""
echo "🔄 Starting services with supervisor..."

# Start supervisor which will manage both services
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
