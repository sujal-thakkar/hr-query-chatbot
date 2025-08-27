#!/usr/bin/env python3
"""
Simple keep-alive script to prevent Render free tier cold starts.
Run this locally or on a different service to ping your backend every 10 minutes.
"""

import requests
import time
import os
from datetime import datetime

BACKEND_URL = "https://backend-aohf.onrender.com"
PING_INTERVAL = 600  # 10 minutes

def ping_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=30)
        if response.status_code == 200:
            print(f"✅ {datetime.now()}: Backend is alive")
            return True
        else:
            print(f"⚠️ {datetime.now()}: Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {datetime.now()}: Failed to ping backend: {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 Starting keep-alive for {BACKEND_URL}")
    print(f"⏰ Pinging every {PING_INTERVAL} seconds")
    
    while True:
        ping_backend()
        time.sleep(PING_INTERVAL)
