import os
from supabase import create_client, Client
from typing import Optional

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            print(f"Warning: SUPABASE_URL={url}, SUPABASE_SERVICE_KEY={'set' if key else 'not set'}")
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        self.client: Client = create_client(url, key)
    
    def insert_file(self, filename: str, mime: str, size_bytes: int, sha256: str, user_id: str = "default") -> dict:
        """Insert file metadata and return the record"""
        result = self.client.table("kudwa_files").insert({
            "filename": filename,
            "mime": mime,
            "size_bytes": size_bytes,
            "sha256": sha256,
            "user_id": user_id,
            "status": "processing"
        }).execute()
        return result.data[0] if result.data else None
    
    def insert_chunks(self, file_id: str, chunks: list) -> list:
        """Insert text chunks for a file"""
        chunk_records = []
        for i, chunk in enumerate(chunks):
            chunk_records.append({
                "file_id": file_id,
                "chunk_index": i,
                "content": chunk,
                "meta": {}
            })
        
        result = self.client.table("kudwa_chunks").insert(chunk_records).execute()
        return result.data if result.data else []
    
    def insert_vectors(self, chunk_embeddings: list) -> list:
        """Insert embeddings for chunks"""
        vector_records = []
        for chunk_id, embedding in chunk_embeddings:
            vector_records.append({
                "chunk_id": chunk_id,
                "embedding": embedding
            })
        
        result = self.client.table("kudwa_vectors").insert(vector_records).execute()
        return result.data if result.data else []
    
    def insert_proposal(self, proposal_type: str, payload: dict, created_by: str = "system") -> dict:
        """Insert a proposal for human approval"""
        result = self.client.table("kudwa_proposals").insert({
            "type": proposal_type,
            "payload": payload,
            "status": "pending",
            "created_by": created_by
        }).execute()
        return result.data[0] if result.data else None
    
    def get_proposals(self) -> list:
        """Get all proposals"""
        result = self.client.table("kudwa_proposals").select("*").order("created_at", desc=True).execute()
        return result.data if result.data else []

    def get_pending_proposals(self) -> list:
        """Get all pending proposals"""
        result = self.client.table("kudwa_proposals").select("*").eq("status", "pending").execute()
        return result.data if result.data else []

    def get_files(self) -> list:
        """Get all uploaded files"""
        result = self.client.table("kudwa_files").select("*").order("created_at", desc=True).execute()
        return result.data if result.data else []

    def delete_file(self, file_id: str) -> bool:
        """Delete a file and its related data"""
        try:
            # Delete related proposals first
            self.client.table("kudwa_proposals").delete().eq("payload->>source_file_id", file_id).execute()

            # Delete related vectors and chunks
            chunks_result = self.client.table("kudwa_chunks").select("id").eq("file_id", file_id).execute()
            if chunks_result.data:
                chunk_ids = [chunk["id"] for chunk in chunks_result.data]
                for chunk_id in chunk_ids:
                    self.client.table("kudwa_vectors").delete().eq("chunk_id", chunk_id).execute()
                self.client.table("kudwa_chunks").delete().eq("file_id", file_id).execute()

            # Delete the file record
            result = self.client.table("kudwa_files").delete().eq("id", file_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Error deleting file {file_id}: {e}")
            return False
    
    def get_proposal_by_id(self, proposal_id: str) -> dict:
        """Get a specific proposal by ID"""
        try:
            result = self.client.table("kudwa_proposals").select("*").eq("id", proposal_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching proposal: {e}")
            return None

    def update_proposal_status(self, proposal_id: str, status: str, reviewed_by: str = "user") -> dict:
        """Update proposal status"""
        result = self.client.table("kudwa_proposals").update({
            "status": status,
            "reviewed_by": reviewed_by,
            "reviewed_at": "now()"
        }).eq("id", proposal_id).execute()
        return result.data[0] if result.data else None

    def approve_proposal(self, proposal_id: str, action: str, reviewed_by: str = "user") -> dict:
        """Approve or reject a proposal"""
        result = self.client.table("kudwa_proposals").update({
            "status": "approved" if action == "approve" else "rejected",
            "reviewed_by": reviewed_by,
            "reviewed_at": "now()"
        }).eq("id", proposal_id).execute()
        return result.data[0] if result.data else None

    def find_entity_id_by_name(self, entity_name: str) -> str:
        """Find entity UUID by name"""
        try:
            result = self.client.table("kudwa_ontology_entities").select("id").eq("name", entity_name).execute()
            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            print(f"Error finding entity {entity_name}: {e}")
            return None

    def merge_proposal_to_ontology(self, proposal: dict) -> dict:
        """Merge a proposal into the ontology and update its status"""
        try:
            # First merge the proposal
            self.merge_approved_proposal(proposal)

            # Update proposal status to approved
            self.update_proposal_status(proposal["id"], "approved")

            return {
                "success": True,
                "entity_name": proposal.get("payload", {}).get("name", "unknown"),
                "type": proposal.get("type")
            }
        except Exception as e:
            print(f"Error merging proposal to ontology: {e}")
            raise e

    def merge_approved_proposal(self, proposal: dict):
        """Merge an approved proposal into the ontology tables"""
        try:
            proposal_type = proposal.get("type")
            payload = proposal.get("payload", {})

            if proposal_type == "entity":
                # Insert into entities table
                result = self.client.table("kudwa_ontology_entities").insert({
                    "name": payload.get("name"),
                    "properties": payload.get("properties", {})
                }).execute()
                print(f"Successfully merged entity: {payload.get('name')}")

            elif proposal_type == "relation":
                # Find entity UUIDs by name
                source_name = payload.get("source")
                target_name = payload.get("target")

                source_id = self.find_entity_id_by_name(source_name)
                target_id = self.find_entity_id_by_name(target_name)

                if source_id and target_id:
                    # Insert into relations table with proper UUIDs
                    self.client.table("kudwa_ontology_relations").insert({
                        "source_entity_id": source_id,
                        "target_entity_id": target_id,
                        "rel_type": payload.get("rel_type"),
                        "properties": payload.get("properties", {})
                    }).execute()
                    print(f"Successfully merged relation: {source_name} -> {target_name}")
                else:
                    print(f"Skipping relation - entities not found: {source_name} -> {target_name}")

            elif proposal_type == "instance":
                # Find entity UUID by name
                entity_name = payload.get("entity")
                entity_id = self.find_entity_id_by_name(entity_name)

                if entity_id:
                    # Insert into instances table with proper UUID
                    self.client.table("kudwa_instances").insert({
                        "entity_id": entity_id,
                        "properties": payload.get("properties", {})
                    }).execute()
                    print(f"Successfully merged instance for entity: {entity_name}")
                else:
                    print(f"Skipping instance - entity not found: {entity_name}")

        except Exception as e:
            print(f"Error merging proposal {proposal.get('id')}: {e}")
            raise e
    
    def update_file_status(self, file_id: str, status: str):
        """Update file processing status"""
        self.client.table("kudwa_files").update({"status": status}).eq("id", file_id).execute()

    def reset_all_data(self) -> dict:
        """Reset all data in the database - USE WITH CAUTION"""
        try:
            # Delete in order to respect foreign key constraints
            tables_to_clear = [
                "kudwa_vectors",
                "kudwa_chunks",
                "kudwa_instances",
                "kudwa_ontology_relations",
                "kudwa_ontology_entities",
                "kudwa_proposals",
                "kudwa_files",
                "kudwa_widgets",
                "kudwa_messages",
                "kudwa_conversations"
            ]

            results = {}
            for table in tables_to_clear:
                try:
                    # Delete all rows from table
                    result = self.client.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                    deleted_count = len(result.data) if result.data else 0
                    results[table] = deleted_count
                    print(f"Cleared {deleted_count} rows from {table}")
                except Exception as e:
                    print(f"Error clearing {table}: {e}")
                    results[table] = f"Error: {str(e)}"

            return {
                "message": "Database reset completed",
                "results": results,
                "timestamp": "now()"
            }
        except Exception as e:
            return {
                "message": "Database reset failed",
                "error": str(e),
                "timestamp": "now()"
            }

    def get_ontology_entities(self) -> list:
        """Get all approved entities from the ontology"""
        try:
            # Try to get real data from database first
            result = self.client.table("kudwa_ontology_entities").select("*").execute()
            if result.data:
                return result.data
        except Exception as e:
            print(f"Error fetching entities from database: {e}")

        # If no approved entities, show entities from pending proposals for preview
        try:
            proposals = self.get_pending_proposals()
            entities = []
            for proposal in proposals:
                if proposal.get("type") == "entity":
                    payload = proposal.get("payload", {})
                    entities.append({
                        "id": f"pending_{proposal['id']}",
                        "name": payload.get("name", "Unknown"),
                        "properties": payload.get("properties", {}),
                        "status": "pending"
                    })
            return entities
        except Exception as e:
            print(f"Error fetching pending entities: {e}")

        # Return empty list if all fails
        return []

    def get_ontology_relations(self) -> list:
        """Get all approved relations from the ontology"""
        try:
            # Try to get real data from database first
            result = self.client.table("kudwa_ontology_relations").select("*").execute()
            if result.data:
                return result.data
        except Exception as e:
            print(f"Error fetching relations from database: {e}")

        # If no approved relations, show relations from pending proposals for preview
        try:
            proposals = self.get_pending_proposals()
            relations = []
            for proposal in proposals:
                if proposal.get("type") == "relation":
                    payload = proposal.get("payload", {})
                    relations.append({
                        "id": f"pending_{proposal['id']}",
                        "source_entity_id": payload.get("source", "unknown"),
                        "target_entity_id": payload.get("target", "unknown"),
                        "rel_type": payload.get("rel_type", "unknown"),
                        "properties": payload.get("properties", {}),
                        "status": "pending"
                    })
            return relations
        except Exception as e:
            print(f"Error fetching pending relations: {e}")

        # Return empty list if all fails
        return []

    def get_ontology_instances(self) -> list:
        """Get all approved instances from the ontology"""
        try:
            # Try to get real data from database first
            result = self.client.table("kudwa_instances").select("*").execute()
            if result.data:
                return result.data
        except Exception as e:
            print(f"Error fetching instances from database: {e}")

        # If no approved instances, show instances from pending proposals for preview
        try:
            proposals = self.get_pending_proposals()
            instances = []
            for proposal in proposals:
                if proposal.get("type") == "instance":
                    payload = proposal.get("payload", {})
                    instances.append({
                        "id": f"pending_{proposal['id']}",
                        "entity_id": payload.get("entity", "unknown"),
                        "properties": payload.get("properties", {}),
                        "status": "pending"
                    })
            return instances
        except Exception as e:
            print(f"Error fetching pending instances: {e}")

        # Return empty list if all fails
        return []

# Global instance
supabase_service = SupabaseService()
