#!/usr/bin/env python3
"""
Add sample data to test the dashboard
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
import uuid

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials not found in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample ontology classes
sample_classes = [
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "revenue_account",
        "label": "Revenue Account",
        "class_type": "pl:Account",
        "properties": {"account_type": "revenue", "currency": "USD", "description": "Account for tracking revenue"},
        "status": "active",
        "confidence_score": 0.95
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "expense_account",
        "label": "Expense Account",
        "class_type": "pl:Account",
        "properties": {"account_type": "expense", "currency": "USD", "description": "Account for tracking expenses"},
        "status": "active",
        "confidence_score": 0.90
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "financial_transaction",
        "label": "Financial Transaction",
        "class_type": "pl:Transaction",
        "properties": {"transaction_type": "general", "description": "A financial transaction record"},
        "status": "pending_review",
        "confidence_score": 0.85
    }
]

# Sample financial observations
sample_observations = [
    {
        "id": str(uuid.uuid4()),
        "dataset_id": str(uuid.uuid4()),
        "account_id": "rev_001",
        "account_name": "Sales Revenue",
        "amount": 25000.00,
        "currency": "USD",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "metadata": {"description": "January sales revenue", "source": "sample_data"}
    },
    {
        "id": str(uuid.uuid4()),
        "dataset_id": str(uuid.uuid4()),
        "account_id": "rev_002",
        "account_name": "Service Revenue",
        "amount": 15000.00,
        "currency": "USD",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "metadata": {"description": "January service revenue", "source": "sample_data"}
    },
    {
        "id": str(uuid.uuid4()),
        "dataset_id": str(uuid.uuid4()),
        "account_id": "exp_001",
        "account_name": "Office Expenses",
        "amount": -5000.00,
        "currency": "USD",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "metadata": {"description": "January office expenses", "source": "sample_data"}
    },
    {
        "id": str(uuid.uuid4()),
        "dataset_id": str(uuid.uuid4()),
        "account_id": "rev_001",
        "account_name": "Sales Revenue",
        "amount": 28000.00,
        "currency": "USD",
        "period_start": "2024-02-01",
        "period_end": "2024-02-29",
        "metadata": {"description": "February sales revenue", "source": "sample_data"}
    },
    {
        "id": str(uuid.uuid4()),
        "dataset_id": str(uuid.uuid4()),
        "account_id": "rev_002",
        "account_name": "Service Revenue",
        "amount": 18000.00,
        "currency": "USD",
        "period_start": "2024-02-01",
        "period_end": "2024-02-29",
        "metadata": {"description": "February service revenue", "source": "sample_data"}
    }
]

# Sample relations
sample_relations = [
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "revenue_account",
        "predicate": "contains",
        "object_class_id": "financial_transaction",
        "properties": {"description": "Revenue accounts contain financial transactions"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "expense_account",
        "predicate": "contains",
        "object_class_id": "financial_transaction",
        "properties": {"description": "Expense accounts contain financial transactions"}
    }
]

try:
    print("🚀 Adding sample ontology classes...")
    result = supabase.table("kudwa_ontology_classes").insert(sample_classes).execute()
    print(f"✅ Added {len(sample_classes)} ontology classes")
    
    print("🚀 Adding sample financial observations...")
    result = supabase.table("kudwa_financial_observations").insert(sample_observations).execute()
    print(f"✅ Added {len(sample_observations)} financial observations")
    
    print("🚀 Adding sample relations...")
    result = supabase.table("kudwa_ontology_relations").insert(sample_relations).execute()
    print(f"✅ Added {len(sample_relations)} relations")
    
    print("🎉 Sample data added successfully!")
    print("📊 Refresh your dashboard at http://localhost:8050 to see the data")
    
except Exception as e:
    print(f"❌ Error adding sample data: {e}")
