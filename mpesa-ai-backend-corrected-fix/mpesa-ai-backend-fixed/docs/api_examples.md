# AI M-Pesa Agent API Documentation

**Base URL**: `http://localhost:8000` (or your deployed server URL)

This API provides AI-powered M-Pesa payment processing through natural language commands. Perfect for mobile app integration.

## 🚀 Quick Start for Mobile Apps

### 1. Health Check
Check if the API is running and the AI agent is available.

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00",
  "database": "sqlite:///./mpesa_sessions.db",
  "agent_available": true
}
```

### 2. Create a Session
Create a new conversation session for a user. Each user should have their own session.

**Endpoint**: `POST /sessions`

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "app_name": "mpesa_agent"
  }'
```

**Request Body**:
```json
{
  "user_id": "user_12345",        // Required: Unique identifier for your user
  "app_name": "mpesa_agent",      // Optional: Default is "mpesa_agent"
  "session_id": "custom_id",      // Optional: Auto-generated if not provided
  "state": {}                     // Optional: Initial session state
}
```

**Response**:
```json
{
  "id": "session_abc123",
  "app_name": "mpesa_agent",
  "user_id": "user_12345",
  "state": {
    "created_at": "2025-01-15T10:30:00",
    "mpesa_agent": {
      "status": "active",
      "conversation_history": []
    }
  },
  "events": [],
  "last_update_time": 1705312200.0
}
```

### 3. Send Message to AI Agent (Main Endpoint)
This is the primary endpoint your mobile app will use to send payment commands and get AI responses.

**Endpoint**: `POST /run`

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "session_id": "session_abc123",
    "app_name": "mpesa_agent",
    "message": "Send 500 KSh to 0712345678 for lunch"
  }'
```

**Request Body**:
```json
{
  "user_id": "user_12345",           // Required: Same as session creation
  "session_id": "session_abc123",    // Required: From session creation response
  "app_name": "mpesa_agent",         // Optional: Default is "mpesa_agent"
  "message": "Send 500 to John"      // Required: Natural language command
}
```

**Response**:
```json
{
  "events": [
    {
      "id": "event_123",
      "author": "mpesa_payment_agent",
      "timestamp": 1705312200.0,
      "turn_complete": true,
      "content": {
        "role": "model",
        "parts": [
          {
            "text": "I'll help you send 500 KSh to 0712345678 for lunch right away!\n📱 Initiating M-Pesa payment...\n✅ STK push sent successfully! Transaction ID: ABC123XYZ"
          }
        ]
      }
    }
  ]
}
```

## 📱 Mobile App Integration Examples

### Example Payment Commands
The AI agent understands natural language. Here are examples your users can send:

```json
// Simple payment
{
  "message": "Send 1000 to 0722123456"
}

// Payment with description
{
  "message": "Send 500 KSh to 0712345678 for lunch"
}

// Check balance
{
  "message": "What's my M-Pesa balance?"
}

// Check transaction status
{
  "message": "Check status of transaction ABC123"
}

// Payment to business
{
  "message": "Pay 2000 to till number 123456 for shopping"
}
```

### Typical Mobile App Flow

1. **App Startup**: Check API health
2. **User Login**: Create session with user ID
3. **User Input**: Send natural language command to `/run`
4. **Display Response**: Show AI response to user
5. **Session Persistence**: Reuse same session for conversation context

## 🔧 Session Management Endpoints

### Get Session Details
```bash
curl "http://localhost:8000/sessions/session_abc123?user_id=user_12345&app_name=mpesa_agent"
```

### List All Sessions for User
```bash
curl "http://localhost:8000/sessions?user_id=user_12345&app_name=mpesa_agent"
```

### Delete Session
```bash
curl -X DELETE "http://localhost:8000/sessions/session_abc123?user_id=user_12345&app_name=mpesa_agent"
```

## 🛡️ Error Handling

### Common HTTP Status Codes
- `200`: Success
- `404`: Session not found
- `422`: Validation error (invalid request body)
- `500`: Internal server error

### Error Response Format
```json
{
  "detail": "Session not found"
}
```

### Handling API Errors in Mobile Apps
```javascript
// Example in JavaScript/React Native
try {
  const response = await fetch('http://localhost:8000/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: 'user_12345',
      session_id: 'session_abc123',
      message: 'Send 500 to 0712345678'
    })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.detail);
    return;
  }

  const data = await response.json();
  // Process successful response
  const aiResponse = data.events[0]?.content?.parts[0]?.text;
  console.log('AI Response:', aiResponse);

} catch (error) {
  console.error('Network Error:', error);
}
```

## 📊 Response Processing

### Extracting AI Response Text
The AI response is nested in the events array. Here's how to extract it:

```javascript
function extractAIResponse(apiResponse) {
  if (apiResponse.events && apiResponse.events.length > 0) {
    const lastEvent = apiResponse.events[apiResponse.events.length - 1];
    if (lastEvent.content && lastEvent.content.parts && lastEvent.content.parts.length > 0) {
      return lastEvent.content.parts[0].text;
    }
  }
  return "No response received";
}
```

### Detecting Payment Success
Look for these keywords in the AI response:
- "✅ STK push sent successfully"
- "Transaction ID:"
- "Payment initiated"
- "Check your phone"

### Detecting Errors
Look for these keywords:
- "❌ Error"
- "Failed to"
- "Invalid phone number"
- "Insufficient balance"

## 🔄 Session Management Best Practices

### For Mobile Apps:
1. **Create one session per user** when they first use the payment feature
2. **Reuse the same session** for all conversations with that user
3. **Store session_id locally** (SharedPreferences/UserDefaults)
4. **Create new session** only if the stored one becomes invalid
5. **Include user context** in session creation (user_id should be unique per user)

### Session Lifecycle:
```
App Install → Create Session → Store Session ID → Use for All Payments
     ↓
User Logout → Delete Session → Clear Stored Session ID
     ↓
User Login → Create New Session → Store New Session ID
```

## 🚀 Production Deployment

### Environment Variables Required:
```env
# M-Pesa Configuration
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_BUSINESS_SHORT_CODE=your_shortcode
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://your-domain.com/mpesa/callback
MPESA_ENVIRONMENT=production

# Google AI
GOOGLE_API_KEY=your_google_api_key
```

### CORS Configuration
The API is configured to accept requests from any origin (`allow_origins=["*"]`). For production, restrict this to your mobile app's domain.

### Rate Limiting
Consider implementing rate limiting for production use to prevent abuse.

## 📱 Mobile SDK Examples

### React Native Example
```javascript
class MpesaAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
    this.userId = null;
  }

  async createSession(userId) {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        app_name: 'mpesa_agent'
      })
    });

    const data = await response.json();
    this.sessionId = data.id;
    this.userId = userId;
    return data;
  }

  async sendPaymentCommand(message) {
    if (!this.sessionId || !this.userId) {
      throw new Error('Session not initialized. Call createSession first.');
    }

    const response = await fetch(`${this.baseUrl}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: this.userId,
        session_id: this.sessionId,
        app_name: 'mpesa_agent',
        message: message
      })
    });

    const data = await response.json();
    return this.extractResponse(data);
  }

  extractResponse(apiResponse) {
    if (apiResponse.events && apiResponse.events.length > 0) {
      const lastEvent = apiResponse.events[apiResponse.events.length - 1];
      if (lastEvent.content && lastEvent.content.parts && lastEvent.content.parts.length > 0) {
        return lastEvent.content.parts[0].text;
      }
    }
    return "No response received";
  }
}

// Usage
const mpesa = new MpesaAPI('https://your-api-domain.com');
await mpesa.createSession('user_12345');
const response = await mpesa.sendPaymentCommand('Send 1000 to 0722123456');
console.log(response);
```

### Flutter/Dart Example
```dart
class MpesaAPI {
  final String baseUrl;
  String? sessionId;
  String? userId;

  MpesaAPI({this.baseUrl = 'http://localhost:8000'});

  Future<Map<String, dynamic>> createSession(String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/sessions'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'app_name': 'mpesa_agent',
      }),
    );

    final data = jsonDecode(response.body);
    this.sessionId = data['id'];
    this.userId = userId;
    return data;
  }

  Future<String> sendPaymentCommand(String message) async {
    if (sessionId == null || userId == null) {
      throw Exception('Session not initialized. Call createSession first.');
    }

    final response = await http.post(
      Uri.parse('$baseUrl/run'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'session_id': sessionId,
        'app_name': 'mpesa_agent',
        'message': message,
      }),
    );

    final data = jsonDecode(response.body);
    return extractResponse(data);
  }

  String extractResponse(Map<String, dynamic> apiResponse) {
    final events = apiResponse['events'] as List?;
    if (events != null && events.isNotEmpty) {
      final lastEvent = events.last as Map<String, dynamic>;
      final content = lastEvent['content'] as Map<String, dynamic>?;
      if (content != null) {
        final parts = content['parts'] as List?;
        if (parts != null && parts.isNotEmpty) {
          final firstPart = parts.first as Map<String, dynamic>;
          return firstPart['text'] as String? ?? 'No response received';
        }
      }
    }
    return 'No response received';
  }
}
```

## 🎯 Summary for Mobile Developers

**Essential Endpoints:**
1. `GET /health` - Check API status
2. `POST /sessions` - Create user session (once per user)
3. `POST /run` - Send payment commands (main endpoint)

**Key Points:**
- Use natural language for payment commands
- One session per user, reuse across app usage
- Extract AI response from `events[].content.parts[].text`
- Handle errors gracefully with try-catch
- Store session_id locally for persistence

**Ready to integrate!** 🚀

## 6. Delete Session
```bash
curl -X DELETE "http://localhost:8000/sessions/{session_id}?user_id=test_user&app_name=mpesa_agent"
```

## Running Options

### CLI Mode
```bash
python app/main.py cli
```

### Server Mode (default)
```bash
python app/main.py
```

The server will start on http://localhost:8000 with auto-reload enabled.
