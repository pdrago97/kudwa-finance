#!/usr/bin/env python3
"""
Debug script to understand the n8n response structure
"""

import requests
import json
from datetime import datetime

# Test the webhook with a simple message
webhook_url = "https://n8n-moveup-u53084.vm.elestio.app/webhook-test/9ba11544-5c4e-4f91-818a-08a4ecb596c5"

test_payload = {
    "message": "Hello, can you analyze this simple message?",
    "timestamp": datetime.now().isoformat(),
    "chatId": "debug-test-456"
}

print("🔍 Testing n8n webhook to understand response structure...")
print(f"URL: {webhook_url}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print("-" * 60)

try:
    response = requests.post(
        webhook_url,
        json=test_payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": "kudwa_secure_api_key_2025_8f9d2e1a4b7c3f6e9d8a5b2c7f1e4d9a"
        },
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("-" * 60)
    
    if response.status_code == 200:
        try:
            json_response = response.json()
            print("✅ JSON Response Structure:")
            print(f"Type: {type(json_response)}")
            print(f"Content: {json.dumps(json_response, indent=2, default=str)}")
            
            if isinstance(json_response, list):
                print(f"\n📋 List Analysis:")
                print(f"Length: {len(json_response)}")
                if len(json_response) > 0:
                    print(f"First item type: {type(json_response[0])}")
                    print(f"First item: {json.dumps(json_response[0], indent=2, default=str)}")
                    
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            print(f"Raw response: {response.text}")
    else:
        print(f"❌ Error response: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
