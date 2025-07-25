#!/usr/bin/env python3
"""
FIXED M-Pesa tools - Direct implementation that works
TIMESTAMP: 2025-06-28 14:25:00 - FORCE RELOAD
"""

import os
import base64
import requests
from datetime import datetime
from typing import Dict, Any
import phonenumbers
from phonenumbers import NumberParseException
from dotenv import load_dotenv

# Load environment variables from root directory
import pathlib
root_dir = pathlib.Path(__file__).parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

# Debug print to verify this module is loaded
print("🔄 LOADING FIXED MPESA_TOOLS MODULE - 2025-06-28 14:25:00")

def validate_phone_number(phone: str) -> Dict[str, Any]:
    """
    Validates and formats a Kenyan phone number for M-Pesa.
    
    Args:
        phone (str): Phone number to validate (can be in various formats)
        
    Returns:
        dict: Validation result with formatted number or error
    """
    try:
        # Parse the phone number
        parsed = phonenumbers.parse(phone, "KE")  # KE for Kenya
        
        # Check if it's valid
        if not phonenumbers.is_valid_number(parsed):
            return {
                "status": "error",
                "error_message": f"Invalid phone number: {phone}"
            }
        
        # Format for M-Pesa (254XXXXXXXXX)
        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        # Remove the + sign
        formatted = formatted.replace('+', '')
        
        return {
            "status": "success",
            "formatted_number": formatted,
            "original_number": phone
        }
        
    except NumberParseException as e:
        return {
            "status": "error",
            "error_message": f"Could not parse phone number {phone}: {e}"
        }

def initiate_stk_push(phone_number: str, amount: float, account_reference: str = "Payment", transaction_desc: str = "Payment") -> Dict[str, Any]:
    """
    Initiates an STK Push request to the user's phone for M-Pesa payment.
    
    Args:
        phone_number (str): The phone number to send the STK push to
        amount (float): Amount to be paid
        account_reference (str): Account reference for the transaction
        transaction_desc (str): Description of the transaction
        
    Returns:
        dict: STK push response with status and details
    """
    
    # Validate phone number first
    phone_validation = validate_phone_number(phone_number)
    if phone_validation["status"] == "error":
        return phone_validation
    
    formatted_phone = phone_validation["formatted_number"]
    
    # Validate amount
    if amount <= 0:
        return {
            "status": "error",
            "error_message": "Amount must be greater than 0"
        }
    
    # Get credentials from environment
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    business_short_code = os.getenv('MPESA_BUSINESS_SHORT_CODE')
    passkey = os.getenv('MPESA_PASSKEY')
    callback_url = os.getenv('MPESA_CALLBACK_URL')
    environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
    
    if not all([consumer_key, consumer_secret, business_short_code, passkey]):
        return {
            "status": "error",
            "error_message": "Missing M-Pesa credentials in environment variables"
        }
    
    # Set base URL
    if environment == 'sandbox':
        base_url = 'https://sandbox.safaricom.co.ke'
    else:
        base_url = 'https://api.safaricom.co.ke'
    
    try:
        # Step 1: Get access token
        auth_string = f"{consumer_key}:{consumer_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to get access token: {response.status_code} - {response.text}"
            }
        
        access_token = response.json().get('access_token')
        if not access_token:
            return {
                "status": "error",
                "error_message": "No access token received from M-Pesa API"
            }
        
        # Step 2: Prepare STK Push
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{business_short_code}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode('utf-8')
        
        payload = {
            "BusinessShortCode": int(business_short_code),
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": int(formatted_phone),
            "PartyB": int(business_short_code),
            "PhoneNumber": int(formatted_phone),
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Step 3: Send STK Push
        response = requests.post(
            f"{base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ResponseCode') == '0':
                return {
                    "status": "success",
                    "message": "STK push sent successfully",
                    "checkout_request_id": result.get('CheckoutRequestID'),
                    "merchant_request_id": result.get('MerchantRequestID'),
                    "response_code": result.get('ResponseCode'),
                    "response_description": result.get('ResponseDescription'),
                    "customer_message": result.get('CustomerMessage')
                }
            else:
                return {
                    "status": "error",
                    "error_message": result.get('ResponseDescription', 'STK push failed'),
                    "response_code": result.get('ResponseCode')
                }
        else:
            return {
                "status": "error",
                "error_message": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error initiating STK push: {str(e)}"
        }

def check_transaction_status(checkout_request_id: str) -> Dict[str, Any]:
    """
    Checks the status of an STK push transaction.
    
    Args:
        checkout_request_id (str): The checkout request ID from STK push response
        
    Returns:
        dict: Transaction status and details
    """
    
    # Get credentials from environment
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    business_short_code = os.getenv('MPESA_BUSINESS_SHORT_CODE')
    passkey = os.getenv('MPESA_PASSKEY')
    environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
    
    if not all([consumer_key, consumer_secret, business_short_code, passkey]):
        return {
            "status": "error",
            "error_message": "Missing M-Pesa credentials in environment variables"
        }
    
    # Set base URL
    if environment == 'sandbox':
        base_url = 'https://sandbox.safaricom.co.ke'
    else:
        base_url = 'https://api.safaricom.co.ke'
    
    try:
        # Get access token
        auth_string = f"{consumer_key}:{consumer_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to get access token: {response.status_code}"
            }
        
        access_token = response.json().get('access_token')
        
        # Generate timestamp and password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{business_short_code}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode('utf-8')
        
        # Prepare request payload
        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Make the status query request
        response = requests.post(
            f"{base_url}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "transaction_status": result.get('ResultCode'),
                "transaction_description": result.get('ResultDesc'),
                "checkout_request_id": result.get('CheckoutRequestID'),
                "merchant_request_id": result.get('MerchantRequestID'),
                "response_code": result.get('ResponseCode')
            }
        else:
            return {
                "status": "error",
                "error_message": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error checking transaction status: {str(e)}"
        }
