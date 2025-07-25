# 📱 Mobile App API Integration Guide

**AI M-Pesa Payment Agent API for Mobile Applications**

## 🚀 Quick Integration

**Base URL**: `http://your-server:8000`

### Step 1: Check API Health
```http
GET /health
```

### Step 2: Create User Session (Once per user)
```http
POST /sessions
Content-Type: application/json

{
  "user_id": "unique_user_id",
  "app_name": "mpesa_agent"
}
```

**Response**: Save the `id` field as your `session_id`

### Step 3: Send Payment Commands (Main Endpoint)
```http
POST /run
Content-Type: application/json

{
  "user_id": "unique_user_id",
  "session_id": "saved_session_id",
  "message": "Send 1000 KSh to 0722123456 for rent"
}
```

**Response**: Extract AI response from `events[0].content.parts[0].text`

## 💬 Natural Language Commands

Your users can send commands like:
- `"Send 500 to 0712345678"`
- `"Send 1000 KSh to John for lunch"`
- `"What's my M-Pesa balance?"`
- `"Check transaction status ABC123"`
- `"Pay 2000 to till 123456"`

## 📱 Mobile SDK Template

### JavaScript/React Native
```javascript
class MpesaAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.sessionId = null;
    this.userId = null;
  }

  async init(userId) {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, app_name: 'mpesa_agent' })
    });
    const data = await response.json();
    this.sessionId = data.id;
    this.userId = userId;
  }

  async sendCommand(message) {
    const response = await fetch(`${this.baseUrl}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: this.userId,
        session_id: this.sessionId,
        message: message
      })
    });
    const data = await response.json();
    return data.events[0]?.content?.parts[0]?.text || 'No response';
  }
}

// Usage
const api = new MpesaAPI('https://your-api-url.com');
await api.init('user123');
const response = await api.sendCommand('Send 500 to 0722123456');
```

### Flutter/Dart
```dart
class MpesaAPI {
  final String baseUrl;
  String? sessionId;
  String? userId;

  MpesaAPI(this.baseUrl);

  Future<void> init(String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/sessions'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'app_name': 'mpesa_agent'}),
    );
    final data = jsonDecode(response.body);
    sessionId = data['id'];
    this.userId = userId;
  }

  Future<String> sendCommand(String message) async {
    final response = await http.post(
      Uri.parse('$baseUrl/run'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'session_id': sessionId,
        'message': message,
      }),
    );
    final data = jsonDecode(response.body);
    return data['events'][0]['content']['parts'][0]['text'] ?? 'No response';
  }
}
```

## ✅ Success Indicators

Look for these in AI responses:
- `"✅ STK push sent successfully"`
- `"Transaction ID:"`
- `"Payment initiated"`

## ❌ Error Indicators

Look for these in AI responses:
- `"❌ Error"`
- `"Invalid phone number"`
- `"Failed to"`

## 🔄 Session Management

- **Create once** per user login
- **Reuse** session for all payments
- **Store** session_id locally
- **Recreate** only if session becomes invalid

## 🛡️ Error Handling

```javascript
try {
  const response = await api.sendCommand(message);
  if (response.includes('✅')) {
    // Success
    showSuccess(response);
  } else if (response.includes('❌')) {
    // Error
    showError(response);
  } else {
    // Normal response
    showResponse(response);
  }
} catch (error) {
  showNetworkError('Connection failed');
}
```

## 🌐 Production Setup

1. **Deploy API** to your server
2. **Update Base URL** in your mobile app
3. **Configure M-Pesa credentials** in server environment
4. **Test** with sandbox first
5. **Switch to production** M-Pesa environment

## 📞 Support

- API runs on port 8000
- Interactive docs at `/docs`
- Health check at `/health`
- All endpoints support CORS

**Ready to integrate!** 🚀
