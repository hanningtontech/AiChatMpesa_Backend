#!/usr/bin/env python3
"""
Setup script for M-Pesa AI Agent
Helps you get started quickly with the necessary configuration
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment file"""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("📝 Please edit .env file with your M-Pesa credentials")
    else:
        print("❌ .env.example file not found")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import phonenumbers
        print("✅ phonenumbers library installed")
    except ImportError:
        print("❌ phonenumbers library not installed")
        print("   Run: pip install phonenumbers")
    
    try:
        import requests
        print("✅ requests library installed")
    except ImportError:
        print("❌ requests library not installed")
        print("   Run: pip install requests")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv library installed")
    except ImportError:
        print("❌ python-dotenv library not installed")
        print("   Run: pip install python-dotenv")

def show_next_steps():
    """Show next steps to the user"""
    print("\n" + "=" * 50)
    print("🚀 NEXT STEPS")
    print("=" * 50)
    
    print("\n1. Get M-Pesa Credentials:")
    print("   - Visit: https://developer.safaricom.co.ke/")
    print("   - Create an account and app")
    print("   - Get Consumer Key, Consumer Secret, and Passkey")
    
    print("\n2. Configure Environment:")
    print("   - Edit .env file with your credentials")
    print("   - Set MPESA_ENVIRONMENT=sandbox for testing")
    
    print("\n3. Test the Integration:")
    print("   - Run: python test_mpesa.py")
    print("   - This will test phone validation and STK push")
    
    print("\n4. Try the Example:")
    print("   - Run: python example_usage.py")
    print("   - This shows how to use the agent tools")
    
    print("\n5. Use the Agent:")
    print("   - Import the agent: from mpesa_agent.agent import root_agent")
    print("   - The agent now has M-Pesa capabilities!")
    
    print("\n📚 Documentation:")
    print("   - Read README.md for detailed instructions")
    print("   - Check the code comments for usage examples")

def main():
    """Main setup function"""
    print("M-Pesa AI Agent Setup")
    print("=" * 30)
    
    print("\n🔍 Checking dependencies...")
    check_dependencies()
    
    print("\n⚙️  Setting up environment...")
    setup_environment()
    
    show_next_steps()

if __name__ == "__main__":
    main()
