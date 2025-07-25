import datetime
import requests
import time
import os
import asyncio
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .mpesa_tools import validate_phone_number, initiate_stk_push, check_transaction_status
from dotenv import load_dotenv

# Load environment variables
import pathlib
root_dir = pathlib.Path(__file__).parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

# Callback server configuration - read from environment
def get_callback_server_url():
    """Get callback server URL from environment or default"""
    # Try to extract from MPESA_CALLBACK_URL
    callback_url = os.getenv('MPESA_CALLBACK_URL', '')
    if callback_url:
        # Extract base URL from callback URL
        # e.g., https://abc123.ngrok.io/mpesa/callback -> https://abc123.ngrok.io
        if '/mpesa/callback' in callback_url:
            return callback_url.replace('/mpesa/callback', '')

    # Fallback to explicit callback server URL or localhost (port 5000 for unified server)
    return os.getenv('CALLBACK_SERVER_URL', 'http://localhost:5000')

CALLBACK_SERVER_URL = get_callback_server_url()

def check_payment_status_realtime(checkout_request_id: str) -> dict:
    """
    Checks the real-time status of an M-Pesa payment using callback integration.

    Args:
        checkout_request_id (str): The checkout request ID from the payment initiation

    Returns:
        dict: Real-time transaction status and details
    """
    try:
        # First try to get status from callback manager
        response = requests.get(f"{CALLBACK_SERVER_URL}/payment/status/{checkout_request_id}", timeout=10)

        if response.status_code == 200:
            result = response.json()

            if result.get('status') == 'found':
                payment_info = result.get('payment_info', {})
                payment_status = payment_info.get('status')

                if payment_status == 'success':
                    return {
                        "status": "success",
                        "message": "✅ Payment completed successfully",
                        "payment_status": "completed",
                        "payment_details": payment_info.get('payment_details', {}),
                        "completed_at": payment_info.get('completed_at'),
                        "real_time_data": True
                    }
                elif payment_status == 'failed':
                    return {
                        "status": "failed",
                        "message": f"❌ Payment failed: {payment_info.get('error_message', 'Unknown error')}",
                        "payment_status": "failed",
                        "error_message": payment_info.get('error_message'),
                        "real_time_data": True
                    }
                elif payment_status == 'pending':
                    return {
                        "status": "pending",
                        "message": "⏳ Payment is still pending - waiting for user to complete on phone",
                        "payment_status": "pending",
                        "initiated_at": payment_info.get('initiated_at'),
                        "real_time_data": True
                    }
                elif payment_status == 'timeout':
                    return {
                        "status": "timeout",
                        "message": "⏱️  Payment timed out - user may not have completed the transaction",
                        "payment_status": "timeout",
                        "real_time_data": True
                    }
            else:
                # Payment not found in callback manager, fall back to M-Pesa API
                return check_transaction_status(checkout_request_id)
        else:
            # Callback server not available, fall back to M-Pesa API
            return check_transaction_status(checkout_request_id)

    except Exception as e:
        print(f"⚠️  Error checking real-time status: {e}")
        # Fall back to M-Pesa API
        return check_transaction_status(checkout_request_id)

def send_instant_payment_with_tracking(phone_number: str, amount: float, wait_for_completion: bool = True) -> dict:
    """
    Sends an instant M-Pesa payment with real-time tracking and automatic status updates.
    This is the main function for frictionless payments with callback integration.

    Args:
        phone_number (str): The recipient's phone number (any format)
        amount (float): Amount to send in KSh
        wait_for_completion (bool): Whether to wait for payment completion

    Returns:
        dict: Payment result with real-time status and details
    """
    # Smart description inference based on context
    description = "AI Agent Payment"  # Default

    # Step 1: Initiate payment
    payment_result = initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        account_reference="AI Agent",
        transaction_desc=description
    )

    if payment_result.get('status') != 'success':
        return payment_result

    checkout_request_id = payment_result.get('checkout_request_id')

    if not checkout_request_id:
        return {
            "status": "error",
            "error_message": "No checkout request ID received from M-Pesa"
        }

    # Step 2: Register payment for tracking
    try:
        register_url = f"{CALLBACK_SERVER_URL}/payment/register"
        print(f"🔗 Registering payment at: {register_url}")

        register_response = requests.post(register_url,
            json={
                'checkout_request_id': checkout_request_id,
                'phone_number': phone_number,
                'amount': amount,
                'description': description
            },
            timeout=30
        )

        if register_response.status_code == 200:
            print(f"✅ Payment registered for tracking: {checkout_request_id}")
        else:
            print(f"⚠️  Failed to register payment for tracking: {register_response.status_code} - {register_response.text}")
    except Exception as e:
        print(f"⚠️  Could not register payment for tracking: {e}")
        print(f"   Callback server URL: {CALLBACK_SERVER_URL}")

    # Step 3: Wait for completion if requested
    if wait_for_completion:
        try:
            wait_url = f"{CALLBACK_SERVER_URL}/payment/wait/{checkout_request_id}?timeout=80"
            print(f"⏳ Waiting for payment completion at: {wait_url}")
            wait_response = requests.get(wait_url, timeout=85)

            if wait_response.status_code == 200:
                wait_result = wait_response.json()

                if wait_result.get('status') == 'completed':
                    payment_info = wait_result.get('payment_info', {})
                    payment_status = payment_info.get('status')

                    if payment_status == 'success':
                        return {
                            "status": "success",
                            "message": f"💰 Payment completed successfully! {amount} KSh sent to {phone_number}",
                            "checkout_request_id": checkout_request_id,
                            "payment_status": "completed",
                            "payment_details": payment_info.get('payment_details', {}),
                            "description": description,
                            "real_time_tracking": True
                        }
                    else:
                        return {
                            "status": "failed",
                            "message": f"❌ Payment failed: {payment_info.get('error_message', 'Unknown error')}",
                            "checkout_request_id": checkout_request_id,
                            "payment_status": "failed",
                            "description": description,
                            "real_time_tracking": True
                        }
                else:
                    return {
                        "status": "timeout",
                        "message": f"⏱️  Payment initiated but completion status unknown. Check manually with ID: {checkout_request_id}",
                        "checkout_request_id": checkout_request_id,
                        "payment_status": "pending",
                        "description": description,
                        "real_time_tracking": True
                    }
        except Exception as e:
            print(f"⚠️  Could not wait for payment completion: {e}")

    # Return immediate result if not waiting or if waiting failed
    return {
        "status": "initiated",
        "message": f"📱 Payment request sent to {phone_number} for {amount} KSh. User will receive STK push prompt.",
        "checkout_request_id": checkout_request_id,
        "payment_status": "pending",
        "description": description,
        "real_time_tracking": True,
        "note": "Payment completion will be tracked automatically"
    }




root_agent = Agent(
    name="mpesa_payment_agent",
    model="gemini-2.0-flash",
    description=(
        "Ultra-fast M-Pesa payment agent with REAL-TIME callback integration. "
        "Processes transactions instantly, waits for completion, and provides personalized responses with actual transaction details."
    ),
    instruction=(
        "You are a lightning-fast M-Pesa payment assistant with REAL-TIME payment tracking and ZERO friction.\n\n"

        "🔑 SENDER PHONE NUMBER: {session.state.user_profile.phoneNumber}\n"
        "This is the phone number that will receive the STK push for ALL payments.\n\n"

        "🚀 CORE BEHAVIOR WITH CALLBACK TRACKING:\n"
        "- When a user mentions sending money, use send_instant_payment_with_tracking()\n"
        "- CRITICAL: ALWAYS use session.state.user_profile.phoneNumber for the phone_number parameter\n"
        "- NEVER use any recipient number mentioned in the message - M-Pesa charges the sender's account\n"
        "- The tool initiates payment with real-time callback integration\n"
        "- It waits for payment completion and returns actual transaction details\n"
        "- Provide immediate feedback with real transaction status and IDs\n"
        "- Use personalized responses based on payment results\n\n"

        "💡 SMART DESCRIPTION INFERENCE:\n"
        "- Analyze conversation to determine payment purpose\n"
        "- Use contextual clues: 'lunch', 'transport', 'rent', 'shopping', 'emergency', etc.\n"
        "- Default to 'AI Agent Payment' if purpose is unclear\n"
        "- Payment descriptions are automatically generated\n\n"

        "⚡ INSTANT PROCESSING WITH REAL-TIME FEEDBACK:\n"
        "- User: 'Send 500 to 0712345678 for lunch' → IMMEDIATELY process\n"
        "- CRITICAL: Extract sender's phone from user_profile.phone or user_profile.sender_phone\n"
        "- System: Sends STK push to SENDER'S phone + tracks completion automatically\n"
        "- You: Provide real-time updates: 'Payment sent! ✅ Completed successfully!' or 'Payment failed ❌'\n"
        "- Users get immediate feedback without asking for status\n\n"

        "🔑 PHONE NUMBER USAGE:\n"
        "- ALWAYS use user's WhatsApp phone number for STK push (the sender)\n"
        "- NEVER use the recipient number mentioned in the message\n"
        "- Access sender phone from session: user_profile.phone or user_profile.sender_phone\n"
        "- Example: User says 'Send 100 to 0759550133' → Use user's phone, NOT 0759550133\n\n"

        "🔔 AUTOMATIC NOTIFICATIONS:\n"
        "- When payment completes successfully: '✅ Payment completed! 500 KSh sent successfully'\n"
        "- When payment fails: '❌ Payment failed: [reason]'\n"
        "- When payment times out: '⏱️ Payment pending - user may not have completed on phone'\n"
        "- Always include payment details and next steps\n\n"

        "🎯 TOOLS PRIORITY:\n"
        "1. send_instant_payment_with_tracking() - PRIMARY tool with real-time callback tracking\n"

        "🎯 EXAMPLES:\n"
        "User: 'Send 500 to 0759550133'\n"
        "You: [Call send_instant_payment_with_tracking(phone_number='{sender_phone_number}', amount=500, wait_for_completion=True)]\n"
        "IMPORTANT: ALWAYS use {sender_phone_number}, NEVER use the recipient number (0759550133)\n"
        "Tool returns: {'status': 'success', 'checkout_request_id': 'ws_CO_28...', 'amount': 500, 'payment_details': {'MpesaReceiptNumber': 'ABC123'}}\n"
        "Your response: '✅ Payment completed! 💰 500 KSh charged from your account 🧾 Transaction ID: ABC123'\n\n"

        "Remember: \n"
        "- ALWAYS use {sender_phone_number} for STK push\n"
        "- This ensures the sender pays from their own account\n"
        "- M-Pesa doesn't support direct peer-to-peer transfers via STK"
    ),
    tools=[
        send_instant_payment_with_tracking,  # Primary tool for payments with callback tracking
    ],
)