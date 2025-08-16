#!/usr/bin/env python3
"""
Script to replace all supabase_service.create_entity calls with _create_kudwa_entity calls
"""

import re

def fix_entity_calls():
    """Fix all entity creation calls in the data parser"""
    
    with open('app/services/data_parser.py', 'r') as f:
        content = f.read()
    
    # Pattern to match supabase_service.create_entity calls
    pattern = r'await supabase_service\.create_entity\(\s*entity_type="([^"]+)",\s*name=([^,]+),\s*properties=\{([^}]+(?:\{[^}]*\}[^}]*)*)\},\s*metadata=\{([^}]+(?:\{[^}]*\}[^}]*)*)\},\s*source_document_id=([^,]+),\s*created_by="([^"]+)"\s*\)'
    
    def replace_call(match):
        entity_type = match.group(1)
        name = match.group(2)
        properties = match.group(3)
        metadata = match.group(4)
        document_id = match.group(5)
        created_by = match.group(6)
        
        # Extract confidence score from metadata if present
        confidence_match = re.search(r'"extraction_confidence":\s*([0-9.]+)', metadata)
        confidence = confidence_match.group(1) if confidence_match else "0.9"
        
        # Add rootfi_id to properties if it's in metadata
        rootfi_id_match = re.search(r'"rootfi_id":\s*([^,]+)', metadata)
        if rootfi_id_match:
            properties += f',\n                    "rootfi_id": {rootfi_id_match.group(1)}'
        
        return f'''await self._create_kudwa_entity(
                entity_type="{entity_type}",
                name={name},
                properties={{
                    {properties}
                }},
                document_id={document_id},
                confidence_score={confidence}
            )'''
    
    # Replace all occurrences
    new_content = re.sub(pattern, replace_call, content, flags=re.DOTALL)
    
    # Also handle simpler patterns without metadata
    simple_pattern = r'await supabase_service\.create_entity\(\s*entity_type="([^"]+)",\s*name=([^,]+),\s*properties=\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\s*\)'
    
    def replace_simple_call(match):
        entity_type = match.group(1)
        name = match.group(2)
        properties = match.group(3)
        
        return f'''await self._create_kudwa_entity(
                entity_type="{entity_type}",
                name={name},
                properties={{
                    {properties}
                }},
                confidence_score=0.9
            )'''
    
    new_content = re.sub(simple_pattern, replace_simple_call, new_content, flags=re.DOTALL)
    
    with open('app/services/data_parser.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed all entity creation calls")

if __name__ == "__main__":
    fix_entity_calls()
