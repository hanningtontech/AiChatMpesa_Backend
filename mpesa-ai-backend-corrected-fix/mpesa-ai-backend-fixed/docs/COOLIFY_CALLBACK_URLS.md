# 🌐 Getting Callback URLs from Coolify

**How to get your M-Pesa callback URL after deploying to Coolify**

## 🎯 The Simple Answer

When you deploy to Coolify, it automatically gives you URLs. Your callback URL will be:

```
https://your-app-name-5455.your-coolify-instance.com/mpesa/callback
```

## 📋 Step-by-Step Process

### Step 1: Deploy to Coolify
1. Create new project in Coolify
2. Choose "Docker Compose"
3. Connect your Git repository
4. Deploy

### Step 2: Find Your URLs
After deployment, Coolify shows you:

```
✅ Service URLs:
   - Port 8000: https://your-app-name-8000.coolify-instance.com
   - Port 5455: https://your-app-name-5455.coolify-instance.com
```

### Step 3: Build Your Callback URL
Your M-Pesa callback URL is:
```
https://your-app-name-5455.coolify-instance.com/mpesa/callback
```

## 🔧 Real Example

Let's say:
- **App name**: `mpesa-backend`
- **Coolify instance**: `app.coolify.io`

**Coolify gives you**:
- AI Agent API: `https://mpesa-backend-8000.app.coolify.io`
- Webhook Server: `https://mpesa-backend-5455.app.coolify.io`

**Your callback URLs**:
- M-Pesa: `https://mpesa-backend-5455.app.coolify.io/mpesa/callback`
- WhatsApp: `https://mpesa-backend-5455.app.coolify.io/whatsapp/webhook`

## ⚙️ Configure in Coolify

### Option 1: Environment Variables
In Coolify dashboard, add:
```env
MPESA_CALLBACK_URL=https://mpesa-backend-5455.app.coolify.io/mpesa/callback
```

### Option 2: Use the Helper Script
```bash
# After deployment, run:
python scripts/get_callback_urls.py mpesa-backend app.coolify.io
```

## 🎯 What You Need to Update

### 1. Coolify Environment Variables
```env
MPESA_CALLBACK_URL=https://your-app-name-5455.coolify-instance.com/mpesa/callback
```

### 2. Safaricom Developer Portal
Update your M-Pesa app with:
```
https://your-app-name-5455.coolify-instance.com/mpesa/callback
```

### 3. Twilio Console (if using WhatsApp)
Update webhook URL to:
```
https://your-app-name-5455.coolify-instance.com/whatsapp/webhook
```

### 4. Mobile App
Update API base URL to:
```
https://your-app-name-8000.coolify-instance.com
```

## 🌐 Custom Domain Option

If you want cleaner URLs:

### Step 1: Add Custom Domain in Coolify
- `api.yourdomain.com` → Port 8000
- `webhooks.yourdomain.com` → Port 5455

### Step 2: Your URLs Become
- M-Pesa: `https://webhooks.yourdomain.com/mpesa/callback`
- WhatsApp: `https://webhooks.yourdomain.com/whatsapp/webhook`
- API: `https://api.yourdomain.com`

## 🧪 Testing Your URLs

### Test if URLs are working:
```bash
# Test AI Agent API
curl https://your-app-name-8000.coolify-instance.com/health

# Test Webhook Server
curl https://your-app-name-5455.coolify-instance.com/whatsapp/test

# Test M-Pesa callback (should return 200)
curl -X POST https://your-app-name-5455.coolify-instance.com/mpesa/callback \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 🚀 Quick Setup Checklist

- [ ] Deploy to Coolify
- [ ] Note the URLs Coolify provides
- [ ] Build callback URL: `webhook-url/mpesa/callback`
- [ ] Update MPESA_CALLBACK_URL in Coolify
- [ ] Update Safaricom portal
- [ ] Update Twilio (if using WhatsApp)
- [ ] Test all endpoints
- [ ] Update mobile app with API URL

## 💡 Pro Tips

1. **Write down your URLs** immediately after deployment
2. **Test endpoints** before updating external services
3. **Use the helper script** to generate all URLs at once
4. **Keep URLs consistent** - don't change app names frequently

## 🆘 If You're Confused

Run this helper script after deployment:
```bash
python scripts/get_callback_urls.py
```

It will walk you through getting your callback URLs step by step!

**The key point**: Coolify automatically gives you HTTPS URLs when you deploy. You just need to add `/mpesa/callback` to the webhook server URL! 🎯
