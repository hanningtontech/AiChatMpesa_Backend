# 🚀 Coolify Deployment Guide

Deploy your AI M-Pesa Backend on Coolify with Docker.

## 📋 Prerequisites

1. **Coolify Instance** - Running and accessible
2. **Domain/Subdomain** - For your API (e.g., `api.yourdomain.com`)
3. **M-Pesa Credentials** - From Safaricom Developer Portal
4. **Twilio Credentials** - For WhatsApp integration (optional)
5. **Google API Key** - For AI functionality

## 🔧 Coolify Setup Steps

### Step 1: Create New Project in Coolify

1. Login to your Coolify dashboard
2. Click **"New Project"**
3. Choose **"Docker Compose"** deployment type
4. Connect your Git repository

### Step 2: Configure Environment Variables

In Coolify, add these environment variables:

#### Required Variables:
```env
# M-Pesa Configuration
MPESA_CONSUMER_KEY=your_consumer_key_here
MPESA_CONSUMER_SECRET=your_consumer_secret_here
MPESA_BUSINESS_SHORT_CODE=174379
MPESA_PASSKEY=your_passkey_here
# 🚨 CRITICAL: Use your actual webhook domain, NOT ngrok!
MPESA_CALLBACK_URL=https://webhooks.yourdomain.com/mpesa/callback
MPESA_ENVIRONMENT=sandbox

# Google AI
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=0
```

#### Optional Variables (for WhatsApp):
```env
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Step 3: Configure Domains (CRITICAL for M-Pesa Callbacks)

**🚨 Important**: You CANNOT use ngrok in production. You need real domains.

#### Option A: Separate Subdomains (Recommended)
1. **AI Agent API**: `api.yourdomain.com` → Port `8000`
2. **Webhook Server**: `webhooks.yourdomain.com` → Port `5455`

#### Option B: Single Domain with Path Routing
- `yourdomain.com` → Port `8000` (AI Agent API)
- `yourdomain.com/webhooks/*` → Port `5455` (Webhook Server)

#### DNS Configuration Required:
```
A Record: api.yourdomain.com → YOUR_COOLIFY_SERVER_IP
A Record: webhooks.yourdomain.com → YOUR_COOLIFY_SERVER_IP
```

#### Your Callback URLs Will Be:
- **M-Pesa**: `https://webhooks.yourdomain.com/mpesa/callback`
- **WhatsApp**: `https://webhooks.yourdomain.com/whatsapp/webhook`

### Step 4: Deploy

1. Click **"Deploy"** in Coolify
2. Monitor the build logs
3. Wait for deployment to complete

## 🌐 Service Endpoints

After deployment, your services will be available at:

### AI Agent API (Port 8000):
- **Health Check**: `https://api.yourdomain.com/health`
- **API Docs**: `https://api.yourdomain.com/docs`
- **Create Session**: `POST https://api.yourdomain.com/sessions`
- **Send Command**: `POST https://api.yourdomain.com/run`

### Webhook Server (Port 5455):
- **M-Pesa Callback**: `https://webhooks.yourdomain.com/mpesa/callback`
- **WhatsApp Webhook**: `https://webhooks.yourdomain.com/whatsapp/webhook`
- **Test Endpoint**: `https://webhooks.yourdomain.com/whatsapp/test`

## 🔒 Security Configuration

### 1. Update M-Pesa Callback URL
Update your M-Pesa app configuration with:
```
https://webhooks.yourdomain.com/mpesa/callback
```

### 2. Configure Twilio Webhook
In Twilio Console, set webhook URL to:
```
https://webhooks.yourdomain.com/whatsapp/webhook
```

### 3. Enable HTTPS
Coolify automatically provides SSL certificates via Let's Encrypt.

## 📊 Monitoring & Logs

### View Logs in Coolify:
1. Go to your project dashboard
2. Click on **"Logs"** tab
3. Monitor both services:
   - `ai-agent-api` - AI Agent API logs
   - `webhook-server` - Webhook server logs

### Health Checks:
- Coolify will automatically monitor the health endpoint
- Service will restart if health check fails

## 🧪 Testing Deployment

### 1. Test AI Agent API:
```bash
curl https://api.yourdomain.com/health
```

### 2. Test Webhook Server:
```bash
curl https://webhooks.yourdomain.com/whatsapp/test
```

### 3. Create a Session:
```bash
curl -X POST https://api.yourdomain.com/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

### 4. Send Payment Command:
```bash
curl -X POST https://api.yourdomain.com/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "your_session_id",
    "message": "What is my M-Pesa balance?"
  }'
```

## 🔄 Updates & Maintenance

### Updating the Application:
1. Push changes to your Git repository
2. Coolify will auto-deploy (if auto-deploy is enabled)
3. Or manually trigger deployment in Coolify dashboard

### Environment Variable Updates:
1. Update variables in Coolify dashboard
2. Restart the application

### Database Persistence:
- SQLite database is persisted via Docker volumes
- Data survives container restarts

## 🚨 Troubleshooting

### Common Issues:

1. **Health Check Failing**:
   - Check if port 8000 is accessible
   - Verify environment variables are set
   - Check application logs

2. **M-Pesa Callbacks Not Working**:
   - Verify callback URL is publicly accessible
   - Check M-Pesa app configuration
   - Ensure HTTPS is working

3. **WhatsApp Messages Not Processing**:
   - Verify Twilio webhook configuration
   - Check Twilio credentials
   - Test webhook endpoint manually

### Debug Commands:
```bash
# Check if services are running
curl https://api.yourdomain.com/health

# Test webhook endpoint
curl https://webhooks.yourdomain.com/whatsapp/test

# Check logs in Coolify dashboard
```

## 📱 Mobile App Integration

Update your mobile app's base URL to:
```
https://api.yourdomain.com
```

All API endpoints remain the same, just with your new domain.

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Domains set up and SSL working
- [ ] M-Pesa callback URL updated
- [ ] Twilio webhook URL updated
- [ ] Health checks passing
- [ ] Mobile app updated with new API URL
- [ ] Test payments working
- [ ] Monitoring set up

**Your AI M-Pesa Backend is now live on Coolify!** 🚀
