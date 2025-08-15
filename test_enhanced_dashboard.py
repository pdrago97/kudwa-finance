#!/usr/bin/env python3
"""
Test the enhanced dashboard with sample data
"""

import requests
import json
from datetime import datetime

# Test the dashboard with a mock response that includes actual data instead of schema
def test_with_mock_data():
    """Test the dashboard with mock structured data"""
    
    # Mock response that simulates what n8n should return (actual data, not schema)
    mock_response = {
        "response": "I've analyzed your financial document and identified several opportunities to extend your ontology.",
        "response_type": "ontology_proposal", 
        "confidence_score": 0.87,
        "ontology_extensions": [
            {
                "id": "ext_001",
                "entity_type": "Payment Gateway",
                "description": "A digital payment processing service that handles online transactions",
                "justification": "Found multiple references to Stripe, PayPal, and Square in the document",
                "confidence": 0.92
            },
            {
                "id": "ext_002", 
                "entity_type": "Merchant Account",
                "description": "A business bank account that allows companies to accept credit card payments",
                "justification": "Document mentions merchant fees and settlement processes",
                "confidence": 0.78
            }
        ],
        "data_entry_proposals": [
            {
                "id": "data_001",
                "entity_type": "Transaction",
                "proposed_data": {
                    "amount": 1250.00,
                    "currency": "USD",
                    "payment_method": "credit_card",
                    "merchant": "TechCorp Inc",
                    "date": "2025-08-15"
                },
                "confidence": 0.89
            }
        ]
    }
    
    print("🧪 Testing Enhanced Dashboard")
    print("=" * 50)
    print(f"Mock Response: {json.dumps(mock_response, indent=2)}")
    print("=" * 50)
    
    # This would be sent to the dashboard via the webhook
    # The dashboard should now create interactive components for:
    # 1. Ontology extensions with Supabase preview
    # 2. Data entry proposals with validation
    # 3. Human-in-the-loop approval buttons
    
    return mock_response

def test_supabase_connection():
    """Test if we can connect to Supabase"""
    try:
        import os
        from dotenv import load_dotenv
        from supabase import create_client
        
        load_dotenv()
        
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Supabase credentials not found in .env")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connection by getting ontology classes count
        result = supabase.table('kudwa_ontology_classes').select('id', count='exact').execute()
        print(f"✅ Supabase connected! Found {result.count} ontology classes")
        
        # Show recent classes
        recent = supabase.table('kudwa_ontology_classes')\
            .select('class_id, label, confidence_score, created_at')\
            .order('created_at', desc=True)\
            .limit(3)\
            .execute()
            
        print("\n📋 Recent Ontology Classes:")
        for item in (recent.data or []):
            print(f"  • {item.get('label', 'Unknown')} ({item.get('confidence_score', 0):.1%})")
            
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced Kudwa Dashboard")
    print()
    
    # Test Supabase connection
    supabase_ok = test_supabase_connection()
    print()
    
    # Test mock data structure
    mock_data = test_with_mock_data()
    print()
    
    print("🎯 Next Steps:")
    print("1. Visit http://localhost:8051 to see the enhanced dashboard")
    print("2. Try sending a message to see the interactive schema form")
    print("3. Use the dashboard sidebar to view current ontology stats")
    if supabase_ok:
        print("4. ✅ Supabase is connected - approvals will be saved to database")
    else:
        print("4. ⚠️  Configure Supabase in .env for full functionality")
    print()
    print("💡 The dashboard now includes:")
    print("   • Interactive ontology extension proposals")
    print("   • Database preview before adding to Supabase")
    print("   • Human-in-the-loop approval workflow")
    print("   • Real-time ontology statistics")
    print("   • Pending approvals management")
