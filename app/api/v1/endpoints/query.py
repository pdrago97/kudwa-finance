"""
Natural language query endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import structlog

from app.services.n8n_client import n8n_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class NaturalQueryRequest(BaseModel):
    """Request model for natural language queries"""
    query: str
    user_id: str
    entity_types: Optional[List[str]] = None
    time_range: str = "all"
    context: Optional[dict] = None


class QueryResponse(BaseModel):
    """Response model for query results"""
    response: str
    query: str
    session_id: str
    user_id: str
    timestamp: str
    extracted_metrics: dict
    suggested_actions: List[str]
    dashboard_hints: dict


@router.post("/natural", response_model=QueryResponse)
async def natural_language_query(request: NaturalQueryRequest):
    """
    Process natural language queries about financial data
    
    Examples:
    - "What was the total profit in Q1?"
    - "Show me revenue trends for 2024"
    - "Which expense category had the highest increase?"
    - "Compare Q1 and Q2 performance"
    """
    try:
        logger.info(
            "Processing natural language query",
            query=request.query,
            user_id=request.user_id,
            entity_types=request.entity_types
        )
        
        # Trigger n8n financial RAG agent workflow
        result = await n8n_service.trigger_financial_query(
            query=request.query,
            user_id=request.user_id,
            entity_types=request.entity_types,
            time_range=request.time_range
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(
            "Natural language query failed",
            query=request.query,
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


class InsightRequest(BaseModel):
    """Request model for financial insights"""
    entity_types: List[str]
    time_range: str = "last_30_days"
    metrics: Optional[List[str]] = None
    user_id: str


@router.post("/insights")
async def generate_financial_insights(request: InsightRequest):
    """
    Generate AI-powered financial insights and summaries
    
    This endpoint analyzes financial data and provides:
    - Key performance indicators
    - Trend analysis
    - Anomaly detection
    - Automated narratives
    """
    try:
        # Create insight query based on request parameters
        insight_query = f"Generate financial insights for {', '.join(request.entity_types)} over {request.time_range}"
        
        if request.metrics:
            insight_query += f" focusing on {', '.join(request.metrics)}"
        
        logger.info(
            "Generating financial insights",
            entity_types=request.entity_types,
            time_range=request.time_range,
            user_id=request.user_id
        )
        
        # Use the same n8n workflow for insights
        result = await n8n_service.trigger_financial_query(
            query=insight_query,
            user_id=request.user_id,
            entity_types=request.entity_types,
            time_range=request.time_range
        )
        
        return {
            "insights": result.get("response", ""),
            "metrics": result.get("extractedMetrics", {}),
            "recommendations": result.get("suggestedActions", []),
            "timestamp": result.get("timestamp"),
            "entity_types": request.entity_types,
            "time_range": request.time_range
        }
        
    except Exception as e:
        logger.error(
            "Financial insights generation failed",
            entity_types=request.entity_types,
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Insights generation failed: {str(e)}"
        )


@router.get("/suggestions")
async def get_query_suggestions():
    """
    Get suggested queries for financial data exploration
    """
    suggestions = [
        {
            "category": "Revenue Analysis",
            "queries": [
                "What was our total revenue this quarter?",
                "Show me revenue trends by customer type",
                "Which customers contributed the most revenue?",
                "Compare revenue growth year over year"
            ]
        },
        {
            "category": "Payment Analysis",
            "queries": [
                "What's our average payment processing time?",
                "Show me payment failure rates by method",
                "Which payment methods are most popular?",
                "Analyze payment patterns by geography"
            ]
        },
        {
            "category": "Customer Insights",
            "queries": [
                "How many new customers did we acquire this month?",
                "What's the average customer lifetime value?",
                "Show me customer churn analysis",
                "Which customer segments are most profitable?"
            ]
        },
        {
            "category": "Risk & Compliance",
            "queries": [
                "Show me high-risk transactions this week",
                "What's our compliance score by region?",
                "Identify potential AML flags",
                "Analyze transaction velocity patterns"
            ]
        }
    ]
    
    return {"suggestions": suggestions}
