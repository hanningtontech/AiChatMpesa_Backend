#!/usr/bin/env python3
"""
M-Pesa Callback Manager
Handles real-time payment notifications and status tracking
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import queue

class PaymentTracker:
    """Tracks pending payments and their status"""
    
    def __init__(self):
        self.pending_payments = {}  # checkout_request_id -> payment_info
        self.completed_payments = {}  # checkout_request_id -> callback_data
        self.payment_callbacks = {}  # checkout_request_id -> callback_function
        self.lock = threading.Lock()
    
    def add_pending_payment(self, checkout_request_id: str, payment_info: Dict[str, Any], 
                          callback_func: Optional[Callable] = None):
        """Add a payment to tracking"""
        with self.lock:
            self.pending_payments[checkout_request_id] = {
                **payment_info,
                'initiated_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            if callback_func:
                self.payment_callbacks[checkout_request_id] = callback_func
    
    def mark_payment_completed(self, checkout_request_id: str, callback_data: Dict[str, Any]):
        """Mark a payment as completed with callback data"""
        with self.lock:
            if checkout_request_id in self.pending_payments:
                # Move from pending to completed
                payment_info = self.pending_payments.pop(checkout_request_id)
                payment_info['completed_at'] = datetime.now().isoformat()
                payment_info['callback_data'] = callback_data
                
                # Extract payment result
                body = callback_data.get('Body', {})
                stk_callback = body.get('stkCallback', {})
                result_code = stk_callback.get('ResultCode')
                
                if result_code == 0:
                    payment_info['status'] = 'success'
                    # Extract payment details
                    callback_metadata = stk_callback.get('CallbackMetadata', {})
                    items = callback_metadata.get('Item', [])
                    payment_details = {}
                    for item in items:
                        name = item.get('Name')
                        value = item.get('Value')
                        payment_details[name] = value
                    payment_info['payment_details'] = payment_details
                else:
                    payment_info['status'] = 'failed'
                    payment_info['error_message'] = stk_callback.get('ResultDesc', 'Payment failed')
                
                self.completed_payments[checkout_request_id] = payment_info
                
                # Execute callback if registered
                if checkout_request_id in self.payment_callbacks:
                    callback_func = self.payment_callbacks.pop(checkout_request_id)
                    try:
                        callback_func(payment_info)
                    except Exception as e:
                        print(f"Error executing payment callback: {e}")
                
                return payment_info
        return None
    
    def get_payment_status(self, checkout_request_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a payment"""
        with self.lock:
            # Check completed payments first
            if checkout_request_id in self.completed_payments:
                return self.completed_payments[checkout_request_id]
            
            # Check pending payments
            if checkout_request_id in self.pending_payments:
                payment = self.pending_payments[checkout_request_id].copy()
                # Check if payment has timed out (5 minutes)
                initiated_time = datetime.fromisoformat(payment['initiated_at'])
                if datetime.now() - initiated_time > timedelta(minutes=5):
                    payment['status'] = 'timeout'
                return payment
            
            return None
    
    def cleanup_old_payments(self, hours: int = 24):
        """Remove old completed payments to prevent memory buildup"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self.lock:
            to_remove = []
            for checkout_id, payment in self.completed_payments.items():
                completed_time = datetime.fromisoformat(payment.get('completed_at', payment['initiated_at']))
                if completed_time < cutoff_time:
                    to_remove.append(checkout_id)
            
            for checkout_id in to_remove:
                self.completed_payments.pop(checkout_id, None)

class CallbackManager:
    """Manages M-Pesa callback integration with the agent"""
    
    def __init__(self):
        self.tracker = PaymentTracker()
        self.notification_queue = queue.Queue()
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Start background thread for processing notifications
        self.processing_thread = threading.Thread(target=self._process_notifications, daemon=True)
        self.processing_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def register_payment(self, checkout_request_id: str, phone_number: str, amount: float, 
                        description: str, callback_func: Optional[Callable] = None) -> Dict[str, Any]:
        """Register a new payment for tracking"""
        payment_info = {
            'checkout_request_id': checkout_request_id,
            'phone_number': phone_number,
            'amount': amount,
            'description': description
        }
        
        self.tracker.add_pending_payment(checkout_request_id, payment_info, callback_func)
        
        return {
            'status': 'registered',
            'message': f'Payment tracking started for {checkout_request_id}',
            'payment_info': payment_info
        }
    
    def process_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming M-Pesa callback"""
        try:
            # Extract checkout request ID
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            if not checkout_request_id:
                return {'status': 'error', 'message': 'No CheckoutRequestID found in callback'}
            
            # Update payment status
            payment_info = self.tracker.mark_payment_completed(checkout_request_id, callback_data)
            
            if payment_info:
                # Add to notification queue for real-time processing
                self.notification_queue.put({
                    'type': 'payment_completed',
                    'checkout_request_id': checkout_request_id,
                    'payment_info': payment_info,
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'status': 'success',
                    'message': f'Payment {checkout_request_id} processed successfully',
                    'payment_status': payment_info['status'],
                    'payment_info': payment_info
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'Callback received for unknown payment {checkout_request_id}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error processing callback: {str(e)}'
            }
    
    def get_payment_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """Get real-time payment status"""
        payment_info = self.tracker.get_payment_status(checkout_request_id)
        
        if payment_info:
            return {
                'status': 'found',
                'payment_status': payment_info['status'],
                'payment_info': payment_info
            }
        else:
            return {
                'status': 'not_found',
                'message': f'No payment found with ID {checkout_request_id}'
            }
    
    def wait_for_payment_completion(self, checkout_request_id: str, timeout_seconds: int = 80) -> Dict[str, Any]:
        """Wait for payment completion with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            payment_info = self.tracker.get_payment_status(checkout_request_id)
            
            if payment_info and payment_info['status'] in ['success', 'failed', 'timeout']:
                return {
                    'status': 'completed',
                    'payment_status': payment_info['status'],
                    'payment_info': payment_info
                }
            
            time.sleep(1)  # Check every second
        
        return {
            'status': 'timeout',
            'message': f'Payment {checkout_request_id} did not complete within {timeout_seconds} seconds'
        }
    
    def _process_notifications(self):
        """Background thread to process payment notifications"""
        while True:
            try:
                notification = self.notification_queue.get(timeout=1)
                # Here you can add real-time notification logic
                # e.g., WebSocket broadcasts, email notifications, etc.
                print(f"🔔 Payment notification: {notification['checkout_request_id']} - {notification['payment_info']['status']}")
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing notification: {e}")
    
    def _periodic_cleanup(self):
        """Background thread for periodic cleanup"""
        while True:
            try:
                time.sleep(3600)  # Run every hour
                self.tracker.cleanup_old_payments()
            except Exception as e:
                print(f"Error in cleanup: {e}")

# Global callback manager instance
callback_manager = CallbackManager()
