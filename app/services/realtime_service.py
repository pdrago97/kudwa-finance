"""
Real-time WebSocket service for live updates
Handles document ingestion, RAG chat, and entity operations
"""

import asyncio
import json
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import structlog
from datetime import datetime
import uuid

from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Connection pools by type
        self.document_connections: Dict[str, WebSocket] = {}
        self.rag_chat_connections: Dict[str, WebSocket] = {}
        self.entity_operations_connections: Dict[str, WebSocket] = {}
        self.dashboard_connections: Dict[str, WebSocket] = {}
        
        # User session mapping
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def connect_document_ingestion(self, websocket: WebSocket, user_id: str):
        """Connect to document ingestion stream"""
        await websocket.accept()
        connection_id = f"doc_{user_id}_{uuid.uuid4().hex[:8]}"
        self.document_connections[connection_id] = websocket
        
        logger.info("Document ingestion connection established", 
                   connection_id=connection_id, user_id=user_id)
        
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "service": "document_ingestion",
            "connection_id": connection_id,
            "message": "Ready to receive document uploads and show real-time ontology updates"
        })
        
        return connection_id
    
    async def connect_rag_chat(self, websocket: WebSocket, user_id: str):
        """Connect to RAG chat stream"""
        await websocket.accept()
        connection_id = f"rag_{user_id}_{uuid.uuid4().hex[:8]}"
        self.rag_chat_connections[connection_id] = websocket
        
        # Initialize user session for RAG chat
        self.user_sessions[connection_id] = {
            "user_id": user_id,
            "chat_history": [],
            "context": {},
            "session_start": datetime.now().isoformat()
        }
        
        logger.info("RAG chat connection established", 
                   connection_id=connection_id, user_id=user_id)
        
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "service": "rag_chat",
            "connection_id": connection_id,
            "message": "RAG Chat ready - Ask questions about your financial data!",
            "available_entities": await self._get_available_entity_types()
        })
        
        return connection_id
    
    async def connect_entity_operations(self, websocket: WebSocket, user_id: str):
        """Connect to entity operations stream"""
        await websocket.accept()
        connection_id = f"entity_{user_id}_{uuid.uuid4().hex[:8]}"
        self.entity_operations_connections[connection_id] = websocket
        
        # Initialize user session for entity operations
        self.user_sessions[connection_id] = {
            "user_id": user_id,
            "active_entities": [],
            "operations_history": [],
            "session_start": datetime.now().isoformat()
        }
        
        logger.info("Entity operations connection established", 
                   connection_id=connection_id, user_id=user_id)
        
        # Send user's entities
        user_entities = await self._get_user_entities(user_id)
        
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "service": "entity_operations",
            "connection_id": connection_id,
            "message": "Entity Operations ready - Manage your financial entities!",
            "user_entities": user_entities,
            "entity_count": len(user_entities)
        })
        
        return connection_id
    
    async def connect_dashboard(self, websocket: WebSocket, user_id: str):
        """Connect to dashboard updates stream"""
        await websocket.accept()
        connection_id = f"dash_{user_id}_{uuid.uuid4().hex[:8]}"
        self.dashboard_connections[connection_id] = websocket
        
        logger.info("Dashboard connection established", 
                   connection_id=connection_id, user_id=user_id)
        
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "service": "dashboard",
            "connection_id": connection_id,
            "message": "Dashboard connected - Real-time updates enabled!"
        })
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect and cleanup"""
        # Remove from all connection pools
        self.document_connections.pop(connection_id, None)
        self.rag_chat_connections.pop(connection_id, None)
        self.entity_operations_connections.pop(connection_id, None)
        self.dashboard_connections.pop(connection_id, None)
        
        # Cleanup user session
        self.user_sessions.pop(connection_id, None)
        
        logger.info("Connection disconnected", connection_id=connection_id)
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        websocket = (
            self.document_connections.get(connection_id) or
            self.rag_chat_connections.get(connection_id) or
            self.entity_operations_connections.get(connection_id) or
            self.dashboard_connections.get(connection_id)
        )
        
        if websocket:
            try:
                await websocket.send_text(json.dumps({
                    **message,
                    "timestamp": datetime.now().isoformat(),
                    "connection_id": connection_id
                }))
            except Exception as e:
                logger.error("Failed to send message", 
                           connection_id=connection_id, error=str(e))
                await self.disconnect(connection_id)
    
    async def broadcast_document_update(self, update_data: Dict[str, Any]):
        """Broadcast document processing updates to all document connections"""
        message = {
            "type": "document_update",
            "data": update_data
        }
        
        for connection_id in list(self.document_connections.keys()):
            await self.send_to_connection(connection_id, message)
        
        # Also update dashboards
        await self.broadcast_dashboard_update({
            "trigger": "document_processed",
            "data": update_data
        })
    
    async def broadcast_ontology_update(self, ontology_changes: Dict[str, Any]):
        """Broadcast ontology updates to all relevant connections"""
        message = {
            "type": "ontology_update",
            "changes": ontology_changes
        }
        
        # Notify document ingestion connections
        for connection_id in list(self.document_connections.keys()):
            await self.send_to_connection(connection_id, message)
        
        # Notify RAG chat connections (they need to know about new entities)
        for connection_id in list(self.rag_chat_connections.keys()):
            await self.send_to_connection(connection_id, {
                **message,
                "message": "New entities available for querying!"
            })
        
        # Update dashboards
        await self.broadcast_dashboard_update({
            "trigger": "ontology_updated",
            "changes": ontology_changes
        })
    
    async def broadcast_dashboard_update(self, update_data: Dict[str, Any]):
        """Broadcast dashboard updates"""
        message = {
            "type": "dashboard_update",
            "data": update_data
        }
        
        for connection_id in list(self.dashboard_connections.keys()):
            await self.send_to_connection(connection_id, message)
    
    async def send_rag_response(self, connection_id: str, query: str, response: str, context: Dict[str, Any]):
        """Send RAG chat response"""
        # Update session history
        if connection_id in self.user_sessions:
            self.user_sessions[connection_id]["chat_history"].append({
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "context": context
            })
        
        await self.send_to_connection(connection_id, {
            "type": "rag_response",
            "query": query,
            "response": response,
            "context": context,
            "session_id": connection_id
        })
    
    async def send_entity_operation_result(self, connection_id: str, operation: str, result: Dict[str, Any]):
        """Send entity operation result"""
        # Update session history
        if connection_id in self.user_sessions:
            self.user_sessions[connection_id]["operations_history"].append({
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
        
        await self.send_to_connection(connection_id, {
            "type": "entity_operation_result",
            "operation": operation,
            "result": result
        })
    
    async def _get_available_entity_types(self) -> List[Dict[str, Any]]:
        """Get available entity types for RAG chat"""
        try:
            # Get distinct entity types from database
            result = await supabase_service.client.table("entities").select("entity_type").execute()
            
            if result.data:
                entity_types = list(set([item["entity_type"] for item in result.data]))
                return [{"type": et, "available": True} for et in entity_types]
            
            return []
        except Exception as e:
            logger.error("Failed to get entity types", error=str(e))
            return []
    
    async def _get_user_entities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's entities for entity operations"""
        try:
            # Get entities created by or associated with user
            result = await supabase_service.client.table("entities").select("*").or_(
                f"created_by.eq.{user_id},metadata->>user_id.eq.{user_id}"
            ).limit(50).execute()
            
            return result.data or []
        except Exception as e:
            logger.error("Failed to get user entities", user_id=user_id, error=str(e))
            return []


# Global connection manager instance
connection_manager = ConnectionManager()
