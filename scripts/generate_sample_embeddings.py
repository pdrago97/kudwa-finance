#!/usr/bin/env python3
"""
Generate sample embeddings for RAG testing
"""

import os
import sys
import uuid
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sentence_transformers import SentenceTransformer
from app.services.supabase_client import SupabaseService
import structlog

logger = structlog.get_logger(__name__)

def generate_sample_embeddings():
    """Generate sample embeddings from financial observations"""
    
    # Initialize services
    supabase = SupabaseService()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get financial observations
    observations = supabase.client.table("kudwa_financial_observations")\
        .select("id, account_name, amount, observation_type, source_document_id, metadata")\
        .limit(50)\
        .execute()
    
    if not observations.data:
        print("No financial observations found")
        return
    
    print(f"Processing {len(observations.data)} observations...")
    
    embeddings_to_insert = []
    
    for obs in observations.data:
        # Create content text for embedding
        content_parts = [
            f"Account: {obs['account_name']}",
            f"Type: {obs['observation_type']}",
            f"Amount: {obs['amount']} USD"
        ]
        
        # Add metadata if available
        if obs.get('metadata') and obs['metadata'].get('properties'):
            props = obs['metadata']['properties']
            if props.get('account_category'):
                content_parts.append(f"Category: {props['account_category']}")
        
        content = " | ".join(content_parts)
        
        # Generate embedding
        embedding = model.encode([content])[0].tolist()
        
        # Prepare for insertion - use dummy vector for the required column, real vector in metadata
        dummy_vector = [0.0] * 1536  # Create 1536-dim zero vector to satisfy constraint
        embeddings_to_insert.append({
            "id": str(uuid.uuid4()),
            "content": content,
            "embedding": dummy_vector,  # Dummy vector to satisfy NOT NULL constraint
            "source_kind": "financial_observation",
            "source_id": obs["id"],
            "ontology_class_id": obs.get("observation_type"),
            "metadata": {
                "account_name": obs["account_name"],
                "amount": obs["amount"],
                "observation_type": obs["observation_type"],
                "embedding_vector": embedding  # Real 384-dim vector in metadata
            }
        })
    
    # Insert embeddings in batches
    batch_size = 10
    for i in range(0, len(embeddings_to_insert), batch_size):
        batch = embeddings_to_insert[i:i+batch_size]
        try:
            result = supabase.client.table("kudwa_embeddings").insert(batch).execute()
            print(f"Inserted batch {i//batch_size + 1}: {len(batch)} embeddings")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {e}")
    
    print(f"✅ Generated {len(embeddings_to_insert)} embeddings")

def generate_ontology_embeddings():
    """Generate embeddings for ontology classes"""
    
    supabase = SupabaseService()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get ontology classes
    classes = supabase.client.table("kudwa_ontology_classes")\
        .select("id, class_id, label, class_type, properties")\
        .eq("status", "active")\
        .execute()
    
    if not classes.data:
        print("No active ontology classes found")
        return
    
    print(f"Processing {len(classes.data)} ontology classes...")
    
    embeddings_to_insert = []
    
    for cls in classes.data:
        # Create content text
        content = f"Ontology Class: {cls['label']} ({cls['class_id']}) - Type: {cls.get('class_type', 'entity')}"
        
        # Generate embedding
        embedding = model.encode([content])[0].tolist()
        
        dummy_vector = [0.0] * 1536  # Create 1536-dim zero vector to satisfy constraint
        embeddings_to_insert.append({
            "id": str(uuid.uuid4()),
            "content": content,
            "embedding": dummy_vector,  # Dummy vector to satisfy NOT NULL constraint
            "source_kind": "ontology_class",
            "source_id": cls["id"],
            "ontology_class_id": cls["class_id"],
            "metadata": {
                "class_id": cls["class_id"],
                "label": cls["label"],
                "class_type": cls.get("class_type"),
                "embedding_vector": embedding  # Real 384-dim vector in metadata
            }
        })
    
    # Insert embeddings
    try:
        result = supabase.client.table("kudwa_embeddings").insert(embeddings_to_insert).execute()
        print(f"✅ Generated {len(embeddings_to_insert)} ontology embeddings")
    except Exception as e:
        print(f"Error inserting ontology embeddings: {e}")

if __name__ == "__main__":
    print("🔧 Generating sample embeddings for RAG...")
    
    # Clear existing embeddings
    try:
        supabase = SupabaseService()
        supabase.client.table("kudwa_embeddings").delete().neq("id", "").execute()
        print("🧹 Cleared existing embeddings")
    except Exception as e:
        print(f"Warning: Could not clear embeddings: {e}")
    
    # Generate new embeddings
    generate_sample_embeddings()
    generate_ontology_embeddings()
    
    print("✨ Embedding generation complete!")
