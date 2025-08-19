from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv

from app.services.supabase_client import supabase_service
from app.services.embeddings import embedding_service
from app.services.ontology_extractor import ontology_extractor
from app.services.genai_service import genai_service

load_dotenv()

app = FastAPI(title="Kudwa POC Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}

class Proposal(BaseModel):
    id: str
    type: str
    payload: dict
    status: str

@app.post("/api/upload-json")
async def upload_json(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json supported in MVP phase")

    try:
        # Read and parse JSON
        content = await file.read()
        content_str = content.decode('utf-8')
        json_data = json.loads(content_str)

        # Create file hash for deduplication
        file_hash = hashlib.md5(content_str.encode()).hexdigest()
        
        # Store file metadata
        file_id = supabase_service.insert_file(file.filename, file_hash, content_str)
        
        if not file_id:
            return {"message": "File already processed (duplicate)", "file_id": None}

        # Chunk the JSON content for embeddings
        chunks = embedding_service.chunk_text(content_str)
        chunk_records = supabase_service.insert_chunks(file_id, chunks)

        # Generate embeddings (DISABLED - causes token limit issues)
        # if os.getenv("OPENAI_API_KEY"):
        #     try:
        #         embeddings = embedding_service.generate_embeddings(chunks)
        #         supabase_service.update_chunk_embeddings(chunk_records, embeddings)
        #     except Exception as e:
        #         print(f"Embedding generation failed: {e}")

        # Extract ontology proposals
        proposals = ontology_extractor.extract_ontology_proposals(json_data, file_id)
        
        # Store proposals in database
        stored_proposals = []
        for proposal in proposals:
            stored_proposal = supabase_service.insert_proposal(
                proposal_type=proposal["type"],
                payload=proposal["payload"],
                created_by="system"
            )
            if stored_proposal:
                stored_proposals.append(stored_proposal)

        return {
            "message": f"Successfully processed {file.filename}",
            "file_id": file_id,
            "proposals_generated": len(stored_proposals),
            "proposals": stored_proposals
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/proposals")
def get_proposals():
    """Get all pending proposals"""
    try:
        proposals = supabase_service.get_pending_proposals()
        return {"proposals": proposals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: str):
    """Approve a proposal and merge it into the ontology"""
    try:
        # Get the proposal
        proposal = supabase_service.get_proposal_by_id(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        # Merge the proposal into the ontology
        result = supabase_service.merge_proposal_to_ontology(proposal)
        
        return {
            "message": f"Successfully merged {proposal['type']} for {result.get('entity_name', 'entity')}",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ontology/structure")
def get_ontology_structure():
    """Get the current ontology structure counts"""
    try:
        entities = supabase_service.get_ontology_entities()
        relations = supabase_service.get_ontology_relations()
        instances = supabase_service.get_ontology_instances()

        return {
            "entities": len(entities),
            "relations": len(relations),
            "instances": len(instances)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ontology/graph-data")
def get_ontology_graph_data():
    """Get full ontology data for graph visualization"""
    try:
        entities = supabase_service.get_ontology_entities()
        relations = supabase_service.get_ontology_relations()
        instances = supabase_service.get_ontology_instances()

        return {
            "entities": entities,
            "relations": relations,
            "instances": instances
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatInput(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(inp: ChatInput):
    """RAG-enabled chat about ontology data with real GenAI"""
    
    print(f"\n🤖 === CHAT REQUEST STARTED ===")
    print(f"📝 User Message: '{inp.message}'")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    try:
        print(f"\n🔍 STEP 1: Fetching ontology data from Supabase...")
        
        # Get current ontology data for context
        entities = supabase_service.get_ontology_entities()
        relations = supabase_service.get_ontology_relations()
        instances = supabase_service.get_ontology_instances()
        
        print(f"✅ Data fetched: {len(entities)} entities, {len(relations)} relations, {len(instances)} instances")

        print(f"\n🔍 STEP 2: Building ontology context...")
        
        # Build context about the ontology
        context_parts = []

        if entities:
            entity_names = [e.get('name', 'Unknown') for e in entities]
            context_parts.append(f"Available entities: {', '.join(entity_names)}")
            print(f"📊 Processing {len(entities)} entities: {entity_names}")

            # Add entity details
            for entity in entities:
                name = entity.get('name', 'Unknown')
                props = entity.get('properties', {})
                if props:
                    prop_desc = ', '.join([f"{k}: {v}" for k, v in props.items()])
                    context_parts.append(f"Entity '{name}' has properties: {prop_desc}")

        if relations:
            rel_types = list(set([r.get('rel_type', 'unknown') for r in relations]))
            context_parts.append(f"Available relationship types: {', '.join(rel_types)}")
            print(f"🔗 Processing {len(relations)} relations with types: {rel_types}")

            # Add specific relationships
            for relation in relations:
                rel_type = relation.get('rel_type', 'unknown')
                # Try to get entity names from IDs
                source_id = relation.get('source_entity_id')
                target_id = relation.get('target_entity_id')

                source_name = "Unknown"
                target_name = "Unknown"

                for entity in entities:
                    if str(entity.get('id')) == str(source_id):
                        source_name = entity.get('name', 'Unknown')
                    if str(entity.get('id')) == str(target_id):
                        target_name = entity.get('name', 'Unknown')

                context_parts.append(f"Relationship: {source_name} --{rel_type}--> {target_name}")

        if instances:
            context_parts.append(f"Total instances: {len(instances)}")

            # Group instances by entity
            instance_counts = {}
            for instance in instances:
                entity_id = instance.get('entity_id')
                entity_name = "Unknown"

                for entity in entities:
                    if str(entity.get('id')) == str(entity_id):
                        entity_name = entity.get('name', 'Unknown')
                        break

                if entity_name not in instance_counts:
                    instance_counts[entity_name] = 0
                instance_counts[entity_name] += 1

            for entity_name, count in instance_counts.items():
                context_parts.append(f"{count} instances of {entity_name}")

        # Build the full context
        ontology_context = "\n".join(context_parts) if context_parts else "No ontology data available yet."
        print(f"✅ Context built: {len(context_parts)} parts, {len(ontology_context)} characters")

        print(f"\n🔍 STEP 3: Calling GenAI Service...")
        
        # Use real GenAI instead of pattern matching
        result = genai_service.generate_ontology_response(
            user_message=inp.message,
            entities=entities,
            relations=relations,
            instances=instances
        )
        
        print(f"✅ GenAI response received")
        print(f"📝 Response length: {len(result.get('text', ''))}")
        if 'metadata' in result:
            metadata = result['metadata']
            print(f"🤖 Model used: {metadata.get('model', 'unknown')}")
            if 'tokens_used' in metadata:
                print(f"💰 Tokens used: {metadata['tokens_used']}")

        print(f"\n🎯 STEP 4: Response generated")
        print(f"✅ === CHAT REQUEST COMPLETED ===\n")
        
        return result

    except Exception as e:
        print(f"\n❌ === CHAT REQUEST FAILED ===")
        print(f"💥 Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        print(f"📍 Traceback: {traceback.format_exc()}")
        print(f"❌ === END ERROR LOG ===\n")
        
        return {"text": f"I encountered an error while processing your question. Please try again or check if your ontology data is properly loaded.", "widgets": []}

@app.get("/api/debug/raw-data")
async def get_raw_debug_data():
    """Get raw ontology data for debugging - shows exact structure"""
    try:
        entities = supabase_service.get_ontology_entities()
        relations = supabase_service.get_ontology_relations()
        instances = supabase_service.get_ontology_instances()
        
        return {
            "entities": {
                "count": len(entities),
                "data": entities[:3] if entities else [],  # Show first 3 for brevity
                "sample_structure": entities[0] if entities else None
            },
            "relations": {
                "count": len(relations),
                "data": relations[:3] if relations else [],
                "sample_structure": relations[0] if relations else None
            },
            "instances": {
                "count": len(instances),
                "data": instances[:3] if instances else [],
                "sample_structure": instances[0] if instances else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-all-data")
async def reset_all_data():
    """Reset all data in the database - USE WITH CAUTION"""
    try:
        result = supabase_service.reset_all_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
