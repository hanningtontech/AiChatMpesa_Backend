# Google AI API Configuration Fix - CORRECTED

## Problem
The M-Pesa AI backend was throwing a Pydantic validation error:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for LlmAgent
api_key
  Extra inputs are not permitted [type=extra_forbidden, input_value=None, input_type=NoneType]
```

## Root Cause Analysis
The issue was that the Google ADK Agent class does **NOT** accept `api_key` as a direct parameter in its constructor. According to the official Google ADK documentation, authentication should be handled via environment variables, not constructor parameters.

## Correct Solution

### 1. Remove api_key from Agent Constructor
The Agent should be initialized **without** the `api_key` parameter:

```python
root_agent = Agent(
    name="mpesa_payment_agent",
    model="gemini-2.0-flash",  # No api_key parameter here
    description=(...),
    instruction=(...),
    tools=[...]
)
```

### 2. Configure Environment Variables Properly
According to Google ADK documentation, set these environment variables in your `.env` file:

```env
# Google AI Configuration
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_google_api_key_here
```

**Important Notes:**
- Use `FALSE` (not `0`) for `GOOGLE_GENAI_USE_VERTEXAI`
- The ADK automatically loads the API key from the environment variable
- No need to pass it explicitly to the Agent constructor

## How to Apply the Fix

1. **Get your Google AI API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Generate an API key

2. **Update your .env file**:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. **Ensure the Agent is initialized correctly** (without api_key parameter):
   ```python
   root_agent = Agent(
       name="mpesa_payment_agent",
       model="gemini-2.0-flash",
       description=(...),
       instruction=(...),
       tools=[...]
   )
   ```

4. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Files Modified
- `app/mpesa_agent/agent.py` - Removed `api_key` parameter from Agent initialization
- `.env` - Updated with correct Google AI configuration format

## Expected Result
The Pydantic validation error should be resolved, and the server should start successfully with the agent properly authenticated via environment variables.

## Reference
- [Google ADK Models & Authentication Documentation](https://google.github.io/adk-docs/agents/models/)
- [Google AI Studio API Keys](https://aistudio.google.com/app/apikey)

