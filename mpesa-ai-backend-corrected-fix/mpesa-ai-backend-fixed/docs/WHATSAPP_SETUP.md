# WhatsApp Integration Setup Guide

This guide will help you set up Twilio WhatsApp integration with your M-Pesa agent.

## 🚀 Quick Setup

### 1. Twilio Account Setup

1. **Create a Twilio Account**
   - Go to [https://console.twilio.com/](https://console.twilio.com/)
   - Sign up for a free account

2. **Get Your Credentials**
   - Find your `Account SID` and `Auth Token` in the Twilio Console
   - Copy these to your `.env` file

3. **WhatsApp Sandbox Setup**
   - Go to **Messaging** → **Try it out** → **Send a WhatsApp message**
   - Follow the instructions to join the sandbox
   - Note the sandbox number (usually `+1 415 523 8886`)

### 2. Environment Configuration

Add these to your `.env` file:

```bash
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 3. Webhook Configuration

1. **Start the Server**
   ```bash
   python callback_server.py
   ```

2. **Expose with ngrok**
   ```bash
   ngrok http 5455
   ```

3. **Configure Twilio Webhook**
   - In Twilio Console, go to **Messaging** → **Settings** → **WhatsApp sandbox settings**
   - Set webhook URL to: `https://your-ngrok-url.ngrok.io/whatsapp/webhook`
   - Set status callback URL to: `https://your-ngrok-url.ngrok.io/whatsapp/status`

## 📱 Testing

1. **Join the Sandbox**
   - Send the join code to the Twilio sandbox number
   - Example: Send `join <your-sandbox-code>` to `+1 415 523 8886`

2. **Send a Test Message**
   - Send any message to the sandbox number
   - You should receive a response from your agent

3. **Check Logs**
   - Monitor the server console for incoming messages
   - Check `logs/whatsapp_messages_YYYY-MM-DD.json` for detailed logs

## 🔧 Advanced Configuration

### Custom Agent Responses

The agent processing is handled in the `process_whatsapp_message()` function in `callback_server.py`. You can customize this to:

- Integrate with your existing M-Pesa agent
- Add conversation context
- Handle different message types
- Implement user authentication

### Production Setup

For production use:

1. **Get a Twilio WhatsApp Business Account**
   - Apply for WhatsApp Business API access
   - Get your own WhatsApp Business number

2. **Use a Proper Domain**
   - Replace ngrok with a proper domain
   - Use HTTPS with SSL certificates

3. **Add Error Handling**
   - Implement retry logic
   - Add monitoring and alerting

## 🛠 Troubleshooting

### Common Issues

1. **Webhook Not Receiving Messages**
   - Check ngrok is running and accessible
   - Verify webhook URL in Twilio console
   - Check server logs for errors

2. **Agent Not Responding**
   - Ensure agent is properly imported
   - Check for import errors in server logs
   - Verify environment variables are set

3. **Messages Not Sending**
   - Verify Twilio credentials
   - Check account balance
   - Ensure phone number is verified in sandbox

### Debug Mode

Enable debug logging by setting `debug=True` in the Flask app configuration.

## 📊 Monitoring

The server provides several endpoints for monitoring:

- `http://localhost:5455/` - Server status page
- `http://localhost:5455/logs` - Recent logs viewer
- Log files in `logs/` directory

## 🔐 Security Notes

- Keep your Twilio credentials secure
- Use environment variables for sensitive data
- Implement webhook signature verification for production
- Consider rate limiting for production use

## 📞 Support

If you encounter issues:

1. Check the server logs
2. Verify your Twilio configuration
3. Test with ngrok tunnel
4. Review the webhook payload format

The unified server handles both M-Pesa callbacks and WhatsApp webhooks on the same port (5455), making it perfect for ngrok's free tier limitation.
