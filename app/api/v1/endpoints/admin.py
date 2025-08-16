"""
Admin API endpoints for system management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from app.services.supabase_client import supabase_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/wipe-database")
async def wipe_database() -> Dict[str, str]:
    """Wipe all data from the database - DANGEROUS OPERATION"""
    try:
        logger.warning("Database wipe requested - clearing all data")
        
        # Clear all tables in correct order (respecting foreign keys)
        # Use a condition that will match all rows since we can't use TRUNCATE via REST API
        
        # Clear observations first (has foreign keys to datasets and documents)
        obs_result = supabase_service.client.table("kudwa_financial_observations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        logger.info(f"Cleared {len(obs_result.data) if obs_result.data else 0} financial observations")
        
        # Clear datasets (has foreign key to documents)
        datasets_result = supabase_service.client.table("kudwa_financial_datasets").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        logger.info(f"Cleared {len(datasets_result.data) if datasets_result.data else 0} datasets")
        
        # Clear ontology relations
        relations_result = supabase_service.client.table("kudwa_ontology_relations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        logger.info(f"Cleared {len(relations_result.data) if relations_result.data else 0} ontology relations")
        
        # Clear ontology classes
        classes_result = supabase_service.client.table("kudwa_ontology_classes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        logger.info(f"Cleared {len(classes_result.data) if classes_result.data else 0} ontology classes")
        
        # Clear documents last
        docs_result = supabase_service.client.table("kudwa_documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        logger.info(f"Cleared {len(docs_result.data) if docs_result.data else 0} documents")
        
        logger.info("Database wipe completed successfully")
        return {"status": "success", "message": "Database wiped successfully"}
        
    except Exception as e:
        logger.error(f"Error wiping database: {e}")
        raise HTTPException(status_code=500, detail=f"Error wiping database: {str(e)}")

@router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """Get system status and statistics"""
    try:
        # Get counts from all tables
        documents_result = supabase_service.client.table("kudwa_documents").select("id", count="exact").execute()
        classes_result = supabase_service.client.table("kudwa_ontology_classes").select("id", count="exact").execute()
        observations_result = supabase_service.client.table("kudwa_financial_observations").select("id", count="exact").execute()
        datasets_result = supabase_service.client.table("kudwa_financial_datasets").select("id", count="exact").execute()
        
        return {
            "status": "operational",
            "database": {
                "documents": documents_result.count or 0,
                "ontology_classes": classes_result.count or 0,
                "financial_observations": observations_result.count or 0,
                "datasets": datasets_result.count or 0
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "database": {
                "documents": 0,
                "ontology_classes": 0,
                "financial_observations": 0,
                "datasets": 0
            }
        }
