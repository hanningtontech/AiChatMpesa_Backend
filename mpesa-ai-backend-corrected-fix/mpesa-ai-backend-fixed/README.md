# AI M-Pesa Payment Agent

An AI-powered FastAPI server with CLI interface that can process M-Pesa payments through natural language commands using Google's ADK and Safaricom's Daraja API.

## Features

- **🚀 FastAPI Server**: REST API with session management and agent interaction
- **💬 Beautiful CLI**: Clean command-line interface with filtered logs and token counting
- **💰 M-Pesa Integration**: Send payments, check transaction status, validate phone numbers
- **🤖 AI-Powered**: Uses Google Gemini 2.0 Flash for natural language understanding
- **📱 Phone Validation**: Validates and formats Kenyan phone numbers
- **📊 Transaction Tracking**: Real-time payment status and account balance
- **💾 SQLite Database**: Simple session persistence without external dependencies

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment (if using one)
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

**CLI Mode (Beautiful Interface):**
```bash
python app/main.py cli
```

**Server Mode (REST API):**
```bash
python app/main.py
# Server will start at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Run Unified Webhook Server (M-Pesa + WhatsApp)

For webhook integrations (M-Pesa callbacks and WhatsApp messages):

```bash
# Start the unified webhook server on port 5455
python callback_server.py

# In another terminal, expose with ngrok
ngrok http 5455
```

**Endpoints:**
- 📱 M-Pesa: `http://localhost:5455/mpesa/callback`
- 💬 WhatsApp: `http://localhost:5455/whatsapp/webhook`
- 🧪 Test: `http://localhost:5455/whatsapp/test`

### 4. Configure M-Pesa (Optional)

For actual M-Pesa payments, configure your credentials:

1. Get credentials from [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Update `.env` file:
   ```env
   MPESA_CONSUMER_KEY=your_consumer_key
   MPESA_CONSUMER_SECRET=your_consumer_secret
   MPESA_BUSINESS_SHORT_CODE=your_shortcode
   MPESA_PASSKEY=your_passkey
   MPESA_CALLBACK_URL=https://your-domain.com/mpesa/callback
   MPESA_ENVIRONMENT=sandbox
   ```

### 5. Configure WhatsApp (Optional)

For WhatsApp integration via Twilio:

1. Get credentials from [Twilio Console](https://console.twilio.com/)
2. Add to `.env` file:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```
3. Configure webhook URL in Twilio: `https://your-ngrok-url.ngrok.io/whatsapp/webhook`

📖 **Detailed Setup:** See [docs/WHATSAPP_SETUP.md](docs/WHATSAPP_SETUP.md)

## 📚 Documentation

For detailed documentation, examples, and setup guides, see the **[docs/](docs/)** folder:

- **[API Examples](docs/api_examples.md)** - Complete API usage examples
- **[CLI Demo](docs/cli_demo.md)** - Beautiful CLI interface demonstration
- **[Setup Guides](docs/)** - Docker, Ngrok, and M-Pesa integration guides

## 💬 Usage Examples

The agent can handle natural language commands like:
- "Send 500 KSh to 0712345678 for lunch"
- "Check the status of transaction ABC123"
- "What's my M-Pesa balance?"
- "Send 1000 to 0722123456 for rent payment"

### CLI Example:
```
💬 You: send 500 to 0712345678 for lunch

🤖 Agent:
────────────────────────────────────────────────────────────
  I'll help you send 500 KSh to 0712345678 for lunch right away!
  📱 Initiating M-Pesa payment...
  ✅ STK push sent successfully!
────────────────────────────────────────────────────────────
💡 Tokens: 1,247
```

### API Example:
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session456",
    "message": "Send 500 KSh to 0712345678 for lunch"
  }'
```

## 🛠️ API Endpoints

### Session Management
- `POST /sessions` - Create a new session
- `GET /sessions` - List all sessions
- `GET /sessions/{session_id}` - Get specific session
- `DELETE /sessions/{session_id}` - Delete session

### Agent Interaction
- `POST /run` - Send message to agent and get response
- `GET /health` - Health check endpoint

### Legacy Endpoints (ADK Compatible)
- `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}` - Create session with ID
- `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}` - Get session by ID

## 🔧 Available M-Pesa Tools

The AI agent has access to these M-Pesa tools:

- **`send_instant_payment()`** - Primary tool with real-time tracking
- **`send_instant_payment_with_tracking()`** - Advanced tracking options
- **`check_payment_status_realtime()`** - Real-time status checks
- **`send_mpesa_payment()`** - Legacy payment initiation
- **`get_mpesa_balance()`** - Account balance inquiries

The agent automatically chooses the right tool based on your natural language request.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MPESA_CONSUMER_KEY` | Your app's consumer key | Yes |
| `MPESA_CONSUMER_SECRET` | Your app's consumer secret | Yes |
| `MPESA_BUSINESS_SHORT_CODE` | Your business short code | Yes |
| `MPESA_PASSKEY` | Your app's passkey | Yes |
| `MPESA_CALLBACK_URL` | URL for M-Pesa callbacks | Yes |
| `MPESA_ENVIRONMENT` | `sandbox` or `production` | No (default: sandbox) |

## Security Notes

- Never commit your `.env` file to version control
- Use sandbox environment for testing
- Implement proper callback URL handling for production
- Consider implementing additional security measures for production use

## 🚀 Features

- **Zero Complexity**: Simple setup with SQLite database
- **Beautiful CLI**: Clean interface with filtered logs and token counting
- **Session Persistence**: Automatic session management and history
- **Real-time Payments**: Instant M-Pesa processing with callback integration
- **RESTful API**: Complete FastAPI server with auto-generated docs
- **AI-Powered**: Smart payment description inference from context

## Troubleshooting

### Common Issues

1. **"Failed to get M-Pesa access token"**
   - Check your consumer key and secret
   - Ensure you're using the correct environment (sandbox/production)

2. **"Invalid phone number"**
   - Ensure phone numbers are in Kenyan format
   - Use the validation tool to check format

3. **STK Push fails**
   - Verify your business short code and passkey
   - Check that callback URL is accessible (for production)

### Getting Help

- Check the [Safaricom Developer Documentation](https://developer.safaricom.co.ke/docs)
- Review the test script output for detailed error messages
- Ensure all environment variables are properly set
