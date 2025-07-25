
import asyncio
import json
import os
import sys
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# Firebase Admin SDK imports
import firebase_admin
from firebase_admin import credentials, firestore

# Import the mpesa agent
try:
    # Add the parent directory to sys.path to handle relative imports
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.sys.path.insert(0, str(parent_dir))

    from app.mpesa_agent.agent import root_agent
    print("✅ Mpesa agent imported successfully!")
except ImportError as e:
    print(f"Warning: Could not import mpesa agent: {e}")
    root_agent = None

load_dotenv()

# Setup logging - quiet for CLI, normal for server
def setup_logging(quiet_mode=False):
    if quiet_mode:
        # Suppress all logging except critical errors
        logging.basicConfig(level=logging.CRITICAL)
        # Specifically silence the noisy loggers
        logging.getLogger("google_adk").setLevel(logging.CRITICAL)
        logging.getLogger("google_genai").setLevel(logging.CRITICAL)
        logging.getLogger("google.adk").setLevel(logging.CRITICAL)
    else:
        logging.basicConfig(level=logging.INFO)

    return logging.getLogger(__name__)

# Use SQLite database for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mpesa_sessions.db")

# Initialize logger (will be reconfigured in CLI mode)
logger = setup_logging(quiet_mode=False)

# Initialize session service
session_service = DatabaseSessionService(db_url=DATABASE_URL)

# Initialize Firebase Admin SDK (do this once at startup)
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH", "serviceAccountKey.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Helper function to fetch user data by ID
async def get_user_by_id(user_id: str):
    users_ref = db.collection("users")
    doc = await asyncio.to_thread(lambda: users_ref.document(user_id).get())
    if doc.exists:
        return doc.to_dict()
    return None

# Create FastAPI app
app = FastAPI(title="Mpesa AI Agent API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SessionCreateRequest(BaseModel):
    app_name: str = "mpesa_agent"
    user_id: str
    session_id: Optional[str] = None
    state: Optional[Dict[str, Any]] = None

class AgentRunRequest(BaseModel):
    app_name: str = "mpesa_agent"
    user_id: str
    session_id: str
    message: str

class SessionResponse(BaseModel):
    id: str
    app_name: str
    user_id: str
    state: Dict[str, Any]
    events: List[Dict[str, Any]]
    last_update_time: float

def create_initial_state(**kwargs) -> Dict[str, Any]:
    """Create initial state for a new session with custom parameters."""
    return {
        "created_at": datetime.now().isoformat(),
        "mpesa_agent": {
            "status": "active",
            "conversation_history": []
        },
        **kwargs
    }


# Session management endpoints
@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new session."""
    try:
        # Check if session_id is provided and if it already exists
        if request.session_id:
            existing_session = await session_service.get_session(
                app_name=request.app_name,
                user_id=request.user_id,
                session_id=request.session_id,
            )
            if existing_session:
                logger.info(f"Session {request.session_id} already exists for user {request.user_id}. Returning existing session.")
                return SessionResponse(
                    id=existing_session.id,
                    app_name=existing_session.app_name,
                    user_id=existing_session.user_id,
                    state=existing_session.state,
                    events=[event.__dict__ for event in existing_session.events],
                    last_update_time=existing_session.last_update_time
                )

        session_id = request.session_id or str(uuid.uuid4())
        initial_state = create_initial_state(**(request.state or {}))

        session = await session_service.create_session(
            app_name=request.app_name,
            user_id=request.user_id,
            session_id=session_id,
            state=initial_state,
        )

        logger.info(f"Created session {session_id} for user {request.user_id}")

        return SessionResponse(
            id=session.id,
            app_name=session.app_name,
            user_id=session.user_id,
            state=session.state,
            events=[event.__dict__ for event in session.events],
            last_update_time=session.last_update_time
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}", response_model=SessionResponse)
async def create_session_with_id(
    app_name: str,
    user_id: str,
    session_id: str,
    state: Optional[Dict[str, Any]] = None,
):
    """Create a new session with a specified ID."""
    try:
        # Check if session already exists
        existing_session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if existing_session:
            logger.info(f"Session {session_id} already exists for user {user_id}. Returning existing session.")
            return SessionResponse(
                id=existing_session.id,
                app_name=existing_session.app_name,
                user_id=existing_session.user_id,
                state=existing_session.state,
                events=[event.__dict__ for event in existing_session.events],
                last_update_time=existing_session.last_update_time
            )

        initial_state = create_initial_state(**(state or {}))
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state,
        )

        logger.info(f"Created session {session_id} for user {user_id}")

        return SessionResponse(
            id=session.id,
            app_name=session.app_name,
            user_id=session.user_id,
            state=session.state,
            events=[event.__dict__ for event in session.events],
            last_update_time=session.last_update_time
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, app_name: str = "mpesa_agent", user_id: str = "default"):
    """Get a session by ID."""
    try:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            id=session.id,
            app_name=session.app_name,
            user_id=session.user_id,
            state=session.state,
            events=[event.__dict__ for event in session.events],
            last_update_time=session.last_update_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.get("/apps/{app_name}/users/{user_id}/sessions/{session_id}", response_model=SessionResponse)
async def get_session_with_id(
    app_name: str,
    user_id: str,
    session_id: str,
):
    """Get a session with a specified ID."""
    try:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            id=session.id,
            app_name=session.app_name,
            user_id=session.user_id,
            state=session.state,
            events=[event.__dict__ for event in session.events],
            last_update_time=session.last_update_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str, app_name: str = "mpesa_agent", user_id: str = "default"):
    """Delete a session by ID."""
    try:
        await session_service.delete_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        logger.info(f"Deleted session {session_id}")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def delete_session_with_id(
    app_name: str,
    user_id: str,
    session_id: str,
):
    """Delete a session with a specified ID."""
    try:
        await session_service.delete_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        logger.info(f"Deleted session {session_id} for user {user_id}")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@app.get("/sessions")
async def list_sessions(app_name: str = "mpesa_agent", user_id: str = "default"):
    """List all sessions for a user."""
    try:
        sessions_list = await session_service.list_sessions(app_name=app_name, user_id=user_id)

        return {
            "sessions": [
                SessionResponse(
                    id=session.id,
                    app_name=session.app_name,
                    user_id=session.user_id,
                    state=session.state,
                    events=[event.__dict__ for event in session.events],
                    last_update_time=session.last_update_time
                ).dict()
                for session in sessions_list.sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.get("/apps/{app_name}/users/{user_id}/sessions")
async def list_sessions_for_user(app_name: str, user_id: str):
    """List all sessions for a user."""
    try:
        sessions_list = await session_service.list_sessions(app_name=app_name, user_id=user_id)

        return {
            "sessions": [
                SessionResponse(
                    id=session.id,
                    app_name=session.app_name,
                    user_id=session.user_id,
                    state=session.state,
                    events=[event.__dict__ for event in session.events],
                    last_update_time=session.last_update_time
                ).dict()
                for session in sessions_list.sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


# Agent interaction endpoints
@app.post("/run")
async def agent_run(request: AgentRunRequest):
    """Run agent with a message and return response."""
    try:
        logger.info(f"Running agent for session {request.session_id} with message: {request.message}")

        if root_agent is None:
            # Simple echo response if no agent is available
            return {
                "response": f"Echo: {request.message}",
                "session_id": request.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Fetch user data from Firestore (assume user_id is the document ID)
        user_data = await get_user_by_id(request.user_id)
        if not user_data:
            logger.error(f"User not found in Firestore: {request.user_id}")
            raise HTTPException(status_code=404, detail="User not found in Firestore")
        sender_phone_number = user_data.get("phoneNumber")
        user_email = user_data.get("email")

        # Create runner
        runner = Runner(
            app_name=request.app_name,
            agent=root_agent,
            session_service=session_service,
        )

        # Convert message to Content
        content = types.Content(
            role="user",
            parts=[types.Part(text=request.message)]
        )

        # Store user data in session state before running agent
        session = await session_service.get_session(
            app_name=request.app_name,
            user_id=request.user_id,
            session_id=request.session_id,
        )
        
        if session:
            # Update session state with user profile data
            session.state["user_profile"] = {
                "phoneNumber": sender_phone_number,
                "email": user_email
            }
            # Check if update_session exists before calling it
            if hasattr(session_service, 'update_session'):
                await session_service.update_session(session)
            else:
                logger.warning("session_service does not have update_session method. Skipping session state update.")

        events = []
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=content
        ):
            event_dict = {
                "author": event.author,
                "timestamp": event.timestamp,
                "turn_complete": getattr(event, "turn_complete", False),
                "content": None
            }

            # Handle content
            if event.content and event.content.parts:
                parts = []
                for part in event.content.parts:
                    part_dict = {}
                    if hasattr(part, "text") and part.text:
                        # Escape double quotes within the text to prevent JSON parsing errors on Android
                        part_dict["text"] = part.text.replace("\"", "\\\"")
                    # Add other attributes of "part" to part_dict if necessary
                    parts.append(part_dict)
                event_dict["content"] = {
                    "role": event.content.role,
                    "parts": parts
                }

            events.append(event_dict)

        logger.info(f"Agent run completed with {len(events)} events")
        return {"events": events}

    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run agent: {str(e)}")


# CLI functionality
async def main_async():
    """CLI interface for interacting with the Mpesa Agent."""
    APP_NAME = "mpesa_agent"
    USER_ID = "cli_user"

    # Setup quiet logging for CLI
    logger = setup_logging(quiet_mode=True)

    print("\n" + "🚀 Mpesa Agent CLI".center(60))
    print("=" * 60)
    print("💰 Your AI-powered M-Pesa assistant".center(60))
    print("=" * 60)

    # Check for existing sessions for this user
    try:
        existing_sessions = await session_service.list_sessions(
            app_name=APP_NAME,
            user_id=USER_ID,
        )

        # If there's an existing session, use it, otherwise create a new one
        if existing_sessions and len(existing_sessions.sessions) > 0:
            # Use the most recent session
            SESSION_ID = existing_sessions.sessions[0].id
            print(f"\n📋 Continuing existing session")
            print(f"   Session ID: {SESSION_ID[:8]}...")
        else:
            # Create a new session with initial state
            SESSION_ID = str(uuid.uuid4())
            initial_state = create_initial_state()
            new_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
                state=initial_state,
            )
            print(f"\n✨ Created new session")
            print(f"   Session ID: {SESSION_ID[:8]}...")

        print(f"\n{'Commands:'.center(60)}")
        print("─" * 60)
        print('💬 Just type your message to chat with the agent')
        print('📋 Type \'sessions\' to list all sessions')
        print('🆕 Type \'clear\' to create a new session')
        print('🚪 Type \'exit\' or \'quit\' to end')
        print("─" * 60)

        # Interactive conversation loop
        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ["exit", "quit"]:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == "sessions":
                    sessions_list = await session_service.list_sessions(app_name=APP_NAME, user_id=USER_ID)
                    print(f"\n📋 Session History ({len(sessions_list.sessions)} sessions)")
                    print("─" * 60)
                    for i, session in enumerate(sessions_list.sessions, 1):
                        session_id_short = session.id[:8] + "..."
                        created_at = session.state.get("created_at", "unknown")
                        if created_at != "unknown":
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                                created_at = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                pass
                        print(f"  {i:2d}. {session_id_short} (created: {created_at})")
                    print("─" * 60)
                    continue
                elif user_input.lower() == "clear":
                    SESSION_ID = str(uuid.uuid4())
                    initial_state = create_initial_state()
                    new_session = await session_service.create_session(
                        app_name=APP_NAME,
                        user_id=USER_ID,
                        session_id=SESSION_ID,
                        state=initial_state,
                    )
                    print(f"\n✨ New session created")
                    print(f"   Session ID: {SESSION_ID[:8]}...")
                    print("─" * 60)
                    continue
                elif not user_input:
                    continue

                # Process the message
                if root_agent is None:
                    print(f"🤖 Agent: Echo - {user_input}")
                else:
                    # Create runner and process message
                    runner = Runner(
                        app_name=APP_NAME,
                        agent=root_agent,
                        session_service=session_service,
                    )

                    content = types.Content(
                        role="user",
                        parts=[types.Part(text=user_input)]
                    )

                    print("\n🤖 Agent:")
                    print("─" * 60)

                    # Collect response and token info
                    response_text = ""
                    token_count = None

                    async for event in runner.run_async(
                        user_id=USER_ID,
                        session_id=SESSION_ID,
                        new_message=content
                    ):
                        # Only process model responses (not user messages)
                        if event.author == "mpesa_payment_agent" and event.content and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, "text") and part.text:
                                    response_text += part.text

                        # Extract token usage if available
                        if hasattr(event, "usage_metadata") and event.usage_metadata:
                            token_count = event.usage_metadata.total_token_count

                    # Print the clean response with nice formatting
                    if response_text.strip():
                        # Add some padding and clean formatting
                        lines = response_text.strip().split("\n")
                        for line in lines:
                            print(f"  {line}")

                    # Print token count in a beautiful format
                    print("─" * 60)
                    if token_count:
                        print(f"💡 Tokens: {token_count:,}")
                    print()  # Extra line for spacing

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        logger.error(f"CLI error: {e}")
        print(f"❌ Failed to start CLI: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": DATABASE_URL,
        "agent_available": root_agent is not None
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn

    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Run CLI mode
        asyncio.run(main_async())
    else:
        # Run FastAPI server with normal logging
        logger = setup_logging(quiet_mode=False)

        # Get port from environment variable or default to 8000
        port = int(os.getenv("PORT", 8000))

        print("\n🚀 Starting Mpesa Agent FastAPI Server")
        print("=" * 50)
        print(f"📊 Database: {DATABASE_URL}")
        print(f"🤖 Agent: {'✅ Available' if root_agent is not None else '❌ Not Available'}")
        print(f"🌐 Server: http://localhost:{port}")
        print(f"📚 Docs: http://localhost:{port}/docs")
        print("=" * 50)
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=True
        )



