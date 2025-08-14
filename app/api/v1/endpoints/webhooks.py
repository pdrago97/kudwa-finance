"""
Webhook endpoints for n8n integration and real-time updates
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
import json

from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class EntityUpdateWebhook(BaseModel):
    """Webhook payload for entity updates"""
    event_type: str
    document_id: str
    new_entities: List[Dict[str, Any]]
    ontology_updates: Dict[str, Any]
    timestamp: Optional[str] = None


class DashboardUpdateWebhook(BaseModel):
    """Webhook payload for dashboard updates"""
    dashboard_ids: List[str]
    update_type: str
    trigger_event: str
    priority: str = "normal"


@router.post("/entity-updates")
async def handle_entity_updates(
    webhook_data: EntityUpdateWebhook,
    background_tasks: BackgroundTasks
):
    """
    Handle entity update notifications from n8n workflows
    
    This endpoint receives notifications when:
    - New entities are extracted from documents
    - Ontology schema is updated
    - Entity relationships are created
    """
    try:
        logger.info(
            "Received entity update webhook",
            event_type=webhook_data.event_type,
            document_id=webhook_data.document_id,
            entities_count=len(webhook_data.new_entities)
        )
        
        # Process entity updates in background
        background_tasks.add_task(
            _process_entity_updates,
            webhook_data
        )
        
        return {
            "success": True,
            "message": "Entity updates received and queued for processing",
            "event_type": webhook_data.event_type,
            "entities_count": len(webhook_data.new_entities)
        }
        
    except Exception as e:
        logger.error(
            "Failed to handle entity updates webhook",
            event_type=webhook_data.event_type,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process entity updates: {str(e)}"
        )


@router.post("/dashboard-updates")
async def handle_dashboard_updates(
    webhook_data: DashboardUpdateWebhook,
    background_tasks: BackgroundTasks
):
    """
    Handle dashboard update notifications from n8n workflows
    
    This endpoint receives notifications when:
    - Dashboards need to be refreshed
    - New dashboards are auto-generated
    - Dashboard configurations are updated
    """
    try:
        logger.info(
            "Received dashboard update webhook",
            dashboard_ids=webhook_data.dashboard_ids,
            update_type=webhook_data.update_type,
            trigger_event=webhook_data.trigger_event
        )
        
        # Process dashboard updates in background
        background_tasks.add_task(
            _process_dashboard_updates,
            webhook_data
        )
        
        return {
            "success": True,
            "message": "Dashboard updates received and queued for processing",
            "dashboard_count": len(webhook_data.dashboard_ids),
            "update_type": webhook_data.update_type
        }
        
    except Exception as e:
        logger.error(
            "Failed to handle dashboard updates webhook",
            dashboard_ids=webhook_data.dashboard_ids,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process dashboard updates: {str(e)}"
        )


@router.post("/n8n-workflow-status")
async def handle_workflow_status(request: Request):
    """
    Handle workflow status updates from n8n
    
    Generic endpoint for receiving workflow execution status
    """
    try:
        body = await request.json()
        
        workflow_id = body.get("workflow_id")
        execution_id = body.get("execution_id")
        status = body.get("status")
        
        logger.info(
            "Received n8n workflow status",
            workflow_id=workflow_id,
            execution_id=execution_id,
            status=status
        )
        
        # Store workflow execution status
        await supabase_service.client.table("workflow_executions").insert({
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "status": status,
            "payload": body,
            "received_at": "NOW()"
        }).execute()
        
        return {
            "success": True,
            "message": "Workflow status received",
            "workflow_id": workflow_id,
            "status": status
        }
        
    except Exception as e:
        logger.error("Failed to handle workflow status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process workflow status: {str(e)}"
        )


@router.post("/supabase-realtime")
async def handle_supabase_realtime(request: Request):
    """
    Handle real-time updates from Supabase
    
    This endpoint can be used to trigger additional processing
    when data changes in Supabase
    """
    try:
        body = await request.json()
        
        table = body.get("table")
        event_type = body.get("type")  # INSERT, UPDATE, DELETE
        record = body.get("record")
        old_record = body.get("old_record")
        
        logger.info(
            "Received Supabase real-time update",
            table=table,
            event_type=event_type,
            record_id=record.get("id") if record else None
        )
        
        # Handle different table updates
        if table == "entities" and event_type == "INSERT":
            # New entity created - might trigger dashboard updates
            await _handle_new_entity_created(record)
        elif table == "dashboard_configs" and event_type in ["INSERT", "UPDATE"]:
            # Dashboard configuration changed
            await _handle_dashboard_config_changed(record, event_type)
        
        return {
            "success": True,
            "message": "Real-time update processed",
            "table": table,
            "event_type": event_type
        }
        
    except Exception as e:
        logger.error("Failed to handle Supabase real-time update", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process real-time update: {str(e)}"
        )


@router.get("/health")
async def webhook_health_check():
    """
    Health check endpoint for webhook services
    """
    return {
        "status": "healthy",
        "service": "webhook_handler",
        "endpoints": [
            "/entity-updates",
            "/dashboard-updates", 
            "/n8n-workflow-status",
            "/supabase-realtime"
        ]
    }


async def _process_entity_updates(webhook_data: EntityUpdateWebhook):
    """
    Background task to process entity updates
    """
    try:
        logger.info(
            "Processing entity updates in background",
            event_type=webhook_data.event_type,
            document_id=webhook_data.document_id
        )
        
        # Update document processing status
        await supabase_service.client.table("documents").update({
            "processing_status": "completed",
            "extracted_entities": webhook_data.new_entities,
            "processed_at": "NOW()"
        }).eq("id", webhook_data.document_id).execute()
        
        # Check if any dashboards need updates based on new entities
        entity_types = list(set([entity.get("entity_type") for entity in webhook_data.new_entities]))
        
        if entity_types:
            # Find dashboards that use these entity types
            dashboards_result = await supabase_service.client.table("dashboard_configs").select("*").overlaps("entity_types", entity_types).execute()
            
            if dashboards_result.data:
                logger.info(
                    "Found dashboards to update",
                    dashboard_count=len(dashboards_result.data),
                    entity_types=entity_types
                )
                
                # Update dashboard timestamps to trigger refresh
                for dashboard in dashboards_result.data:
                    await supabase_service.client.table("dashboard_configs").update({
                        "updated_at": "NOW()"
                    }).eq("id", dashboard["id"]).execute()
        
        logger.info("Entity updates processing completed")
        
    except Exception as e:
        logger.error(
            "Failed to process entity updates in background",
            document_id=webhook_data.document_id,
            error=str(e)
        )


async def _process_dashboard_updates(webhook_data: DashboardUpdateWebhook):
    """
    Background task to process dashboard updates
    """
    try:
        logger.info(
            "Processing dashboard updates in background",
            dashboard_ids=webhook_data.dashboard_ids,
            update_type=webhook_data.update_type
        )
        
        for dashboard_id in webhook_data.dashboard_ids:
            # Update dashboard timestamp
            await supabase_service.client.table("dashboard_configs").update({
                "updated_at": "NOW()"
            }).eq("id", dashboard_id).execute()
        
        logger.info("Dashboard updates processing completed")
        
    except Exception as e:
        logger.error(
            "Failed to process dashboard updates in background",
            dashboard_ids=webhook_data.dashboard_ids,
            error=str(e)
        )


async def _handle_new_entity_created(entity_record: Dict[str, Any]):
    """
    Handle new entity creation from Supabase real-time
    """
    try:
        entity_type = entity_record.get("entity_type")
        
        # Check if any auto-generated dashboards should include this entity type
        dashboards_result = await supabase_service.client.table("dashboard_configs").select("*").contains("entity_types", [entity_type]).eq("auto_generated", True).execute()
        
        if dashboards_result.data:
            logger.info(
                "Updating auto-generated dashboards for new entity",
                entity_type=entity_type,
                dashboard_count=len(dashboards_result.data)
            )
            
            for dashboard in dashboards_result.data:
                await supabase_service.client.table("dashboard_configs").update({
                    "updated_at": "NOW()"
                }).eq("id", dashboard["id"]).execute()
        
    except Exception as e:
        logger.error(
            "Failed to handle new entity creation",
            entity_id=entity_record.get("id"),
            error=str(e)
        )


async def _handle_dashboard_config_changed(dashboard_record: Dict[str, Any], event_type: str):
    """
    Handle dashboard configuration changes
    """
    try:
        dashboard_id = dashboard_record.get("id")
        dashboard_name = dashboard_record.get("dashboard_name")
        
        logger.info(
            "Dashboard configuration changed",
            dashboard_id=dashboard_id,
            dashboard_name=dashboard_name,
            event_type=event_type
        )
        
        # Could trigger additional processing here
        # For example, validate configuration, update related dashboards, etc.
        
    except Exception as e:
        logger.error(
            "Failed to handle dashboard config change",
            dashboard_id=dashboard_record.get("id"),
            error=str(e)
        )
