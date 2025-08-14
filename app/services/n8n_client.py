"""
n8n client service for triggering workflows and agents
"""

import httpx
import structlog
from typing import Dict, Any, Optional
from app.core.config import settings

logger = structlog.get_logger(__name__)


class N8nService:
    """Service for interacting with n8n workflows"""
    
    def __init__(self):
        self.base_url = settings.N8N_WEBHOOK_BASE_URL
        self.api_key = settings.N8N_API_KEY
        self.headers = {}
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def trigger_financial_query(
        self,
        query: str,
        user_id: str,
        entity_types: Optional[list] = None,
        time_range: str = "all"
    ) -> Dict[str, Any]:
        """Trigger the financial RAG agent workflow"""
        try:
            payload = {
                "query": query,
                "user_id": user_id,
                "entity_types": entity_types or [],
                "time_range": time_range
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/financial-query",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                
                logger.info(
                    "Financial query triggered successfully",
                    query=query,
                    user_id=user_id,
                    response_length=len(result.get("response", ""))
                )
                
                return result
                
        except Exception as e:
            logger.error(
                "Failed to trigger financial query",
                query=query,
                user_id=user_id,
                error=str(e)
            )
            raise
    
    async def trigger_document_processing(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
        document_type: str = "financial",
        expected_entities: Optional[list] = None
    ) -> Dict[str, Any]:
        """Trigger the document processing workflow"""
        try:
            files = {
                "file": (filename, file_data, "application/octet-stream")
            }
            
            data = {
                "user_id": user_id,
                "document_type": document_type,
                "expected_entities": expected_entities or ["customer", "payment", "contract"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/process-document",
                    files=files,
                    data=data,
                    headers=self.headers,
                    timeout=60.0
                )
                response.raise_for_status()
                
                result = response.json()
                
                logger.info(
                    "Document processing triggered successfully",
                    filename=filename,
                    user_id=user_id,
                    entities_extracted=result.get("entitiesExtracted", 0)
                )
                
                return result
                
        except Exception as e:
            logger.error(
                "Failed to trigger document processing",
                filename=filename,
                user_id=user_id,
                error=str(e)
            )
            raise
    
    async def notify_entity_updates(
        self,
        event_type: str,
        document_id: str,
        new_entities: list,
        ontology_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Notify dashboard generation agent of entity updates"""
        try:
            payload = {
                "event_type": event_type,
                "document_id": document_id,
                "new_entities": new_entities,
                "ontology_updates": ontology_updates
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/entity-updates",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                
                logger.info(
                    "Entity update notification sent successfully",
                    event_type=event_type,
                    document_id=document_id,
                    dashboards_updated=result.get("dashboardsUpdated", [])
                )
                
                return result
                
        except Exception as e:
            logger.error(
                "Failed to notify entity updates",
                event_type=event_type,
                document_id=document_id,
                error=str(e)
            )
            raise
    
    async def trigger_compliance_check(
        self,
        entity_id: str,
        entity_type: str,
        compliance_rules: Optional[list] = None
    ) -> Dict[str, Any]:
        """Trigger compliance monitoring workflow"""
        try:
            payload = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "compliance_rules": compliance_rules or ["aml", "kyc", "sanctions"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/compliance-check",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                
                logger.info(
                    "Compliance check triggered successfully",
                    entity_id=entity_id,
                    entity_type=entity_type,
                    compliance_status=result.get("status", "unknown")
                )
                
                return result
                
        except Exception as e:
            logger.error(
                "Failed to trigger compliance check",
                entity_id=entity_id,
                entity_type=entity_type,
                error=str(e)
            )
            raise


# Global instance
n8n_service = N8nService()
