import requests
import threading
import time
import sys
import os
from flask import Flask
from app import app

def start_server():
    app.run(port=5001, use_reloader=False)

def verify_ui():
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give server a moment to start
    time.sleep(2)
    
    base_url = "http://127.0.0.1:5001"
    
    try:
        # 1. Check Main Page
        print("Checking Main Page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Main Page loaded successfully")
            if 'style.css' in response.text:
                print("✓ CSS linked correctly")
            if 'script.js' in response.text:
                print("✓ JS linked correctly")
        else:
            print(f"✗ Main Page failed with status {response.status_code}")
            
        # 2. Check Login Page
        print("\nChecking Login Page...")
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✓ Login Page loaded successfully")
            if 'login-form' in response.text or '<form' in response.text:
                print("✓ Login form present")
        else:
            print(f"✗ Login Page failed with status {response.status_code}")

        # 3. Check Detail Page (using a known item ID if possible, or mock)
        # Since we are using in-memory DB, we know ID 1 exists (The Three-Body Problem)
        print("\nChecking Detail Page...")
        response = requests.get(f"{base_url}/detail/book/1")
        if response.status_code == 200:
            print("✓ Detail Page loaded successfully")
            if '三体' in response.text:
                print("✓ Item content present")
        else:
            print(f"✗ Detail Page failed with status {response.status_code}")
            
        print("\nUI Verification Completed.")
        
    except Exception as e:
        print(f"Verification failed with error: {e}")

if __name__ == "__main__":
    verify_ui()
