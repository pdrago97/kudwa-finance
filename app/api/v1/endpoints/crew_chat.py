"""
CrewAI-based chat endpoints for intelligent financial data interaction
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.crew_chat_agent import CrewChatAgent
from agents.rag_graph_manager import RAGGraphManager

logger = structlog.get_logger(__name__)
router = APIRouter()

# Initialize CrewAI components lazily
chat_agent = None
rag_manager = None

def get_chat_agent():
    global chat_agent
    if chat_agent is None:
        chat_agent = CrewChatAgent()
    return chat_agent

def get_rag_manager():
    global rag_manager
    if rag_manager is None:
        rag_manager = RAGGraphManager()
    return rag_manager


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    user_id: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    response: str
    agent_type: str
    query_type: str
    processing_time_ms: Optional[int] = None
    graph_data: Optional[Dict[str, Any]] = None


class SemanticSearchRequest(BaseModel):
    """Semantic search request model"""
    query: str
    top_k: int = 10
    user_id: str


class GraphAnalysisRequest(BaseModel):
    """Graph analysis request model"""
    analysis_type: str = "overview"  # overview, visualization, statistics
    user_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_crew_agent(message: ChatMessage):
    """
    Chat with CrewAI-based financial data agent

    This endpoint provides intelligent responses using multiple specialized agents
    """
    try:
        import time
        import uuid

        start_time = time.time()
        request_id = str(uuid.uuid4())

        logger.info(
            "Processing chat message with CrewAI",
            message=message.message[:100] + "..." if len(message.message) > 100 else message.message,
            user_id=message.user_id,
            request_id=request_id
        )

        # Get chat agent and process message
        agent = get_chat_agent()
        context = {**(message.context or {}), "request_id": request_id}
        result = await agent.process_chat_message(
            message.message,
            context
        )
        
        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            "Chat processing completed",
            request_id=request_id,
            processing_time_ms=processing_time,
            success=result.get("success", False),
            agent_type=result.get("agent_type", "unknown")
        )

        if result.get("success"):
            # Check if response contains visualization spec
            if "gadget_spec" in result:
                return ChatResponse(
                    success=True,
                    response=result["response"],
                    agent_type=result.get("agent_type", "unknown"),
                    query_type=result.get("query_type", "general"),
                    processing_time_ms=processing_time,
                    graph_data=result["gadget_spec"]
                )
            return ChatResponse(
                success=True,
                response=result["response"],
                agent_type=result.get("agent_type", "unknown"),
                query_type=result.get("query_type", "general"),
                processing_time_ms=processing_time
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error occurred")
            )
            
    except Exception as e:
        logger.error(
            "Chat processing failed",
            message=message.message,
            user_id=message.user_id,
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/semantic-search")
async def semantic_search(request: SemanticSearchRequest):
    """
    Perform semantic search across financial data
    
    Uses RAG techniques to find relevant information
    """
    try:
        logger.info(
            "Performing semantic search",
            query=request.query,
            top_k=request.top_k,
            user_id=request.user_id
        )
        
        # Get RAG manager and initialize if needed
        rag_mgr = get_rag_manager()
        if not rag_mgr.embeddings_data:
            await rag_mgr.initialize_vector_index()

        # Perform semantic search
        results = await rag_mgr.semantic_search(request.query, request.top_k)
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(
            "Semantic search failed",
            query=request.query,
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/graph-analysis")
async def analyze_knowledge_graph(request: GraphAnalysisRequest):
    """
    Analyze knowledge graph structure and generate insights
    
    Provides graph statistics, visualizations, and relationship analysis
    """
    try:
        logger.info(
            "Analyzing knowledge graph",
            analysis_type=request.analysis_type,
            user_id=request.user_id
        )
        
        if request.analysis_type == "overview":
            # Build and analyze knowledge graph
            rag_mgr = get_rag_manager()
            graph_result = await rag_mgr.build_knowledge_graph()
            
            return {
                "success": True,
                "analysis_type": "overview",
                "graph_stats": graph_result.get("stats", {}),
                "nodes": graph_result.get("nodes", 0),
                "edges": graph_result.get("edges", 0),
                "graph_data": graph_result.get("graph_data", {})
            }
            
        elif request.analysis_type == "visualization":
            # Generate interactive visualization
            rag_mgr = get_rag_manager()
            viz_path = rag_mgr.generate_interactive_visualization()
            
            return {
                "success": True,
                "analysis_type": "visualization",
                "visualization_path": viz_path,
                "message": "Interactive graph visualization generated"
            }
            
        elif request.analysis_type == "statistics":
            # Get detailed graph statistics
            rag_mgr = get_rag_manager()
            await rag_mgr.build_knowledge_graph()
            stats = rag_mgr._calculate_graph_stats()
            
            return {
                "success": True,
                "analysis_type": "statistics",
                "detailed_stats": stats
            }
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown analysis type: {request.analysis_type}"
            )
            
    except Exception as e:
        logger.error(
            "Graph analysis failed",
            analysis_type=request.analysis_type,
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Graph analysis failed: {str(e)}"
        )


@router.get("/ontology/classes")
async def get_ontology_classes(domain: str = "financial", limit: int = 100):
    """
    Get ontology classes for the specified domain
    """
    try:
        from app.services.supabase_client import SupabaseService
        supabase = SupabaseService()
        
        result = supabase.client.table("kudwa_ontology_classes")\
            .select("class_id, label, domain, class_type, properties, confidence_score, status")\
            .eq("domain", domain)\
            .eq("status", "active")\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "domain": domain,
            "classes": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        logger.error("Failed to get ontology classes", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ontology classes: {str(e)}"
        )


@router.get("/ontology/relationships")
async def get_ontology_relationships(domain: str = "financial", limit: int = 100):
    """
    Get ontology relationships for the specified domain
    """
    try:
        from app.services.supabase_client import SupabaseService
        supabase = SupabaseService()
        
        result = supabase.client.table("kudwa_ontology_relations")\
            .select("subject_class_id, predicate, object_class_id, properties, confidence_score, status")\
            .eq("domain", domain)\
            .eq("status", "active")\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "domain": domain,
            "relationships": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        logger.error("Failed to get ontology relationships", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ontology relationships: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for CrewAI chat service
    """
    try:
        # Test basic functionality
        agent = get_chat_agent()
        rag_mgr = get_rag_manager()
        test_result = await agent._analyze_query("test financial query")

        return {
            "success": True,
            "status": "healthy",
            "agents_initialized": True,
            "rag_manager_ready": len(rag_mgr.embeddings_data) > 0 if rag_mgr.embeddings_data else False,
            "test_query_analysis": test_result
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }
