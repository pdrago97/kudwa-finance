#!/usr/bin/env python3
"""
Test script to verify the CrewAI system is working properly
"""

import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get("http://localhost:8000/api/v1/crew/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health Check:", data)
            return True
        else:
            print("❌ API Health Check Failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ API Health Check Error:", str(e))
        return False

def test_simple_chat():
    """Test simple chat functionality"""
    print("\n💬 Testing Simple Chat...")
    try:
        payload = {
            "message": "Hello, what can you help me with?",
            "context": {}
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/crew/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat Response:", data.get("response", "No response"))
            return True
        else:
            print("❌ Chat Test Failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Chat Test Error:", str(e))
        return False

def test_semantic_search():
    """Test semantic search functionality"""
    print("\n🔍 Testing Semantic Search...")
    try:
        payload = {
            "query": "financial data",
            "top_k": 5
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/crew/semantic-search",
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Semantic Search Results:", len(data.get("results", [])), "items found")
            return True
        else:
            print("❌ Semantic Search Failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Semantic Search Error:", str(e))
        return False

def test_dashboard_access():
    """Test dashboard accessibility"""
    print("\n📊 Testing Dashboard Access...")
    try:
        response = requests.get("http://localhost:8051/", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            return True
        else:
            print("❌ Dashboard access failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Dashboard access error:", str(e))
        return False

def main():
    """Run all tests"""
    print("🚀 Kudwa CrewAI System Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Health", test_api_health),
        ("Dashboard Access", test_dashboard_access),
        ("Semantic Search", test_semantic_search),
        ("Simple Chat", test_simple_chat),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All systems operational! Your CrewAI system is ready to use.")
        print("\n🌐 Access Points:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • CrewAI Dashboard: http://localhost:8051")
        print("   • API Base URL: http://localhost:8000/api/v1")
    else:
        print("\n⚠️  Some tests failed. Please check the system configuration.")

if __name__ == "__main__":
    main()
