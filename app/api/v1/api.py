"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import entities, query, documents, dashboards, webhooks, realtime, crew_chat, dashboard, admin, agno_chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(realtime.router, prefix="/realtime", tags=["realtime"])
api_router.include_router(crew_chat.router, prefix="/crew", tags=["crew-ai"])
api_router.include_router(agno_chat.router, prefix="/agno", tags=["agno-ai"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(dashboard.router, prefix="/ontology", tags=["ontology"])
api_router.include_router(dashboard.router, prefix="/chat", tags=["chat"])
