#!/usr/bin/env python3
"""
Test script for ingesting data2.json into the Kudwa financial ontology system
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
USER_ID = "demo_user"
DATA_FILE = "data2.json"

def test_rootfi_ingestion():
    """Test the RootFi data ingestion endpoint"""
    
    # Check if data file exists
    if not Path(DATA_FILE).exists():
        print(f"❌ Error: {DATA_FILE} not found in current directory")
        return False
    
    print(f"🔄 Starting RootFi data ingestion test...")
    print(f"📁 File: {DATA_FILE}")
    print(f"👤 User: {USER_ID}")
    print(f"🌐 API: {API_BASE_URL}")
    print("-" * 50)
    
    try:
        # Prepare file upload
        with open(DATA_FILE, 'rb') as f:
            files = {'file': (DATA_FILE, f, 'application/json')}
            data = {'user_id': USER_ID}
            
            # Send request to RootFi ingestion endpoint
            response = requests.post(
                f"{API_BASE_URL}/documents/ingest-rootfi",
                files=files,
                data=data,
                timeout=60
            )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✅ Ingestion successful!")
            print(f"📄 Document ID: {result.get('document_id')}")
            print(f"🔢 Entities extracted: {result.get('entities_extracted')}")
            print(f"📊 Records processed: {result.get('records_processed')}")
            print(f"🏷️  Entity types: {', '.join(result.get('entity_types', []))}")
            print(f"⭐ Data quality score: {result.get('data_quality_score'):.2f}")
            print(f"⏱️  Processing time: {result.get('processing_time_ms')}ms")
            print(f"💬 Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Ingestion failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_database_stats():
    """Check database statistics after ingestion"""
    
    print("\n" + "=" * 50)
    print("📊 Checking database statistics...")
    
    try:
        # Get ontology classes count
        response = requests.get(f"{API_BASE_URL}/ontology/classes")
        if response.status_code == 200:
            classes = response.json()
            print(f"🏷️  Ontology classes: {len(classes)}")
        
        # Get financial observations count  
        response = requests.get(f"{API_BASE_URL}/financial/observations")
        if response.status_code == 200:
            observations = response.json()
            print(f"📈 Financial observations: {len(observations)}")
        
        # Get documents count
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            documents = response.json()
            print(f"📄 Documents: {len(documents)}")
            
    except Exception as e:
        print(f"⚠️  Could not retrieve database stats: {str(e)}")

def main():
    """Main test function"""
    
    print("🚀 Kudwa Financial Data Ingestion Test")
    print("=" * 50)
    
    # Test RootFi ingestion
    success = test_rootfi_ingestion()
    
    if success:
        # Check database stats
        check_database_stats()
        
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        print("💡 You can now:")
        print("   - Open the dashboard at http://localhost:8050")
        print("   - Chat with the financial data using the RAG system")
        print("   - View the ontology graph visualization")
        print("   - Explore financial observations and trends")
    else:
        print("\n" + "=" * 50)
        print("❌ Test failed!")
        print("💡 Troubleshooting:")
        print("   - Make sure the FastAPI server is running: uvicorn app.main:app --reload")
        print("   - Check that Supabase is configured correctly")
        print("   - Verify data2.json is in the current directory")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
