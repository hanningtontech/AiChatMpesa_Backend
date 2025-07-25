# 🌐 Production Callback URL Setup

**No More Ngrok!** Setting up proper production callback URLs for M-Pesa and WhatsApp.

## 🚨 Why No Ngrok in Production?

- **Unreliable**: Ngrok URLs change on restart
- **Temporary**: Free ngrok tunnels expire
- **Unprofessional**: Random URLs in production
- **Security**: No control over the tunnel
- **Performance**: Extra latency through ngrok servers

## 🏗️ Production URL Structure

### Your Coolify Deployment Will Have:

```
┌─────────────────────────────────────────┐
│           Your Domain Setup             │
├─────────────────────────────────────────┤
│  🤖 AI Agent API                        │
│  https://api.yourdomain.com             │
│  (Port 8000 - for mobile apps)         │
├─────────────────────────────────────────┤
│  📱 Webhook Server                      │
│  https://webhooks.yourdomain.com        │
│  (Port 5455 - for callbacks)           │
└─────────────────────────────────────────┘
```

## 🔧 Domain Configuration Options

### Option 1: Separate Subdomains (Recommended)
```
api.yourdomain.com      → Port 8000 (AI Agent API)
webhooks.yourdomain.com → Port 5455 (Webhook Server)
```

**Callback URLs:**
- M-Pesa: `https://webhooks.yourdomain.com/mpesa/callback`
- WhatsApp: `https://webhooks.yourdomain.com/whatsapp/webhook`

### Option 2: Single Domain with Path Routing
```
yourdomain.com          → Port 8000 (AI Agent API)
yourdomain.com/webhooks → Port 5455 (Webhook Server)
```

**Callback URLs:**
- M-Pesa: `https://yourdomain.com/webhooks/mpesa/callback`
- WhatsApp: `https://yourdomain.com/webhooks/whatsapp/webhook`

### Option 3: Port-Based (Not Recommended for Production)
```
yourdomain.com:8000 → AI Agent API
yourdomain.com:5455 → Webhook Server
```

## 🎯 Step-by-Step Setup

### Step 1: Choose Your Domain
You need a domain name. Options:
- **Custom Domain**: `yourdomain.com` (recommended)
- **Coolify Subdomain**: `yourapp.coolify-instance.com`
- **Free Domain**: Use services like Freenom (for testing)

### Step 2: Configure DNS
Point your domain/subdomains to your Coolify server:
```
A Record: api.yourdomain.com → YOUR_COOLIFY_SERVER_IP
A Record: webhooks.yourdomain.com → YOUR_COOLIFY_SERVER_IP
```

### Step 3: Configure Coolify
In your Coolify project:

1. **Add Domains:**
   - `api.yourdomain.com` → Port 8000
   - `webhooks.yourdomain.com` → Port 5455

2. **Enable SSL:**
   - Coolify automatically provides Let's Encrypt SSL
   - Ensure HTTPS is working

### Step 4: Update Environment Variables
```env
# Update your .env file
MPESA_CALLBACK_URL=https://webhooks.yourdomain.com/mpesa/callback
```

### Step 5: Update M-Pesa App Configuration
1. Login to [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Go to your app settings
3. Update callback URL to: `https://webhooks.yourdomain.com/mpesa/callback`
4. Save changes

### Step 6: Update Twilio Configuration
1. Login to [Twilio Console](https://console.twilio.com/)
2. Go to WhatsApp settings
3. Update webhook URL to: `https://webhooks.yourdomain.com/whatsapp/webhook`
4. Save changes

## 🧪 Testing Production URLs

### Test M-Pesa Callback:
```bash
curl -X POST https://webhooks.yourdomain.com/mpesa/callback \
  -H "Content-Type: application/json" \
  -d '{
    "Body": {
      "stkCallback": {
        "MerchantRequestID": "test123",
        "CheckoutRequestID": "test456",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully."
      }
    }
  }'
```

### Test WhatsApp Webhook:
```bash
curl https://webhooks.yourdomain.com/whatsapp/test
```

### Test AI Agent API:
```bash
curl https://api.yourdomain.com/health
```

## 🔒 Security Considerations

### 1. HTTPS Only
- Always use HTTPS for production callbacks
- M-Pesa and Twilio require HTTPS endpoints
- Coolify provides automatic SSL certificates

### 2. Webhook Validation
Your webhook server already includes validation:
- M-Pesa signature verification
- Twilio request validation
- Proper error handling

### 3. Rate Limiting (Optional)
Consider adding rate limiting for production:
```python
# In callback_server.py (optional enhancement)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 📋 Production Checklist

### Before Deployment:
- [ ] Domain purchased and configured
- [ ] DNS records pointing to Coolify server
- [ ] Coolify domains configured with SSL
- [ ] Environment variables updated with production URLs

### After Deployment:
- [ ] Test webhook endpoints are accessible
- [ ] M-Pesa app callback URL updated
- [ ] Twilio webhook URL updated
- [ ] SSL certificates working
- [ ] Health checks passing

### Testing:
- [ ] Send test M-Pesa payment
- [ ] Send test WhatsApp message
- [ ] Verify callbacks are received
- [ ] Check logs for any errors

## 🚨 Common Issues & Solutions

### Issue: "Callback URL not reachable"
**Solution:**
- Verify domain DNS is correct
- Check Coolify port configuration
- Ensure SSL certificate is valid
- Test URL accessibility from external network

### Issue: "SSL certificate error"
**Solution:**
- Wait for Let's Encrypt certificate generation
- Check domain configuration in Coolify
- Verify DNS propagation

### Issue: "M-Pesa callbacks not received"
**Solution:**
- Verify callback URL in Safaricom portal
- Check webhook server logs
- Ensure URL is exactly: `https://webhooks.yourdomain.com/mpesa/callback`

### Issue: "WhatsApp messages not processed"
**Solution:**
- Verify webhook URL in Twilio console
- Check Twilio credentials
- Test webhook endpoint manually

## 🎯 Example Production Configuration

### Your .env file should look like:
```env
# Production URLs (replace yourdomain.com with your actual domain)
MPESA_CALLBACK_URL=https://webhooks.yourdomain.com/mpesa/callback

# M-Pesa Production Credentials
MPESA_CONSUMER_KEY=your_production_key
MPESA_CONSUMER_SECRET=your_production_secret
MPESA_BUSINESS_SHORT_CODE=your_production_shortcode
MPESA_PASSKEY=your_production_passkey
MPESA_ENVIRONMENT=production

# Twilio Production Credentials
TWILIO_ACCOUNT_SID=your_production_sid
TWILIO_AUTH_TOKEN=your_production_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+your_production_number
```

### Your mobile app will use:
```javascript
const API_BASE_URL = 'https://api.yourdomain.com';
```

## 🚀 Ready for Production!

Once you have your domain configured and deployed on Coolify:

1. **No more ngrok needed** ✅
2. **Reliable callback URLs** ✅
3. **Professional setup** ✅
4. **SSL secured** ✅
5. **Mobile app ready** ✅

Your production callback URLs will be stable and reliable! 🎉
