#!/usr/bin/env python3
"""
Quick test script to verify all Kudwa services are running correctly
"""

import requests
import json
import time
from datetime import datetime

def test_service(name, url, expected_status=200):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {name}: {url} - OK")
            return True
        else:
            print(f"❌ {name}: {url} - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False

def test_webhook(name, url, payload):
    """Test webhook endpoint with payload"""
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ {name}: Webhook responded successfully")
            try:
                data = response.json()
                if 'response' in data:
                    print(f"   Response: {data['response'][:100]}...")
                return True
            except:
                print(f"   Raw response: {response.text[:100]}...")
                return True
        else:
            print(f"❌ {name}: Webhook returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Webhook error: {e}")
        return False

def main():
    print("🧠 Kudwa Services Test Suite")
    print("=" * 50)
    
    # Test basic service endpoints
    services = [
        ("FastAPI Backend", "http://localhost:8000/health"),
        ("Chat Dashboard", "http://localhost:8051"),
        ("Mock N8N Webhook", "http://localhost:8052/health"),
        ("FastAPI Docs", "http://localhost:8000/api/v1/docs"),
    ]
    
    print("\n📍 Testing Service Endpoints:")
    all_services_ok = True
    for name, url in services:
        if not test_service(name, url):
            all_services_ok = False
    
    # Test webhook functionality
    print("\n🔗 Testing Webhook Integration:")
    webhook_payload = {
        "body": {
            "message": "Test message from test script",
            "timestamp": datetime.now().isoformat()
        },
        "chatId": "test-chat-123"
    }
    
    webhook_ok = test_webhook(
        "Mock Ontology Webhook", 
        "http://localhost:8052/webhook/ontology-extension",
        webhook_payload
    )
    
    # Summary
    print("\n" + "=" * 50)
    if all_services_ok and webhook_ok:
        print("🎉 All services are running correctly!")
        print("\n📋 Next Steps:")
        print("  • Open http://localhost:8051 to use the chat dashboard")
        print("  • Open http://localhost:8000/api/v1/docs for API documentation")
        print("  • Set USE_MOCK_WEBHOOK=true in .env to use local testing")
    else:
        print("⚠️  Some services have issues. Check the output above.")
        print("\n🔧 Troubleshooting:")
        print("  • Make sure ./start_kudwa.sh is running")
        print("  • Check logs in the logs/ directory")
        print("  • Verify all dependencies are installed")

if __name__ == "__main__":
    main()
