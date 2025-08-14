"""
Supabase client service for database operations
"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    async def create_entity(
        self,
        entity_type: str,
        name: str,
        properties: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        confidence_score: float = 1.0,
        source_document_id: Optional[str] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Create a new entity in the database"""
        try:
            entity_data = {
                "entity_type": entity_type,
                "name": name,
                "properties": properties,
                "metadata": metadata or {},
                "confidence_score": confidence_score,
                "source_document_id": source_document_id,
                "created_by": created_by
            }
            
            result = self.client.table("entities").insert(entity_data).execute()
            
            logger.info(
                "Entity created successfully",
                entity_type=entity_type,
                name=name,
                entity_id=result.data[0]["id"] if result.data else None
            )
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(
                "Failed to create entity",
                entity_type=entity_type,
                name=name,
                error=str(e)
            )
            raise
    
    async def get_entities(
        self,
        entity_types: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve entities from the database"""
        try:
            query = self.client.table("entities").select("*")
            
            if entity_types:
                query = query.in_("entity_type", entity_types)
            
            query = query.eq("status", "active").range(offset, offset + limit - 1)
            result = query.execute()
            
            logger.info(
                "Entities retrieved",
                count=len(result.data) if result.data else 0,
                entity_types=entity_types
            )
            
            return result.data or []
            
        except Exception as e:
            logger.error("Failed to retrieve entities", error=str(e))
            raise
    
    async def search_entities(
        self,
        search_term: str,
        entity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search entities using the database function"""
        try:
            result = self.client.rpc(
                "search_entities",
                {
                    "search_term": search_term,
                    "entity_types": entity_types
                }
            ).execute()
            
            logger.info(
                "Entity search completed",
                search_term=search_term,
                results_count=len(result.data) if result.data else 0
            )
            
            return result.data or []
            
        except Exception as e:
            logger.error(
                "Entity search failed",
                search_term=search_term,
                error=str(e)
            )
            raise
    
    async def create_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        strength: float = 1.0,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Create a relationship between entities"""
        try:
            relationship_data = {
                "source_entity_id": source_entity_id,
                "target_entity_id": target_entity_id,
                "relationship_type": relationship_type,
                "relationship_properties": properties or {},
                "strength": strength,
                "created_by": created_by
            }
            
            result = self.client.table("entity_relationships").insert(relationship_data).execute()
            
            logger.info(
                "Relationship created",
                source_id=source_entity_id,
                target_id=target_entity_id,
                relationship_type=relationship_type
            )
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(
                "Failed to create relationship",
                source_id=source_entity_id,
                target_id=target_entity_id,
                error=str(e)
            )
            raise
    
    async def get_entity_relationships(
        self,
        entity_id: str,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Get relationships for an entity"""
        try:
            result = self.client.rpc(
                "get_entity_relationships",
                {
                    "entity_id": entity_id,
                    "max_depth": max_depth
                }
            ).execute()
            
            logger.info(
                "Entity relationships retrieved",
                entity_id=entity_id,
                relationships_count=len(result.data) if result.data else 0
            )
            
            return result.data or []
            
        except Exception as e:
            logger.error(
                "Failed to get entity relationships",
                entity_id=entity_id,
                error=str(e)
            )
            raise


# Global instance
supabase_service = SupabaseService()
