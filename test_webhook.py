#!/usr/bin/env python3
"""
Test script to debug the n8n webhook connection
"""

import requests
import json
from datetime import datetime

# Test the webhook with different authentication methods
webhook_url = "https://n8n-moveup-u53084.vm.elestio.app/webhook-test/9ba11544-5c4e-4f91-818a-08a4ecb596c5"

# Test payload
test_payload = {
    "message": "Test connection from debug script",
    "timestamp": datetime.now().isoformat(),
    "chatId": "test-debug-123"
}

print("🔍 Testing n8n webhook connection...")
print(f"URL: {webhook_url}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print("-" * 50)

# Test 1: No authentication
print("Test 1: No authentication")
try:
    response = requests.post(
        webhook_url,
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("-" * 50)

# Test 2: With X-API-Key header
print("Test 2: With X-API-Key header")
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
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("-" * 50)

# Test 3: With different header names that n8n might expect
for header_name in ["Authorization", "x-api-key", "api-key", "webhook-key"]:
    print(f"Test 3.{header_name}: With {header_name} header")
    try:
        headers = {
            "Content-Type": "application/json",
            header_name: "kudwa_secure_api_key_2025_8f9d2e1a4b7c3f6e9d8a5b2c7f1e4d9a"
        }
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers=headers,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code != 404:
            print(f"✅ SUCCESS with {header_name}!")
            print(f"Response: {response.text[:500]}")
            break
        else:
            print(f"❌ 404 with {header_name}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 25)
