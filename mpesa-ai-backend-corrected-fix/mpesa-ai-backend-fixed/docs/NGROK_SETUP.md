# 🚀 ngrok Setup Guide for M-Pesa Callbacks

## What You Need to Do

### **Step 1: Get ngrok Auth Token (Optional but Recommended)**

1. **Sign up at ngrok:** https://dashboard.ngrok.com/signup
2. **Get your auth token** from the dashboard
3. **Configure ngrok** with your token:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
   ```

### **Step 2: Start the Callback Server**

**Option A: Use the automated script (Recommended)**
```bash
./start_callback_server.sh
```

**Option B: Manual setup**
```bash
# Terminal 1: Start the callback server
source env/bin/activate
python callback_server.py

# Terminal 2: Start ngrok (in a new terminal)
ngrok http 8000
```

### **Step 3: Get Your Callback URL**

When ngrok starts, you'll see something like:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Your callback URL is:** `https://abc123.ngrok.io/mpesa/callback`

### **Step 4: Update Your .env File**

Copy the ngrok URL and update your `.env`:
```env
MPESA_CALLBACK_URL=https://abc123.ngrok.io/mpesa/callback
```

### **Step 5: Test Your Setup**

1. **Test the server:** Visit `https://abc123.ngrok.io` in your browser
2. **Test M-Pesa integration:**
   ```bash
   source env/bin/activate
   python test_mpesa.py
   ```

## 📋 **What Each Component Does**

### **callback_server.py**
- Receives M-Pesa payment notifications
- Logs all callbacks to `logs/` directory
- Provides web interface to view logs
- Handles both success and timeout callbacks

### **ngrok**
- Creates a secure tunnel from internet to your local server
- Gives you a public URL that M-Pesa can reach
- Handles HTTPS automatically (required by M-Pesa)

## 🔍 **Monitoring Your Callbacks**

### **View Logs in Browser**
- **Home page:** `https://abc123.ngrok.io`
- **Recent logs:** `https://abc123.ngrok.io/logs`
- **Health check:** `https://abc123.ngrok.io/health`

### **View Logs in Terminal**
```bash
# Watch logs in real-time
tail -f logs/mpesa_callbacks_$(date +%Y-%m-%d).json

# View formatted logs
cat logs/mpesa_callbacks_$(date +%Y-%m-%d).json | jq .
```

### **ngrok Web Interface**
Visit `http://127.0.0.1:4040` to see:
- Request/response details
- Traffic inspection
- Replay requests

## 🛠️ **Troubleshooting**

### **"ngrok not found"**
```bash
# Install ngrok if not already installed
sudo apt update && sudo apt install ngrok
```

### **"Port 8000 already in use"**
```bash
# Kill any process using port 8000
sudo lsof -ti:8000 | xargs kill -9
```

### **"Connection refused"**
- Make sure the callback server is running first
- Check that you're using the correct port (8000)

### **"Invalid callback URL"**
- Ensure your ngrok URL includes `/mpesa/callback` at the end
- Use HTTPS URL (ngrok provides this automatically)

## 🔄 **Complete Workflow**

1. **Start servers:** `./start_callback_server.sh`
2. **Copy ngrok URL** from terminal output
3. **Update .env** with the callback URL
4. **Test M-Pesa:** `python test_mpesa.py`
5. **Check logs** at `https://your-ngrok-url.ngrok.io/logs`

## 💡 **Pro Tips**

- **Keep ngrok running** while testing M-Pesa
- **The ngrok URL changes** each time you restart (unless you have a paid plan)
- **Always update .env** when you get a new ngrok URL
- **Check the logs** to see what M-Pesa is sending you

## 🎯 **Next Steps**

Once this is working:
1. Test STK Push payments
2. Verify callbacks are received
3. Integrate with your AI agent
4. Add WhatsApp integration
