# 🚀 Separate Services Deployment Guide

## 📋 **Overview**

We've created separate Docker services for better control and flexibility:

1. **AI Agent API** - Handles intelligent M-Pesa agent responses
2. **Webhook Server** - Handles M-Pesa callbacks and WhatsApp webhooks

## 🏗️ **New Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                        Coolify                              │
├─────────────────────────────────────────────────────────────┤
│  🤖 AI Agent Service                                        │
│  ├── Domain: mpesa-ai.cecilgachie.tech                     │
│  ├── Port: 3343                                            │
│  ├── Endpoints: /health, /chat, /sessions                  │
│  └── Dockerfile: Dockerfile.agent                          │
├─────────────────────────────────────────────────────────────┤
│  📱 Webhook Service                                         │
│  ├── Domain: webhook.cecilgachie.tech                      │
│  ├── Port: 3344                                            │
│  ├── Endpoints: /mpesa/callback, /whatsapp/webhook         │
│  └── Dockerfile: Dockerfile.webhook                        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **New Files Created**

### **1. Dockerfile.agent**
- Dedicated to AI Agent API
- Runs on port 3343
- Starts with: `python app/main.py`

### **2. Dockerfile.webhook** 
- Dedicated to Webhook Server
- Runs on port 3344
- Starts with: `python callback_server.py`

### **3. docker-compose.separate.yml**
- Defines both services
- Shared volume for database
- Proper service dependencies

## 🔧 **Deployment Steps**

### **Step 1: Replace docker-compose.yml**
```bash
# Backup current file
mv docker-compose.yml docker-compose.old.yml

# Use the new separate services configuration
mv docker-compose.separate.yml docker-compose.yml
```

### **Step 2: Deploy to Coolify**
1. **Commit and push changes**
2. **Coolify will auto-deploy**
3. **You'll get TWO separate applications in Coolify**

### **Step 3: Configure Domains in Coolify**

#### **AI Agent Service:**
- **Service Name**: `ai-agent`
- **Domain**: `mpesa-ai.cecilgachie.tech`
- **Port**: `3343`
- **Health Check**: `/health`

#### **Webhook Service:**
- **Service Name**: `webhook-server`  
- **Domain**: `webhook.cecilgachie.tech` (or subdomain of your choice)
- **Port**: `3344`
- **Health Check**: `/health`

## 🎯 **Expected URLs**

### **AI Agent API:**
- **Main**: `https://mpesa-ai.cecilgachie.tech/`
- **Health**: `https://mpesa-ai.cecilgachie.tech/health`
- **Chat**: `https://mpesa-ai.cecilgachie.tech/chat`

### **Webhook Server:**
- **Main**: `https://webhook.cecilgachie.tech/`
- **Health**: `https://webhook.cecilgachie.tech/health`
- **M-Pesa Callback**: `https://webhook.cecilgachie.tech/mpesa/callback`
- **WhatsApp Webhook**: `https://webhook.cecilgachie.tech/whatsapp/webhook`

## 🔄 **Environment Variables**

Update your `.env` file with the new URLs:
```env
# Webhook URLs
MPESA_CALLBACK_URL=https://webhook.cecilgachie.tech/mpesa/callback
WHATSAPP_WEBHOOK_URL=https://webhook.cecilgachie.tech/whatsapp/webhook

# AI Agent URL (for webhook server to communicate)
AI_AGENT_URL=https://mpesa-ai.cecilgachie.tech
```

## ✅ **Benefits**

1. **Independent Scaling** - Scale each service separately
2. **Better Monitoring** - Separate logs and metrics
3. **Easier Debugging** - Isolate issues to specific services
4. **Flexible Domains** - Use different subdomains/domains
5. **Coolify Compatibility** - Each service gets its own configuration

## 🚀 **Ready to Deploy!**

Run these commands to deploy:
```bash
mv docker-compose.yml docker-compose.old.yml
mv docker-compose.separate.yml docker-compose.yml
git add .
git commit -m "Separate AI Agent and Webhook services for better Coolify management"
git push origin main
```

Coolify will automatically deploy both services! 🎉
