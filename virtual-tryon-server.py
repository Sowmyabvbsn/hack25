#!/usr/bin/env python3
"""
Simple server to run the virtual try-on service alongside the main application.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import gradio
        import google.cloud.logging
        from google import genai
        from PIL import Image
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set."""
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or set these variables")
        return False
    
    print("✅ Environment variables are configured")
    return True

def run_virtual_tryon():
    """Run the virtual try-on Gradio app."""
    if not check_requirements():
        return False
    
    if not check_environment():
        print("💡 You can still run the app, but virtual try-on functionality may not work")
    
    print("🚀 Starting Virtual Try-On service...")
    
    try:
        # Run the virtual try-on script
        subprocess.run([sys.executable, "virtual-tryon.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start virtual try-on service: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Virtual Try-On service stopped")
        return True

if __name__ == "__main__":
    print("🎭 Bharat Heritage - Virtual Try-On Service")
    print("=" * 50)
    
    # Load environment variables from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Loaded environment variables from .env file")
        except ImportError:
            print("💡 Install python-dotenv to automatically load .env file")
    
    run_virtual_tryon()