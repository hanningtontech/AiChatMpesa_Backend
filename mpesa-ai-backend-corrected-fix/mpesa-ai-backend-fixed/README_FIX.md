# Google AI API Configuration Fix

## Problem
The M-Pesa AI backend was throwing a 500 Internal Server Error with the message:
```
Missing key inputs argument! To use the Google AI API, provide (`api_key`) arguments. To use the Google Cloud API, provide (`vertexai`, `project` & `location`) arguments.
```

## Root Cause
The Google AI Agent was being initialized without the required `api_key` parameter. The Agent constructor in `app/mpesa_agent/agent.py` was missing the API key configuration.

## Solution
1. **Fixed Agent Initialization**: Added the `api_key` parameter to the Agent constructor in `app/mpesa_agent/agent.py`:
   ```python
   root_agent = Agent(
       name="mpesa_payment_agent",
       model="gemini-2.0-flash",
       api_key=os.getenv("GOOGLE_API_KEY"),  # Added this line
       description=(...),
       instruction=(...),
       tools=[...]
   )
   ```

2. **Environment Configuration**: Created a proper `.env` file with the correct Google AI API configuration:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=0
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## How to Use the Fix

1. **Set up your Google AI API Key**:
   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Replace `your_google_api_key_here` in the `.env` file with your actual API key

2. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app/main.py
   ```

The server should now start without the Google AI API configuration error.

## Files Modified
- `app/mpesa_agent/agent.py` - Added `api_key` parameter to Agent initialization
- `.env` - Created with proper Google AI API configuration

## Testing
After applying this fix, the FastAPI server should start successfully and the `/health` endpoint should show `"agent_available": true`.

