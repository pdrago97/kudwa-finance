#!/usr/bin/env python3
"""
Add more relations to make the ontology graph more interesting
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import uuid

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials not found in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Additional ontology classes for a richer graph
additional_classes = [
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "payment_method",
        "label": "Payment Method",
        "class_type": "pl:PaymentMethod",
        "properties": {"method_type": "electronic", "description": "Electronic payment method"},
        "status": "active",
        "confidence_score": 0.88
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "customer",
        "label": "Customer",
        "class_type": "pl:Entity",
        "properties": {"entity_type": "customer", "description": "Customer entity"},
        "status": "active",
        "confidence_score": 0.92
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "invoice",
        "label": "Invoice",
        "class_type": "pl:Document",
        "properties": {"document_type": "invoice", "description": "Invoice document"},
        "status": "active",
        "confidence_score": 0.85
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "class_id": "tax_category",
        "label": "Tax Category",
        "class_type": "pl:Category",
        "properties": {"category_type": "tax", "description": "Tax classification category"},
        "status": "pending_review",
        "confidence_score": 0.75
    }
]

# Additional relations to create a more connected graph
additional_relations = [
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "customer",
        "predicate": "makes",
        "object_class_id": "financial_transaction",
        "properties": {"description": "Customers make financial transactions"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "financial_transaction",
        "predicate": "uses",
        "object_class_id": "payment_method",
        "properties": {"description": "Transactions use payment methods"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "invoice",
        "predicate": "generates",
        "object_class_id": "financial_transaction",
        "properties": {"description": "Invoices generate financial transactions"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "customer",
        "predicate": "receives",
        "object_class_id": "invoice",
        "properties": {"description": "Customers receive invoices"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "revenue_account",
        "predicate": "applies",
        "object_class_id": "tax_category",
        "properties": {"description": "Revenue accounts apply tax categories"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "expense_account",
        "predicate": "applies",
        "object_class_id": "tax_category",
        "properties": {"description": "Expense accounts apply tax categories"}
    },
    {
        "id": str(uuid.uuid4()),
        "domain": "default",
        "subject_class_id": "payment_method",
        "predicate": "processes",
        "object_class_id": "revenue_account",
        "properties": {"description": "Payment methods process revenue"}
    }
]

try:
    print("🚀 Adding additional ontology classes...")
    result = supabase.table("kudwa_ontology_classes").insert(additional_classes).execute()
    print(f"✅ Added {len(additional_classes)} additional ontology classes")
    
    print("🚀 Adding additional relations...")
    result = supabase.table("kudwa_ontology_relations").insert(additional_relations).execute()
    print(f"✅ Added {len(additional_relations)} additional relations")
    
    print("🎉 Additional graph data added successfully!")
    print("📊 Refresh your dashboard at http://localhost:8050 to see the enhanced ontology graph")
    
except Exception as e:
    print(f"❌ Error adding additional data: {e}")
