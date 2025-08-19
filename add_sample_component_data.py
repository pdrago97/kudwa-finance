#!/usr/bin/env python3
"""
Add sample data for testing the component generation system
"""
import os
import json
import requests
from datetime import datetime, timedelta

BACKEND_URL = "http://localhost:8000"

def add_sample_entities():
    """Add sample financial entities"""
    entities = [
        {
            "name": "Revenue Account",
            "properties": {
                "account_type": "revenue",
                "currency": "USD",
                "description": "Primary revenue tracking account"
            }
        },
        {
            "name": "Expense Account", 
            "properties": {
                "account_type": "expense",
                "currency": "USD",
                "description": "Operating expenses account"
            }
        },
        {
            "name": "Financial Period",
            "properties": {
                "period_type": "monthly",
                "description": "Monthly reporting period"
            }
        }
    ]
    
    print("Adding sample entities...")
    for entity in entities:
        # We'll add these through the upload system to trigger proper ontology extraction
        pass

def add_sample_data_via_upload():
    """Add sample data by uploading a JSON file"""
    
    sample_financial_data = {
        "company": "Sample Corp",
        "report_type": "monthly_financials",
        "periods": [
            {
                "period": "2024-01",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "accounts": [
                    {
                        "account_id": "REV001",
                        "account_name": "Sales Revenue",
                        "account_type": "revenue",
                        "amount": 25000.00,
                        "currency": "USD"
                    },
                    {
                        "account_id": "REV002", 
                        "account_name": "Service Revenue",
                        "account_type": "revenue",
                        "amount": 15000.00,
                        "currency": "USD"
                    },
                    {
                        "account_id": "EXP001",
                        "account_name": "Office Expenses",
                        "account_type": "expense", 
                        "amount": -5000.00,
                        "currency": "USD"
                    }
                ]
            },
            {
                "period": "2024-02",
                "start_date": "2024-02-01", 
                "end_date": "2024-02-29",
                "accounts": [
                    {
                        "account_id": "REV001",
                        "account_name": "Sales Revenue",
                        "account_type": "revenue",
                        "amount": 28000.00,
                        "currency": "USD"
                    },
                    {
                        "account_id": "REV002",
                        "account_name": "Service Revenue", 
                        "account_type": "revenue",
                        "amount": 18000.00,
                        "currency": "USD"
                    },
                    {
                        "account_id": "EXP001",
                        "account_name": "Office Expenses",
                        "account_type": "expense",
                        "amount": -5500.00,
                        "currency": "USD"
                    }
                ]
            },
            {
                "period": "2024-03",
                "start_date": "2024-03-01",
                "end_date": "2024-03-31", 
                "accounts": [
                    {
                        "account_id": "REV001",
                        "account_name": "Sales Revenue",
                        "account_type": "revenue",
                        "amount": 32000.00,
                        "currency": "USD"
                    },
                    {
                        "account_id": "REV002",
                        "account_name": "Service Revenue",
                        "account_type": "revenue", 
                        "amount": 22000.00,
                        "currency": "USD"
                    },
                    {
                        "account_id": "EXP001",
                        "account_name": "Office Expenses",
                        "account_type": "expense",
                        "amount": -6000.00,
                        "currency": "USD"
                    }
                ]
            }
        ]
    }
    
    # Save to temporary file
    temp_file = "sample_financial_data.json"
    with open(temp_file, 'w') as f:
        json.dump(sample_financial_data, f, indent=2)
    
    print(f"Uploading sample data from {temp_file}...")
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': (temp_file, f, 'application/json')}
            data = {
                'extract_ontology': True,
                'auto_approve': True
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/upload-json",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.ok:
                result = response.json()
                print("✅ Sample data uploaded successfully!")
                print(f"📊 Result: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Error uploading data: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_component_generation():
    """Test the component generation with sample prompts"""
    
    test_prompts = [
        "Show me a bar chart of total revenue by month",
        "Create a metric card showing total revenue",
        "Display a table of all financial accounts",
        "Show me a KPI dashboard with key financial metrics"
    ]
    
    print("\n🧪 Testing component generation...")
    
    for prompt in test_prompts:
        print(f"\n📝 Testing prompt: '{prompt}'")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/generate-component",
                json={"prompt": prompt},
                timeout=30
            )
            
            if response.ok:
                component = response.json()
                print(f"✅ Generated component: {component.get('type')} - {component.get('title')}")
                print(f"📊 Data preview: {str(component.get('data', {}))[:100]}...")
            else:
                print(f"❌ Generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Adding sample data for component testing...")
    
    # Add sample data
    add_sample_data_via_upload()
    
    # Wait a moment for processing
    import time
    time.sleep(2)
    
    # Test component generation
    test_component_generation()
    
    print("\n🎉 Sample data setup complete!")
    print("💡 Now try the Canvas tab in your Streamlit app!")
