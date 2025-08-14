"""
Real-time WebSocket endpoints for live demo
Handles document ingestion, RAG chat, and entity operations
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import json
import structlog
import asyncio

from app.services.realtime_service import connection_manager
from app.services.data_parser import financial_parser
from app.services.n8n_client import n8n_service
from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.websocket("/document-ingestion")
async def websocket_document_ingestion(
    websocket: WebSocket,
    user_id: str = Query(...)
):
    """
    WebSocket endpoint for real-time document ingestion and ontology updates
    
    Clients receive:
    - Document processing status
    - Entity extraction results
    - Ontology schema updates
    - Dashboard refresh notifications
    """
    connection_id = await connection_manager.connect_document_ingestion(websocket, user_id)
    
    try:
        while True:
            # Wait for document upload notifications or commands
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "process_document":
                await handle_document_processing(connection_id, message, user_id)
            elif message.get("type") == "get_ontology_status":
                await send_ontology_status(connection_id)
            elif message.get("type") == "ping":
                await connection_manager.send_to_connection(connection_id, {
                    "type": "pong",
                    "message": "Document ingestion service is active"
                })
                
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error("Document ingestion WebSocket error", 
                    connection_id=connection_id, error=str(e))
        await connection_manager.disconnect(connection_id)


@router.websocket("/rag-chat")
async def websocket_rag_chat(
    websocket: WebSocket,
    user_id: str = Query(...)
):
    """
    WebSocket endpoint for RAG-based chat about current ontology
    
    Clients can:
    - Ask questions about financial data
    - Get real-time responses with context
    - Receive notifications about new data availability
    """
    connection_id = await connection_manager.connect_rag_chat(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "chat_query":
                await handle_rag_query(connection_id, message, user_id)
            elif message.get("type") == "get_context":
                await send_chat_context(connection_id)
            elif message.get("type") == "clear_history":
                await clear_chat_history(connection_id)
            elif message.get("type") == "ping":
                await connection_manager.send_to_connection(connection_id, {
                    "type": "pong",
                    "message": "RAG chat service is active"
                })
                
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error("RAG chat WebSocket error", 
                    connection_id=connection_id, error=str(e))
        await connection_manager.disconnect(connection_id)


@router.websocket("/entity-operations")
async def websocket_entity_operations(
    websocket: WebSocket,
    user_id: str = Query(...)
):
    """
    WebSocket endpoint for user-specific entity operations
    
    Clients can:
    - View their entities
    - Create/update/delete entities
    - Manage entity relationships
    - Get real-time operation results
    """
    connection_id = await connection_manager.connect_entity_operations(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "create_entity":
                await handle_entity_creation(connection_id, message, user_id)
            elif message.get("type") == "update_entity":
                await handle_entity_update(connection_id, message, user_id)
            elif message.get("type") == "delete_entity":
                await handle_entity_deletion(connection_id, message, user_id)
            elif message.get("type") == "get_my_entities":
                await send_user_entities(connection_id, user_id)
            elif message.get("type") == "create_relationship":
                await handle_relationship_creation(connection_id, message, user_id)
            elif message.get("type") == "ping":
                await connection_manager.send_to_connection(connection_id, {
                    "type": "pong",
                    "message": "Entity operations service is active"
                })
                
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error("Entity operations WebSocket error", 
                    connection_id=connection_id, error=str(e))
        await connection_manager.disconnect(connection_id)


@router.websocket("/dashboard")
async def websocket_dashboard(
    websocket: WebSocket,
    user_id: str = Query(...)
):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Clients receive:
    - Dashboard data updates
    - New chart configurations
    - Real-time metrics
    """
    connection_id = await connection_manager.connect_dashboard(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "get_dashboard_data":
                await send_dashboard_data(connection_id, message.get("dashboard_id"))
            elif message.get("type") == "subscribe_metrics":
                await subscribe_to_metrics(connection_id, message.get("metrics", []))
            elif message.get("type") == "ping":
                await connection_manager.send_to_connection(connection_id, {
                    "type": "pong",
                    "message": "Dashboard service is active"
                })
                
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error("Dashboard WebSocket error", 
                    connection_id=connection_id, error=str(e))
        await connection_manager.disconnect(connection_id)


# Handler functions

async def handle_document_processing(connection_id: str, message: dict, user_id: str):
    """Handle document processing request"""
    try:
        document_data = message.get("document_data")
        source_format = message.get("source_format", "generic_json")
        
        # Send processing started notification
        await connection_manager.send_to_connection(connection_id, {
            "type": "processing_started",
            "message": "Document processing initiated...",
            "source_format": source_format
        })
        
        # Parse the document
        parsing_result = await financial_parser.parse_financial_data(
            data=document_data,
            source_format=source_format,
            document_id=f"realtime_{connection_id}"
        )
        
        # Send parsing results
        await connection_manager.send_to_connection(connection_id, {
            "type": "parsing_completed",
            "entities_extracted": parsing_result["total_entities_extracted"],
            "data_quality_score": parsing_result["parsing_metadata"]["data_quality_score"],
            "new_entity_types": list(set([e.get("entity_type") for e in parsing_result["financial_entities"]]))
        })
        
        # Broadcast ontology update
        await connection_manager.broadcast_ontology_update({
            "new_entities": parsing_result["total_entities_extracted"],
            "source": source_format,
            "trigger": "document_processing"
        })
        
        # Trigger n8n workflows
        try:
            await n8n_service.notify_entity_updates(
                event_type="realtime_document_processed",
                document_id=f"realtime_{connection_id}",
                new_entities=parsing_result["financial_entities"],
                ontology_updates={"realtime": True}
            )
        except Exception as e:
            logger.warning("Failed to trigger n8n workflows", error=str(e))
        
    except Exception as e:
        await connection_manager.send_to_connection(connection_id, {
            "type": "processing_error",
            "error": str(e),
            "message": "Document processing failed"
        })


async def handle_rag_query(connection_id: str, message: dict, user_id: str):
    """Handle RAG chat query"""
    try:
        query = message.get("query")
        entity_types = message.get("entity_types", [])
        
        # Send query received notification
        await connection_manager.send_to_connection(connection_id, {
            "type": "query_received",
            "query": query,
            "message": "Processing your question..."
        })
        
        # Trigger n8n RAG workflow
        try:
            rag_result = await n8n_service.trigger_financial_query(
                query=query,
                user_id=user_id,
                entity_types=entity_types,
                time_range="all"
            )
            
            # Send response
            await connection_manager.send_rag_response(
                connection_id=connection_id,
                query=query,
                response=rag_result.get("response", "I couldn't process that query right now."),
                context={
                    "entities_used": entity_types,
                    "confidence": rag_result.get("confidence", 0.5),
                    "sources": rag_result.get("sources", [])
                }
            )
            
        except Exception as e:
            # Fallback to simple entity search
            search_results = await supabase_service.search_entities(
                search_term=query,
                entity_types=entity_types if entity_types else None
            )
            
            response = f"Found {len(search_results)} entities related to your query. "
            if search_results:
                response += f"Top results: {', '.join([r.get('name', 'Unknown') for r in search_results[:3]])}"
            
            await connection_manager.send_rag_response(
                connection_id=connection_id,
                query=query,
                response=response,
                context={"fallback_search": True, "results_count": len(search_results)}
            )
        
    except Exception as e:
        await connection_manager.send_to_connection(connection_id, {
            "type": "query_error",
            "error": str(e),
            "message": "Failed to process your query"
        })


async def handle_entity_creation(connection_id: str, message: dict, user_id: str):
    """Handle entity creation request"""
    try:
        entity_data = message.get("entity_data")
        
        # Create entity
        created_entity = await supabase_service.create_entity(
            entity_type=entity_data["entity_type"],
            name=entity_data["name"],
            properties=entity_data.get("properties", {}),
            metadata={**entity_data.get("metadata", {}), "user_id": user_id},
            created_by=user_id
        )
        
        # Send result
        await connection_manager.send_entity_operation_result(
            connection_id=connection_id,
            operation="create_entity",
            result={
                "success": True,
                "entity": created_entity,
                "message": f"Entity '{entity_data['name']}' created successfully"
            }
        )
        
        # Broadcast ontology update
        await connection_manager.broadcast_ontology_update({
            "new_entity": created_entity,
            "operation": "create",
            "user_id": user_id
        })
        
    except Exception as e:
        await connection_manager.send_entity_operation_result(
            connection_id=connection_id,
            operation="create_entity",
            result={
                "success": False,
                "error": str(e),
                "message": "Failed to create entity"
            }
        )


async def send_ontology_status(connection_id: str):
    """Send current ontology status"""
    try:
        # Get entity counts by type
        result = await supabase_service.client.table("entities").select("entity_type").execute()
        
        entity_counts = {}
        if result.data:
            for item in result.data:
                entity_type = item["entity_type"]
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        await connection_manager.send_to_connection(connection_id, {
            "type": "ontology_status",
            "entity_counts": entity_counts,
            "total_entities": sum(entity_counts.values()),
            "entity_types": list(entity_counts.keys())
        })
        
    except Exception as e:
        logger.error("Failed to send ontology status", error=str(e))


async def send_user_entities(connection_id: str, user_id: str):
    """Send user's entities"""
    try:
        entities = await connection_manager._get_user_entities(user_id)
        
        await connection_manager.send_to_connection(connection_id, {
            "type": "user_entities",
            "entities": entities,
            "count": len(entities)
        })
        
    except Exception as e:
        logger.error("Failed to send user entities", error=str(e))


async def send_dashboard_data(connection_id: str, dashboard_id: Optional[str]):
    """Send dashboard data"""
    try:
        if dashboard_id:
            # Get specific dashboard
            result = await supabase_service.client.table("dashboard_configs").select("*").eq("id", dashboard_id).execute()
            dashboards = result.data or []
        else:
            # Get all dashboards
            result = await supabase_service.client.table("dashboard_configs").select("*").limit(10).execute()
            dashboards = result.data or []
        
        await connection_manager.send_to_connection(connection_id, {
            "type": "dashboard_data",
            "dashboards": dashboards,
            "count": len(dashboards)
        })
        
    except Exception as e:
        logger.error("Failed to send dashboard data", error=str(e))


# Additional handler functions would continue here...
