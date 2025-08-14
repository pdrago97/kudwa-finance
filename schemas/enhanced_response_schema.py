"""
Enhanced Response Schema for Human-in-the-Loop Ontology Evolution
Supports multi-source data integration with AI-proposed ontology extensions
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ProposalType(str, Enum):
    """Types of ontology proposals"""
    ENTITY_CLASS = "entity_class"
    RELATIONSHIP = "relationship"
    PROPERTY = "property"
    INSTANCE = "instance"
    CLUSTER = "cluster"
    VECTOR_EMBEDDING = "vector_embedding"

class ConfidenceLevel(str, Enum):
    """Confidence levels for proposals"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5

class DataSource(BaseModel):
    """Information about the data source"""
    source_type: Literal["json", "pdf", "spreadsheet", "api", "manual"]
    source_id: str
    source_name: str
    ingestion_timestamp: datetime
    metadata: Dict[str, Any] = {}

class OntologyProposal(BaseModel):
    """Individual ontology extension proposal"""
    id: str = Field(..., description="Unique proposal identifier")
    type: ProposalType
    title: str = Field(..., description="Human-readable proposal title")
    description: str = Field(..., description="Detailed description of the proposal")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    confidence_level: ConfidenceLevel
    reasoning: str = Field(..., description="AI reasoning for this proposal")
    
    # Proposed ontology changes
    proposed_changes: Dict[str, Any] = Field(..., description="Structured changes to apply")
    
    # Data evidence
    supporting_data: List[Dict[str, Any]] = Field(default=[], description="Data samples supporting this proposal")
    data_sources: List[DataSource] = Field(default=[], description="Sources of supporting data")
    
    # Impact analysis
    affected_entities: List[str] = Field(default=[], description="Existing entities that would be affected")
    estimated_impact: str = Field(..., description="Estimated impact of accepting this proposal")
    
    # Clustering information
    cluster_info: Optional[Dict[str, Any]] = Field(None, description="Event clustering information")
    
    # Vector embedding data
    embedding_data: Optional[Dict[str, Any]] = Field(None, description="Vector embedding information")
    
    # Human validation
    requires_validation: bool = Field(True, description="Whether human validation is required")
    validation_priority: Literal["high", "medium", "low"] = Field("medium")

class EventCluster(BaseModel):
    """Clustered events from multi-source data"""
    cluster_id: str
    cluster_name: str
    event_count: int
    similarity_score: float
    representative_events: List[Dict[str, Any]]
    proposed_ontology_class: Optional[str] = None
    cluster_metadata: Dict[str, Any] = {}

class VectorEmbedding(BaseModel):
    """Vector embedding for semantic search"""
    embedding_id: str
    entity_id: Optional[str] = None
    text_content: str
    embedding_vector: List[float]
    metadata: Dict[str, Any] = {}
    similarity_threshold: float = 0.7

class DataIntegrationSummary(BaseModel):
    """Summary of data integration results"""
    total_records_processed: int
    successful_integrations: int
    failed_integrations: int
    new_entities_created: int
    existing_entities_updated: int
    clusters_identified: int
    embedding_vectors_created: int

class EnhancedChatResponse(BaseModel):
    """Enhanced chat response with ontology proposals and data integration"""
    
    # Standard response
    response: str = Field(..., description="Natural language response to user")
    tool_used: str = Field(default="ontology_agent", description="AI tool that generated response")
    
    # Ontology proposals
    proposals: List[OntologyProposal] = Field(default=[], description="AI-generated ontology proposals")
    
    # Event clustering results
    event_clusters: List[EventCluster] = Field(default=[], description="Identified event clusters")
    
    # Vector embeddings
    vector_embeddings: List[VectorEmbedding] = Field(default=[], description="Generated vector embeddings")
    
    # Data integration summary
    integration_summary: Optional[DataIntegrationSummary] = None
    
    # Real-time updates
    requires_dashboard_refresh: bool = Field(False, description="Whether dashboard should refresh")
    websocket_updates: List[Dict[str, Any]] = Field(default=[], description="Real-time updates to broadcast")
    
    # Human actions required
    human_actions_required: List[str] = Field(default=[], description="Actions requiring human intervention")
    
    # Metadata
    processing_time_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None

class ProposalAction(BaseModel):
    """User action on a proposal"""
    proposal_id: str
    action: Literal["accept", "deny", "modify"]
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    modification_notes: Optional[str] = None
    custom_changes: Optional[Dict[str, Any]] = None

class OntologyUpdateResult(BaseModel):
    """Result of applying ontology updates"""
    proposal_id: str
    success: bool
    changes_applied: Dict[str, Any]
    entities_created: List[str] = []
    entities_updated: List[str] = []
    relationships_created: List[str] = []
    error_message: Optional[str] = None
    rollback_info: Optional[Dict[str, Any]] = None

# Example usage schemas for different data sources
class JSONDataAnalysis(BaseModel):
    """Analysis results for JSON data like your data1.json"""
    detected_entities: List[Dict[str, Any]]
    proposed_schema: Dict[str, Any]
    time_series_data: Optional[List[Dict[str, Any]]] = None
    financial_metrics: Optional[Dict[str, float]] = None

class MultiSourceIngestionRequest(BaseModel):
    """Request for multi-source data ingestion"""
    data_sources: List[DataSource]
    analysis_focus: List[str] = Field(default=["entities", "relationships", "time_series"])
    ontology_extension_mode: Literal["conservative", "aggressive", "balanced"] = "balanced"
    human_validation_required: bool = True
    clustering_enabled: bool = True
    vector_embedding_enabled: bool = True
