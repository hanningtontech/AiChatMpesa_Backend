# 🚀 Coolify Deployment - AI M-Pesa Backend

Your AI M-Pesa backend is now ready for Coolify deployment with Docker!

## 📦 What's Been Set Up

### 1. **Optimized Dockerfile**
- Multi-service container running both AI Agent API and Webhook Server
- Uses Supervisor to manage both services
- Health checks configured
- Proper port exposure (8000 for API, 5455 for webhooks)

### 2. **Docker Compose Configuration**
- Production-ready docker-compose.yml
- Environment variable mapping
- Volume persistence for logs and database
- Health check monitoring

### 3. **Service Architecture**
```
┌─────────────────────────────────────┐
│           Docker Container          │
├─────────────────────────────────────┤
│  🤖 AI Agent API (Port 8000)       │
│  - Session management               │
│  - Natural language processing     │
│  - M-Pesa payment commands         │
│  - REST API endpoints              │
├─────────────────────────────────────┤
│  📱 Webhook Server (Port 5455)     │
│  - M-Pesa callbacks                │
│  - WhatsApp message handling       │
│  - Real-time notifications         │
└─────────────────────────────────────┘
```

## 🔧 Files Created/Modified

### New Files:
- `docker/supervisord.conf` - Service management configuration
- `docker/start.sh` - Container startup script
- `.env.production` - Production environment template
- `deploy.sh` - Local testing script
- `docs/COOLIFY_DEPLOYMENT.md` - Detailed deployment guide

### Modified Files:
- `Dockerfile` - Optimized for dual-service deployment
- `docker-compose.yml` - Coolify-ready configuration

## 🚀 Quick Deployment Steps

### 1. **Test Locally First**
```bash
# Copy and configure environment
cp .env.production .env
# Edit .env with your credentials

# Test the Docker setup
./deploy.sh
```

### 2. **Deploy to Coolify**
1. Create new project in Coolify
2. Choose "Docker Compose" deployment
3. Connect your Git repository
4. Configure environment variables (see below)
5. Set up domains
6. Deploy!

### 3. **Environment Variables for Coolify**

### 🚨 CRITICAL: No Ngrok in Production!
You MUST use your actual domain for callback URLs.

```env
# Required
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_BUSINESS_SHORT_CODE=your_shortcode
MPESA_PASSKEY=your_passkey
# 🚨 Use your REAL domain, NOT ngrok!
MPESA_CALLBACK_URL=https://webhooks.yourdomain.com/mpesa/callback
GOOGLE_API_KEY=your_google_key

# Optional (for WhatsApp)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+your_number
```

### 🌐 Domain Setup Required:
1. **Purchase/configure domain**: `yourdomain.com`
2. **DNS Records**: Point to your Coolify server
3. **Coolify Domains**:
   - `api.yourdomain.com` → Port 8000
   - `webhooks.yourdomain.com` → Port 5455

## 🌐 Service Endpoints

After deployment:

### AI Agent API (Port 8000):
- **Health**: `https://api.yourdomain.com/health`
- **Docs**: `https://api.yourdomain.com/docs`
- **Sessions**: `POST https://api.yourdomain.com/sessions`
- **Commands**: `POST https://api.yourdomain.com/run`

### Webhook Server (Port 5455):
- **M-Pesa**: `https://webhooks.yourdomain.com/mpesa/callback`
- **WhatsApp**: `https://webhooks.yourdomain.com/whatsapp/webhook`

## 📱 Mobile App Integration

Your friend can use the API with:
```javascript
const API_BASE_URL = 'https://api.yourdomain.com';

// Create session
const session = await fetch(`${API_BASE_URL}/sessions`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'user123' })
});

// Send payment command
const response = await fetch(`${API_BASE_URL}/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    session_id: session.id,
    message: 'Send 1000 to 0722123456'
  })
});
```

## 🔍 Monitoring & Logs

### In Coolify Dashboard:
- View real-time logs for both services
- Monitor health checks
- Track resource usage
- Manage deployments

### Service Health:
- Automatic health checks every 30 seconds
- Auto-restart on failure
- Supervisor manages service lifecycle

## 🎯 Production Checklist

- [ ] Environment variables configured in Coolify
- [ ] Domains set up with SSL
- [ ] M-Pesa callback URL updated in Safaricom portal
- [ ] Twilio webhook URL configured (if using WhatsApp)
- [ ] Local testing completed with `./deploy.sh`
- [ ] Health checks passing
- [ ] Mobile app updated with production API URL

## 🚨 Troubleshooting

### Common Issues:
1. **Build fails**: Check Dockerfile and dependencies
2. **Health check fails**: Verify environment variables
3. **Services not starting**: Check supervisor logs in Coolify
4. **API not accessible**: Verify port configuration and domains

### Debug Commands:
```bash
# Local testing
./deploy.sh

# Check logs
docker-compose logs -f

# Test endpoints
curl https://api.yourdomain.com/health
curl https://webhooks.yourdomain.com/whatsapp/test
```

## 📚 Documentation

- **[Coolify Deployment Guide](COOLIFY_DEPLOYMENT.md)** - Detailed setup instructions
- **[Mobile API Guide](MOBILE_API_GUIDE.md)** - For your friend's mobile app
- **[API Examples](api_examples.md)** - Complete API reference

**Your AI M-Pesa backend is ready for production deployment on Coolify!** 🚀

Need help? Check the detailed guides in the `docs/` folder or test locally with `./deploy.sh` first.
