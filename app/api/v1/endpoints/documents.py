"""
Document processing and data ingestion endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import structlog

from app.services.data_parser import financial_parser
from app.services.n8n_client import n8n_service
from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class DataIngestionRequest(BaseModel):
    """Request model for data ingestion"""
    data: Dict[str, Any]
    source_format: str  # "quickbooks_pl", "rootfi_api", "generic_json"
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class DataIngestionResponse(BaseModel):
    """Response model for data ingestion"""
    success: bool
    document_id: str
    entities_extracted: int
    parsing_metadata: Dict[str, Any]
    data_quality_score: float
    processing_time_ms: int


@router.post("/ingest", response_model=DataIngestionResponse)
async def ingest_financial_data(request: DataIngestionRequest):
    """
    Ingest and parse financial data from various sources
    
    Supports:
    - QuickBooks Profit & Loss reports
    - Rootfi API financial data
    - Generic JSON financial data
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(
            "Starting financial data ingestion",
            source_format=request.source_format,
            user_id=request.user_id,
            data_size=len(str(request.data))
        )
        
        # Generate document ID
        import uuid
        document_id = str(uuid.uuid4())
        
        # Parse the financial data
        parsing_result = await financial_parser.parse_financial_data(
            data=request.data,
            source_format=request.source_format,
            document_id=document_id
        )
        
        # Store document metadata
        await supabase_service.client.table("documents").insert({
            "id": document_id,
            "filename": f"{request.source_format}_data_{document_id[:8]}.json",
            "content_type": "application/json",
            "file_size": len(str(request.data)),
            "content": json.dumps(request.data),
            "processing_status": "completed",
            "extracted_entities": parsing_result["financial_entities"],
            "processed_at": parsing_result["parsing_metadata"]["parsing_timestamp"],
            "uploaded_by": request.user_id
        }).execute()
        
        # Trigger n8n workflows for further processing
        try:
            await n8n_service.notify_entity_updates(
                event_type="data_ingested",
                document_id=document_id,
                new_entities=parsing_result["financial_entities"],
                ontology_updates={
                    "source_format": request.source_format,
                    "entities_count": parsing_result["total_entities_extracted"]
                }
            )
        except Exception as e:
            logger.warning("Failed to trigger n8n workflows", error=str(e))
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Financial data ingestion completed",
            document_id=document_id,
            entities_extracted=parsing_result["total_entities_extracted"],
            processing_time_ms=processing_time
        )
        
        return DataIngestionResponse(
            success=True,
            document_id=document_id,
            entities_extracted=parsing_result["total_entities_extracted"],
            parsing_metadata=parsing_result["parsing_metadata"],
            data_quality_score=parsing_result["parsing_metadata"]["data_quality_score"],
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(
            "Financial data ingestion failed",
            source_format=request.source_format,
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Data ingestion failed: {str(e)}"
        )


@router.post("/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    source_format: str = Form(...),
    user_id: str = Form(...)
):
    """
    Upload and process financial documents
    
    Supports JSON files with financial data
    """
    try:
        logger.info(
            "Processing uploaded financial document",
            filename=file.filename,
            content_type=file.content_type,
            source_format=source_format,
            user_id=user_id
        )
        
        # Read file content
        content = await file.read()
        
        # Parse JSON content
        try:
            data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # Process through data ingestion
        ingestion_request = DataIngestionRequest(
            data=data,
            source_format=source_format,
            user_id=user_id,
            metadata={
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(content)
            }
        )
        
        result = await ingest_financial_data(ingestion_request)
        
        # Also trigger n8n document processing workflow
        try:
            await n8n_service.trigger_document_processing(
                file_data=content,
                filename=file.filename,
                user_id=user_id,
                document_type="financial",
                expected_entities=["revenue", "expense", "account", "company"]
            )
        except Exception as e:
            logger.warning("Failed to trigger n8n document processing", error=str(e))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Document upload failed",
            filename=file.filename,
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/")
async def get_documents(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """
    Retrieve processed documents
    """
    try:
        query = supabase_service.client.table("documents").select("*")
        
        if user_id:
            query = query.eq("uploaded_by", user_id)
        
        if status:
            query = query.eq("processing_status", status)
        
        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()
        
        return {
            "documents": result.data or [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error("Failed to retrieve documents", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get specific document details
    """
    try:
        result = supabase_service.client.table("documents").select("*").eq("id", document_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        # Get related entities
        entities_result = supabase_service.client.table("entities").select("*").eq("source_document_id", document_id).execute()
        
        return {
            "document": document,
            "related_entities": entities_result.data or [],
            "entity_count": len(entities_result.data) if entities_result.data else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve document", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.post("/sample-data")
async def load_sample_data(user_id: str = "demo_user"):
    """
    Load sample financial data for testing and demonstration
    """
    try:
        # Load data1.json (QuickBooks)
        with open("data1.json", "r") as f:
            quickbooks_data = json.load(f)
        
        qb_result = await ingest_financial_data(DataIngestionRequest(
            data=quickbooks_data,
            source_format="quickbooks_pl",
            user_id=user_id,
            metadata={"sample_data": True, "source": "data1.json"}
        ))
        
        # Load data2.json (Rootfi)
        with open("data2.json", "r") as f:
            rootfi_data = json.load(f)
        
        rootfi_result = await ingest_financial_data(DataIngestionRequest(
            data=rootfi_data,
            source_format="rootfi_api",
            user_id=user_id,
            metadata={"sample_data": True, "source": "data2.json"}
        ))
        
        return {
            "success": True,
            "quickbooks_result": qb_result,
            "rootfi_result": rootfi_result,
            "total_entities": qb_result.entities_extracted + rootfi_result.entities_extracted
        }
        
    except Exception as e:
        logger.error("Failed to load sample data", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load sample data: {str(e)}"
        )
