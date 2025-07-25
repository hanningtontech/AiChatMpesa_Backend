#!/bin/bash

# AI M-Pesa WhatsApp Integration - Server Startup Script
# This script starts both the AI Agent API and the Webhook Server

echo "🚀 Starting AI M-Pesa WhatsApp Integration Servers..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "❌ Virtual environment 'env' not found!"
    echo "   Please create it with: python -m venv env"
    exit 1
fi

# Activate virtual environment
source env/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import twilio, flask, fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing missing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "🤖 Starting AI Agent API Server (port 8000)..."
echo "   This provides the intelligent M-Pesa agent responses"
echo ""

# Start the AI Agent API in the background
python app/main.py &
AGENT_PID=$!

# Wait a moment for the agent to start
sleep 3

echo ""
echo "📱 Starting Unified Webhook Server (port 5455)..."
echo "   This handles M-Pesa callbacks and WhatsApp webhooks"
echo ""

# Start the webhook server
python callback_server.py &
WEBHOOK_PID=$!

# Wait a moment for the webhook server to start
sleep 2

echo ""
echo "✅ Both servers are starting up!"
echo ""
echo "📊 Server Status:"
echo "   🤖 AI Agent API: http://localhost:8000 (PID: $AGENT_PID)"
echo "   📱 Webhook Server: http://localhost:5455 (PID: $WEBHOOK_PID)"
echo ""
echo "📖 Next Steps:"
echo "   1. Check server logs above for any errors"
echo "   2. Open another terminal and run: ngrok http 5455"
echo "   3. Configure Twilio webhook with your ngrok URL"
echo "   4. Send a WhatsApp message to test!"
echo ""
echo "🛑 To stop servers: Press Ctrl+C or run: kill $AGENT_PID $WEBHOOK_PID"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $AGENT_PID 2>/dev/null
    kill $WEBHOOK_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
echo "💡 Servers are running. Press Ctrl+C to stop both servers."
wait
