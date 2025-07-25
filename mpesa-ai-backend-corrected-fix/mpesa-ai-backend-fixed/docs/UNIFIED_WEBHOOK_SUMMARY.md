# Unified Webhook Server Summary

## ✅ What's Been Created

I've successfully created a **unified webhook server** that handles both M-Pesa callbacks and Twilio WhatsApp webhooks on **port 5455**, perfect for your ngrok free tier limitation.

## 🔧 Key Features

### 1. **Single Server, Multiple Webhooks**
- **Port 5455** - One port for both M-Pesa and WhatsApp
- **M-Pesa Callbacks**: `/mpesa/callback`, `/mpesa/timeout`
- **WhatsApp Webhooks**: `/whatsapp/webhook`, `/whatsapp/status`
- **Test Endpoint**: `/whatsapp/test` (for easy testing)

### 2. **Agent Integration Ready**
- Automatically detects if your M-Pesa agent is available
- Processes WhatsApp messages and sends intelligent responses
- Maintains existing M-Pesa callback functionality

### 3. **Simple & Clean**
- Minimal complexity (as requested)
- Clear logging for both M-Pesa and WhatsApp
- Easy to understand and modify

## 📁 Files Modified/Created

### Modified Files:
1. **`callback_server.py`** - Enhanced to handle WhatsApp webhooks
2. **`.env.example`** - Added Twilio configuration
3. **`README.md`** - Added unified server documentation

### New Files:
1. **`docs/WHATSAPP_SETUP.md`** - Complete WhatsApp setup guide
2. **`docs/UNIFIED_WEBHOOK_SUMMARY.md`** - This summary

## 🚀 How to Use

### 1. Start the Server
```bash
source env/bin/activate
python callback_server.py
```

### 2. Expose with ngrok
```bash
ngrok http 5455
```

### 3. Configure Webhooks
- **M-Pesa**: Use `https://your-ngrok-url.ngrok.io/mpesa/callback`
- **WhatsApp**: Use `https://your-ngrok-url.ngrok.io/whatsapp/webhook`

## 🧪 Testing

### WhatsApp Test Endpoint
Visit `http://localhost:5455/whatsapp/test` to test message processing without needing actual WhatsApp setup.

### Server Status
Visit `http://localhost:5455/` to see server status and available endpoints.

## 📱 WhatsApp Integration Flow

1. **User sends WhatsApp message** → Twilio webhook
2. **Server receives webhook** → Processes with agent
3. **Agent generates response** → Sent back via Twilio API
4. **User receives reply** → Seamless conversation

## 🔧 Environment Variables Needed

```env
# M-Pesa (existing)
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
# ... other M-Pesa vars

# WhatsApp (new)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## 📊 Logging

- **M-Pesa logs**: `logs/mpesa_callbacks_YYYY-MM-DD.json`
- **WhatsApp logs**: `logs/whatsapp_messages_YYYY-MM-DD.json`
- **Console output**: Real-time webhook processing

## 🎯 Next Steps

1. **Test the server** - Start it and visit the test endpoint
2. **Set up Twilio** - Follow the WhatsApp setup guide
3. **Configure ngrok** - Expose the server for webhook testing
4. **Customize agent responses** - Modify `process_whatsapp_message()` function

## 💡 Benefits

- **Single ngrok tunnel** for both M-Pesa and WhatsApp
- **Minimal complexity** - Simple Flask server
- **Easy to extend** - Add more webhook types easily
- **Agent integration** - Leverages your existing M-Pesa agent
- **Clean separation** - Different endpoints for different services

The server is ready to use and can handle both M-Pesa callbacks and WhatsApp messages seamlessly!
