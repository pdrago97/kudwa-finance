"""
Dashboard management and auto-generation endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog

from app.services.supabase_client import supabase_service
from app.services.n8n_client import n8n_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class DashboardConfig(BaseModel):
    """Dashboard configuration model"""
    dashboard_name: str
    entity_types: List[str]
    chart_configs: Dict[str, Any]
    filters: Optional[Dict[str, Any]] = None
    refresh_frequency: str = "real_time"
    auto_generated: bool = True


class DashboardResponse(BaseModel):
    """Dashboard response model"""
    id: str
    dashboard_name: str
    entity_types: List[str]
    chart_configs: Dict[str, Any]
    filters: Dict[str, Any]
    refresh_frequency: str
    auto_generated: bool
    created_at: str
    updated_at: str


@router.get("/", response_model=List[DashboardResponse])
async def get_dashboards(
    entity_types: Optional[List[str]] = Query(None),
    auto_generated: Optional[bool] = None,
    limit: int = Query(50, le=200)
):
    """
    Retrieve dashboard configurations
    """
    try:
        query = supabase_service.client.table("dashboard_configs").select("*")
        
        if entity_types:
            # Filter by entity types (array overlap)
            query = query.overlaps("entity_types", entity_types)
        
        if auto_generated is not None:
            query = query.eq("auto_generated", auto_generated)
        
        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()
        
        logger.info(
            "Retrieved dashboards",
            count=len(result.data) if result.data else 0,
            entity_types=entity_types
        )
        
        return result.data or []
        
    except Exception as e:
        logger.error("Failed to retrieve dashboards", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboards: {str(e)}"
        )


@router.post("/", response_model=DashboardResponse)
async def create_dashboard(config: DashboardConfig):
    """
    Create a new dashboard configuration
    """
    try:
        logger.info(
            "Creating dashboard",
            dashboard_name=config.dashboard_name,
            entity_types=config.entity_types
        )
        
        dashboard_data = {
            "dashboard_name": config.dashboard_name,
            "entity_types": config.entity_types,
            "chart_configs": config.chart_configs,
            "filters": config.filters or {},
            "refresh_frequency": config.refresh_frequency,
            "auto_generated": config.auto_generated,
            "created_by_agent": "manual_creation" if not config.auto_generated else "dashboard_agent"
        }
        
        result = supabase_service.client.table("dashboard_configs").insert(dashboard_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create dashboard")
        
        return result.data[0]
        
    except Exception as e:
        logger.error(
            "Failed to create dashboard",
            dashboard_name=config.dashboard_name,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create dashboard: {str(e)}"
        )


@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """
    Get specific dashboard configuration and data
    """
    try:
        # Get dashboard config
        config_result = supabase_service.client.table("dashboard_configs").select("*").eq("id", dashboard_id).execute()
        
        if not config_result.data:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        dashboard_config = config_result.data[0]
        
        # Get related entities for dashboard data
        entities_query = supabase_service.client.table("entities").select("*")
        
        if dashboard_config["entity_types"]:
            entities_query = entities_query.in_("entity_type", dashboard_config["entity_types"])
        
        entities_result = entities_query.limit(1000).execute()
        
        # Generate dashboard data based on configuration
        dashboard_data = await _generate_dashboard_data(
            dashboard_config,
            entities_result.data or []
        )
        
        return {
            "config": dashboard_config,
            "data": dashboard_data,
            "entity_count": len(entities_result.data) if entities_result.data else 0,
            "last_updated": dashboard_config["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve dashboard", dashboard_id=dashboard_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )


@router.post("/generate")
async def generate_dashboard_from_entities(
    entity_types: List[str],
    dashboard_name: Optional[str] = None,
    user_id: str = "system"
):
    """
    Auto-generate dashboard configuration based on entity types
    """
    try:
        logger.info(
            "Auto-generating dashboard",
            entity_types=entity_types,
            dashboard_name=dashboard_name
        )
        
        # Trigger n8n dashboard generation workflow
        result = await n8n_service.notify_entity_updates(
            event_type="dashboard_generation_request",
            document_id="manual_request",
            new_entities=[],
            ontology_updates={
                "requested_entity_types": entity_types,
                "dashboard_name": dashboard_name or f"Auto Dashboard - {', '.join(entity_types)}",
                "user_id": user_id
            }
        )
        
        return {
            "success": True,
            "message": "Dashboard generation triggered",
            "entity_types": entity_types,
            "workflow_result": result
        }
        
    except Exception as e:
        logger.error(
            "Failed to generate dashboard",
            entity_types=entity_types,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard: {str(e)}"
        )


@router.post("/{dashboard_id}/refresh")
async def refresh_dashboard(dashboard_id: str):
    """
    Refresh dashboard data
    """
    try:
        # Get dashboard config
        config_result = supabase_service.client.table("dashboard_configs").select("*").eq("id", dashboard_id).execute()
        
        if not config_result.data:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        dashboard_config = config_result.data[0]
        
        # Update last refresh timestamp
        supabase_service.client.table("dashboard_configs").update({
            "updated_at": "NOW()"
        }).eq("id", dashboard_id).execute()
        
        logger.info(
            "Dashboard refreshed",
            dashboard_id=dashboard_id,
            dashboard_name=dashboard_config["dashboard_name"]
        )
        
        return {
            "success": True,
            "dashboard_id": dashboard_id,
            "refreshed_at": "NOW()",
            "entity_types": dashboard_config["entity_types"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to refresh dashboard", dashboard_id=dashboard_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh dashboard: {str(e)}"
        )


@router.get("/templates/financial")
async def get_financial_dashboard_templates():
    """
    Get pre-built financial dashboard templates
    """
    templates = [
        {
            "name": "Revenue Analysis Dashboard",
            "description": "Track revenue streams, trends, and performance metrics",
            "entity_types": ["revenue_stream", "revenue_account", "financial_summary"],
            "chart_configs": {
                "revenue_trend": {
                    "type": "line",
                    "title": "Revenue Trend Over Time",
                    "x_axis": "time_period",
                    "y_axis": "amount",
                    "aggregation": "sum"
                },
                "revenue_by_stream": {
                    "type": "pie",
                    "title": "Revenue by Stream",
                    "value_field": "amount",
                    "label_field": "name"
                }
            },
            "filters": {
                "time_range": "last_12_months",
                "currency": "USD"
            }
        },
        {
            "name": "Expense Management Dashboard",
            "description": "Monitor expenses, categories, and cost optimization opportunities",
            "entity_types": ["expense_category", "expense_account", "operating_expenses"],
            "chart_configs": {
                "expense_breakdown": {
                    "type": "bar",
                    "title": "Expenses by Category",
                    "x_axis": "category",
                    "y_axis": "amount",
                    "aggregation": "sum"
                },
                "expense_trend": {
                    "type": "line",
                    "title": "Monthly Expense Trend",
                    "x_axis": "time_period",
                    "y_axis": "amount"
                }
            }
        },
        {
            "name": "Financial Health Overview",
            "description": "Comprehensive view of financial performance and health metrics",
            "entity_types": ["financial_summary", "company", "revenue_stream", "expense_category"],
            "chart_configs": {
                "profit_loss": {
                    "type": "waterfall",
                    "title": "Profit & Loss Breakdown",
                    "categories": ["revenue", "expenses", "profit"]
                },
                "financial_ratios": {
                    "type": "gauge",
                    "title": "Key Financial Ratios",
                    "metrics": ["gross_margin", "operating_margin", "profit_margin"]
                }
            }
        }
    ]
    
    return {"templates": templates}


async def _generate_dashboard_data(
    dashboard_config: Dict[str, Any],
    entities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate dashboard data based on configuration and entities
    """
    chart_configs = dashboard_config.get("chart_configs", {})
    dashboard_data = {}
    
    for chart_name, chart_config in chart_configs.items():
        chart_type = chart_config.get("type", "bar")
        
        if chart_type == "line":
            # Generate time series data
            dashboard_data[chart_name] = _generate_time_series_data(entities, chart_config)
        elif chart_type == "pie":
            # Generate pie chart data
            dashboard_data[chart_name] = _generate_pie_chart_data(entities, chart_config)
        elif chart_type == "bar":
            # Generate bar chart data
            dashboard_data[chart_name] = _generate_bar_chart_data(entities, chart_config)
        else:
            # Default data structure
            dashboard_data[chart_name] = {
                "labels": [],
                "datasets": [],
                "total": 0
            }
    
    return dashboard_data


def _generate_time_series_data(entities: List[Dict], config: Dict) -> Dict[str, Any]:
    """Generate time series data for line charts"""
    # Simplified implementation - would be more sophisticated in production
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "datasets": [{
            "label": config.get("title", "Time Series"),
            "data": [100, 120, 110, 140, 160, 180],
            "borderColor": "rgb(75, 192, 192)",
            "tension": 0.1
        }]
    }


def _generate_pie_chart_data(entities: List[Dict], config: Dict) -> Dict[str, Any]:
    """Generate pie chart data"""
    return {
        "labels": ["Revenue Stream 1", "Revenue Stream 2", "Revenue Stream 3"],
        "datasets": [{
            "data": [300, 200, 100],
            "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56"]
        }]
    }


def _generate_bar_chart_data(entities: List[Dict], config: Dict) -> Dict[str, Any]:
    """Generate bar chart data"""
    return {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{
            "label": config.get("title", "Bar Chart"),
            "data": [65, 59, 80, 81],
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "borderColor": "rgba(54, 162, 235, 1)",
            "borderWidth": 1
        }]
    }
