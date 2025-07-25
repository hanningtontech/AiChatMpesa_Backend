# AI Agent Integration with WhatsApp

## 🎯 Overview

Your unified webhook server now integrates with your AI agent from `app/main.py` to provide intelligent M-Pesa responses via WhatsApp. The integration includes:

- **Personalized responses** using WhatsApp ProfileName
- **Session management** with user context
- **Intelligent M-Pesa operations** via your existing agent
- **Fallback responses** if the AI agent is unavailable

## 🏗 Architecture

```
WhatsApp Message → Webhook Server → AI Agent API → M-Pesa Tools → Response
     ↓                    ↓              ↓            ↓           ↓
User sends message → callback_server.py → main.py → agent.py → WhatsApp reply
```

## 🚀 Quick Start

### Option 1: Use the Startup Script
```bash
./start_servers.sh
```

### Option 2: Manual Startup
```bash
# Terminal 1: Start AI Agent API
source env/bin/activate
python app/main.py

# Terminal 2: Start Webhook Server  
source env/bin/activate
python callback_server.py

# Terminal 3: Expose with ngrok
ngrok http 5455
```

## 🔧 How It Works

### 1. **Message Reception**
When a WhatsApp message arrives:
```python
# Extract user information
profile_name = message_data.get('ProfileName', '')  # "wilfredeveloper"
wa_id = message_data.get('WaId', '')               # "254115425038"
message_body = message_data.get('Body', '')        # "Send 500 to 0712345678"
```

### 2. **Session Creation**
Creates/gets a session with user context:
```python
session_data = {
    "user_id": wa_id,
    "session_id": f"whatsapp_{wa_id}",
    "state": {
        "user_profile": {
            "name": profile_name,
            "phone": phone_number,
            "platform": "whatsapp"
        }
    }
}
```

### 3. **AI Agent Processing**
Sends message to your AI agent:
```python
agent_request = {
    "app_name": "mpesa_agent",
    "user_id": wa_id,
    "session_id": session_id,
    "message": message_body
}
```

### 4. **Response Extraction**
Extracts the agent's response and sends back to WhatsApp.

## 📊 Configuration

### Environment Variables
```env
# AI Agent API
AGENT_API_URL=http://localhost:8000

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+your_number
```

### Server Status Checks
The webhook server now checks:
- ✅ Twilio configuration
- ✅ AI Agent API connectivity
- ✅ M-Pesa callback manager status

## 🧪 Testing

### 1. **Check Server Status**
Visit `http://localhost:5455/` to see:
- Server configuration status
- Available endpoints
- Integration health

### 2. **Test WhatsApp Integration**
Send messages like:
- "Hello" → Personalized greeting
- "Send 500 to 0712345678" → AI agent processes M-Pesa request
- "Check balance" → AI agent handles balance inquiry

### 3. **Monitor Logs**
Watch both servers for:
```
📱 Processing WhatsApp message from wilfredeveloper (+254115425038): Send 500 to 0712345678
🤖 Calling AI Agent API for user 254115425038
📤 Sending message to agent: Send 500 to 0712345678
✅ AI Agent response: [intelligent response]
✅ WhatsApp reply sent successfully: SM1234567890
```

## 🔄 Fallback Behavior

If the AI agent is unavailable:
1. **Connection Error**: Falls back to simple responses
2. **API Error**: Provides helpful M-Pesa guidance
3. **Empty Response**: Uses context-aware fallbacks

## 🎯 Key Features

### **Personalization**
- Uses WhatsApp ProfileName in responses
- Maintains user context across conversations
- Remembers user preferences in session state

### **Intelligent Processing**
- Full access to your M-Pesa agent capabilities
- Real-time payment processing
- Balance checks and transaction history

### **Robust Error Handling**
- Graceful degradation if AI agent is down
- Detailed logging for debugging
- Automatic retry mechanisms

## 📈 Monitoring

### **Server Logs**
- AI Agent API: Standard FastAPI logs
- Webhook Server: Custom formatted logs with emojis
- Integration: API call success/failure tracking

### **Health Checks**
- `/health` endpoint on webhook server
- AI Agent API connectivity tests
- Twilio configuration validation

## 🛠 Troubleshooting

### **AI Agent Not Responding**
1. Check if `python app/main.py` is running
2. Verify `AGENT_API_URL` in `.env`
3. Test API directly: `curl http://localhost:8000/docs`

### **WhatsApp Messages Not Processing**
1. Check Twilio webhook configuration
2. Verify ngrok tunnel is active
3. Check server logs for errors

### **Session Issues**
1. Check database connectivity
2. Verify session creation in logs
3. Test with different user IDs

## 🚀 Production Considerations

1. **Database**: Use PostgreSQL instead of SQLite
2. **Monitoring**: Add proper logging and metrics
3. **Security**: Implement webhook signature verification
4. **Scaling**: Use proper WSGI server (gunicorn)
5. **Error Handling**: Add retry logic and circuit breakers

Your AI agent is now fully integrated with WhatsApp! 🎉
