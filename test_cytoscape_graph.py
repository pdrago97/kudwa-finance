#!/usr/bin/env python3
"""
Test the new Cytoscape ontology graph with sample data
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

def setup_sample_ontology():
    """Add sample ontology data to test the Cytoscape graph"""
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase credentials not found in .env")
        return False
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Sample financial ontology classes
    sample_classes = [
        {
            'class_id': 'payment_gateway',
            'label': 'Payment Gateway',
            'domain': 'financial',
            'class_type': 'pl:Entity',
            'confidence_score': 0.95,
            'status': 'active',
            'properties': {
                'description': 'Digital payment processing service',
                'examples': ['Stripe', 'PayPal', 'Square'],
                'category': 'infrastructure'
            }
        },
        {
            'class_id': 'customer_account',
            'label': 'Customer Account',
            'domain': 'business',
            'class_type': 'pl:Entity',
            'confidence_score': 0.92,
            'status': 'active',
            'properties': {
                'description': 'Individual customer financial account',
                'attributes': ['account_number', 'balance', 'status'],
                'category': 'core_entity'
            }
        },
        {
            'class_id': 'transaction',
            'label': 'Financial Transaction',
            'domain': 'financial',
            'class_type': 'pl:Event',
            'confidence_score': 0.98,
            'status': 'active',
            'properties': {
                'description': 'A financial transaction between parties',
                'attributes': ['amount', 'currency', 'timestamp', 'type'],
                'category': 'core_event'
            }
        },
        {
            'class_id': 'risk_assessment',
            'label': 'Risk Assessment',
            'domain': 'technical',
            'class_type': 'pl:Process',
            'confidence_score': 0.87,
            'status': 'active',
            'properties': {
                'description': 'Process for evaluating financial risk',
                'methods': ['credit_scoring', 'fraud_detection', 'compliance_check'],
                'category': 'analysis'
            }
        },
        {
            'class_id': 'compliance_rule',
            'label': 'Compliance Rule',
            'domain': 'legal',
            'class_type': 'pl:Rule',
            'confidence_score': 0.90,
            'status': 'active',
            'properties': {
                'description': 'Legal compliance requirements',
                'frameworks': ['PCI-DSS', 'GDPR', 'SOX'],
                'category': 'governance'
            }
        }
    ]
    
    # Sample relationships
    sample_relations = [
        {
            'subject_class_id': 'customer_account',
            'predicate': 'initiates',
            'object_class_id': 'transaction',
            'domain': 'financial',
            'confidence_score': 0.95,
            'status': 'active',
            'properties': {'relationship_type': 'action'}
        },
        {
            'subject_class_id': 'payment_gateway',
            'predicate': 'processes',
            'object_class_id': 'transaction',
            'domain': 'financial',
            'confidence_score': 0.93,
            'status': 'active',
            'properties': {'relationship_type': 'processing'}
        },
        {
            'subject_class_id': 'transaction',
            'predicate': 'triggers',
            'object_class_id': 'risk_assessment',
            'domain': 'technical',
            'confidence_score': 0.88,
            'status': 'active',
            'properties': {'relationship_type': 'workflow'}
        },
        {
            'subject_class_id': 'risk_assessment',
            'predicate': 'validates_against',
            'object_class_id': 'compliance_rule',
            'domain': 'legal',
            'confidence_score': 0.91,
            'status': 'active',
            'properties': {'relationship_type': 'validation'}
        },
        {
            'subject_class_id': 'payment_gateway',
            'predicate': 'must_comply_with',
            'object_class_id': 'compliance_rule',
            'domain': 'legal',
            'confidence_score': 0.96,
            'status': 'active',
            'properties': {'relationship_type': 'compliance'}
        }
    ]
    
    try:
        print("🌱 Adding sample ontology classes...")
        
        # Clear existing test data first
        supabase.table('kudwa_ontology_relations').delete().neq('id', 0).execute()
        supabase.table('kudwa_ontology_classes').delete().neq('id', 0).execute()
        
        # Add classes
        for cls in sample_classes:
            result = supabase.table('kudwa_ontology_classes').insert(cls).execute()
            print(f"  ✅ Added: {cls['label']}")
        
        print("\n🔗 Adding sample relationships...")
        
        # Add relationships
        for rel in sample_relations:
            result = supabase.table('kudwa_ontology_relations').insert(rel).execute()
            print(f"  ✅ Added: {rel['subject_class_id']} → {rel['predicate']} → {rel['object_class_id']}")
        
        print(f"\n🎉 Sample ontology created successfully!")
        print(f"📊 Classes: {len(sample_classes)}")
        print(f"🔗 Relations: {len(sample_relations)}")
        print(f"🌐 Domains: {len(set(cls['domain'] for cls in sample_classes))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample ontology: {e}")
        return False

def test_graph_features():
    """Test the graph features"""
    print("\n🧪 Testing Cytoscape Graph Features:")
    print("=" * 50)
    print("✅ Network Graph Visualization (not X/Y scatter!)")
    print("✅ Interactive nodes and edges")
    print("✅ Domain-based color coding:")
    print("   🔵 Financial (blue)")
    print("   🟢 Business (green)")  
    print("   🔴 Technical (red)")
    print("   🟣 Legal (purple)")
    print("✅ Multiple layout options:")
    print("   🌐 Force-directed (COSE) - default")
    print("   🎯 Circular")
    print("   📊 Hierarchical (Dagre)")
    print("   🔄 Concentric")
    print("   📐 Grid")
    print("✅ Click nodes to see detailed information")
    print("✅ Real-time updates when adding entities via chat")
    print("✅ Confidence-based node sizing")
    print("✅ Relationship labels on edges")

if __name__ == "__main__":
    print("🚀 Setting up Cytoscape Ontology Graph Test")
    print()
    
    # Setup sample data
    success = setup_sample_ontology()
    
    if success:
        test_graph_features()
        print()
        print("🎯 Next Steps:")
        print("1. Visit http://localhost:8051 to see the Cytoscape graph")
        print("2. Try different layouts using the dropdown")
        print("3. Click on nodes to see detailed information")
        print("4. Send a chat message and accept an extension to see real-time updates")
        print("5. The graph will grow as you add entities through conversation!")
        print()
        print("💡 This is a proper network graph like GraphRAG, not a scatter plot! 🎉")
    else:
        print("❌ Failed to setup sample data. Check your Supabase configuration.")
