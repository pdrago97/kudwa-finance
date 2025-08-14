"""
Entity management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog

from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class EntityCreate(BaseModel):
    """Model for creating new entities"""
    entity_type: str
    name: str
    properties: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    confidence_score: float = 1.0
    source_document_id: Optional[str] = None
    created_by: str = "api"


class EntityResponse(BaseModel):
    """Model for entity responses"""
    id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    metadata: Dict[str, Any]
    confidence_score: float
    source_document_id: Optional[str]
    created_at: str
    updated_at: str
    created_by: str
    status: str


class RelationshipCreate(BaseModel):
    """Model for creating entity relationships"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: Optional[Dict[str, Any]] = None
    strength: float = 1.0
    created_by: str = "api"


@router.get("/", response_model=List[EntityResponse])
async def get_entities(
    entity_types: Optional[List[str]] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Retrieve entities from the ontology database
    
    Filter by entity types and paginate results
    """
    try:
        logger.info(
            "Retrieving entities",
            entity_types=entity_types,
            limit=limit,
            offset=offset
        )
        
        entities = await supabase_service.get_entities(
            entity_types=entity_types,
            limit=limit,
            offset=offset
        )
        
        return entities
        
    except Exception as e:
        logger.error("Failed to retrieve entities", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve entities: {str(e)}"
        )


@router.post("/", response_model=EntityResponse)
async def create_entity(entity: EntityCreate):
    """
    Create a new entity in the ontology database
    
    Supports dynamic properties based on entity type
    """
    try:
        logger.info(
            "Creating new entity",
            entity_type=entity.entity_type,
            name=entity.name
        )
        
        created_entity = await supabase_service.create_entity(
            entity_type=entity.entity_type,
            name=entity.name,
            properties=entity.properties,
            metadata=entity.metadata,
            confidence_score=entity.confidence_score,
            source_document_id=entity.source_document_id,
            created_by=entity.created_by
        )
        
        return created_entity
        
    except Exception as e:
        logger.error(
            "Failed to create entity",
            entity_type=entity.entity_type,
            name=entity.name,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create entity: {str(e)}"
        )


@router.get("/search")
async def search_entities(
    q: str = Query(..., description="Search term"),
    entity_types: Optional[List[str]] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Search entities using full-text search
    
    Searches entity names and properties
    """
    try:
        logger.info(
            "Searching entities",
            search_term=q,
            entity_types=entity_types
        )
        
        results = await supabase_service.search_entities(
            search_term=q,
            entity_types=entity_types
        )
        
        # Limit results
        limited_results = results[:limit]
        
        return {
            "results": limited_results,
            "total_found": len(results),
            "search_term": q,
            "entity_types": entity_types
        }
        
    except Exception as e:
        logger.error(
            "Entity search failed",
            search_term=q,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{entity_id}/relationships")
async def get_entity_relationships(
    entity_id: str,
    max_depth: int = Query(2, ge=1, le=5)
):
    """
    Get relationships for a specific entity
    
    Returns direct and indirect relationships up to max_depth
    """
    try:
        logger.info(
            "Retrieving entity relationships",
            entity_id=entity_id,
            max_depth=max_depth
        )
        
        relationships = await supabase_service.get_entity_relationships(
            entity_id=entity_id,
            max_depth=max_depth
        )
        
        return {
            "entity_id": entity_id,
            "relationships": relationships,
            "max_depth": max_depth,
            "total_relationships": len(relationships)
        }
        
    except Exception as e:
        logger.error(
            "Failed to retrieve entity relationships",
            entity_id=entity_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve relationships: {str(e)}"
        )


@router.post("/relationships")
async def create_relationship(relationship: RelationshipCreate):
    """
    Create a relationship between two entities
    """
    try:
        logger.info(
            "Creating entity relationship",
            source_id=relationship.source_entity_id,
            target_id=relationship.target_entity_id,
            relationship_type=relationship.relationship_type
        )
        
        created_relationship = await supabase_service.create_relationship(
            source_entity_id=relationship.source_entity_id,
            target_entity_id=relationship.target_entity_id,
            relationship_type=relationship.relationship_type,
            properties=relationship.properties,
            strength=relationship.strength,
            created_by=relationship.created_by
        )
        
        return created_relationship
        
    except Exception as e:
        logger.error(
            "Failed to create relationship",
            source_id=relationship.source_entity_id,
            target_id=relationship.target_entity_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create relationship: {str(e)}"
        )


@router.get("/types")
async def get_entity_types():
    """
    Get available entity types and their schemas
    """
    entity_type_schemas = {
        "customer": {
            "description": "Customer entities representing individuals or organizations",
            "required_properties": ["customer_type"],
            "optional_properties": [
                "industry", "annual_revenue", "risk_profile", "kyc_status",
                "contact_info", "compliance_flags", "account_manager"
            ],
            "example": {
                "customer_type": "corporate",
                "industry": "fintech",
                "annual_revenue": 1000000,
                "risk_profile": "medium"
            }
        },
        "company": {
            "description": "Company entities for business organizations",
            "required_properties": ["company_type"],
            "optional_properties": [
                "industry_code", "employee_count", "founding_date",
                "legal_structure", "headquarters", "financial_health"
            ],
            "example": {
                "company_type": "startup",
                "industry_code": "NAICS_541511",
                "employee_count": 50
            }
        },
        "payment": {
            "description": "Payment transaction entities",
            "required_properties": ["amount", "currency"],
            "optional_properties": [
                "payment_type", "status", "payment_method", "transaction_fees",
                "risk_assessment", "settlement_info"
            ],
            "example": {
                "amount": 1000.00,
                "currency": "USD",
                "payment_type": "transfer",
                "status": "completed"
            }
        },
        "contract": {
            "description": "Contract and agreement entities",
            "required_properties": ["contract_type"],
            "optional_properties": [
                "contract_status", "effective_date", "expiration_date",
                "terms", "financial_terms", "compliance_requirements"
            ],
            "example": {
                "contract_type": "service_agreement",
                "contract_value": 500000,
                "effective_date": "2024-01-01"
            }
        },
        "role": {
            "description": "Role and permission entities",
            "required_properties": ["role_type"],
            "optional_properties": [
                "permissions", "scope", "assignment_info", "access_controls"
            ],
            "example": {
                "role_type": "admin",
                "permissions": ["read_transactions", "approve_payments"]
            }
        }
    }
    
    return {"entity_types": entity_type_schemas}
