#!/usr/bin/env python3
"""
Fix embedding dimensions in Supabase table
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.supabase_client import SupabaseService

def fix_embedding_dimensions():
    """Update the embedding column to use 384 dimensions instead of 1536"""
    
    supabase = SupabaseService()
    
    # SQL to alter the column - this needs to be run as a raw SQL query
    sql_commands = [
        # Drop the existing column constraint if it exists
        "ALTER TABLE kudwa_embeddings DROP CONSTRAINT IF EXISTS kudwa_embeddings_embedding_check;",
        
        # Drop and recreate the column with correct dimensions
        "ALTER TABLE kudwa_embeddings DROP COLUMN IF EXISTS embedding;",
        "ALTER TABLE kudwa_embeddings ADD COLUMN embedding vector(384);",
        
        # Add index for similarity search
        "CREATE INDEX IF NOT EXISTS kudwa_embeddings_embedding_idx ON kudwa_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
    ]
    
    for sql in sql_commands:
        try:
            print(f"Executing: {sql}")
            result = supabase.client.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Success")
        except Exception as e:
            print(f"❌ Error: {e}")
            # Try alternative approach using direct SQL execution
            try:
                # This might work if the RPC function exists
                result = supabase.client.postgrest.rpc('exec_sql', {'query': sql}).execute()
                print(f"✅ Success (alternative method)")
            except Exception as e2:
                print(f"❌ Alternative method also failed: {e2}")
                print("You may need to run this SQL manually in the Supabase dashboard:")
                print(f"  {sql}")

if __name__ == "__main__":
    print("🔧 Fixing embedding dimensions...")
    fix_embedding_dimensions()
    print("✨ Done! You may need to run some SQL commands manually in Supabase dashboard.")
