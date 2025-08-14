"""
Enhanced Ontology Agent for Multi-Source Data Analysis
Analyzes data like data1.json and generates structured ontology proposals
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from openai import OpenAI
import os
from dotenv import load_dotenv

from schemas.enhanced_response_schema import (
    EnhancedChatResponse, OntologyProposal, ProposalType, ConfidenceLevel,
    DataSource, EventCluster, VectorEmbedding, DataIntegrationSummary,
    JSONDataAnalysis
)

load_dotenv()

class EnhancedOntologyAgent:
    """Enhanced agent for analyzing multi-source data and proposing ontology extensions"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
    async def analyze_json_data(self, json_data: Dict[str, Any], source_info: DataSource) -> JSONDataAnalysis:
        """Analyze JSON data structure and extract entities"""
        
        # Extract financial data from your data1.json structure
        detected_entities = []
        proposed_schema = {}
        time_series_data = []
        financial_metrics = {}
        
        if "data" in json_data:
            data = json_data["data"]
            
            # Analyze header information
            if "Header" in data:
                header = data["Header"]
                detected_entities.append({
                    "type": "financial_report",
                    "properties": {
                        "report_name": header.get("ReportName"),
                        "report_basis": header.get("ReportBasis"),
                        "currency": header.get("Currency"),
                        "start_period": header.get("StartPeriod"),
                        "end_period": header.get("EndPeriod")
                    }
                })
            
            # Analyze column structure for time series
            if "Columns" in data and "Column" in data["Columns"]:
                columns = data["Columns"]["Column"]
                for col in columns:
                    if col.get("ColType") == "Money" and "MetaData" in col:
                        metadata = {item["Name"]: item["Value"] for item in col["MetaData"]}
                        if "StartDate" in metadata and "EndDate" in metadata:
                            time_series_data.append({
                                "period": col.get("ColTitle"),
                                "start_date": metadata["StartDate"],
                                "end_date": metadata["EndDate"]
                            })
            
            # Analyze rows for financial line items
            if "Rows" in data and "Row" in data["Rows"]:
                rows = data["Rows"]["Row"]
                for row in rows:
                    if "ColData" in row:
                        col_data = row["ColData"]
                        account_name = None
                        amounts = {}
                        
                        for i, col in enumerate(col_data):
                            if i == 0 and "value" in col:  # First column is usually account name
                                account_name = col["value"]
                            elif "value" in col and col["value"]:
                                amounts[f"period_{i}"] = col["value"]
                        
                        if account_name:
                            detected_entities.append({
                                "type": "financial_line_item",
                                "properties": {
                                    "account_name": account_name,
                                    "amounts": amounts,
                                    "row_type": row.get("group", "line_item")
                                }
                            })
        
        return JSONDataAnalysis(
            detected_entities=detected_entities,
            proposed_schema=proposed_schema,
            time_series_data=time_series_data,
            financial_metrics=financial_metrics
        )
    
    async def generate_ontology_proposals(
        self, 
        analysis: JSONDataAnalysis, 
        source_info: DataSource,
        user_message: str = ""
    ) -> List[OntologyProposal]:
        """Generate structured ontology proposals based on data analysis"""
        
        proposals = []
        
        # Proposal 1: Financial Report Entity Class
        if any(entity["type"] == "financial_report" for entity in analysis.detected_entities):
            proposals.append(OntologyProposal(
                id=str(uuid.uuid4()),
                type=ProposalType.ENTITY_CLASS,
                title="Financial Report Entity Class",
                description="Create a standardized entity class for financial reports with temporal and currency properties",
                confidence=0.95,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning="Detected structured financial report with clear temporal boundaries and standardized format",
                proposed_changes={
                    "class_name": "FinancialReport",
                    "properties": {
                        "report_name": {"type": "string", "required": True},
                        "report_basis": {"type": "enum", "values": ["Accrual", "Cash"]},
                        "currency": {"type": "string", "default": "USD"},
                        "start_period": {"type": "date", "required": True},
                        "end_period": {"type": "date", "required": True},
                        "accounting_standard": {"type": "enum", "values": ["GAAP", "IFRS"]}
                    }
                },
                supporting_data=[entity for entity in analysis.detected_entities if entity["type"] == "financial_report"],
                data_sources=[source_info],
                affected_entities=[],
                estimated_impact="Creates foundation for standardized financial report processing",
                validation_priority="high"
            ))
        
        # Proposal 2: Time Series Financial Data
        if analysis.time_series_data:
            proposals.append(OntologyProposal(
                id=str(uuid.uuid4()),
                type=ProposalType.ENTITY_CLASS,
                title="Time Series Financial Periods",
                description="Create entity class for financial time periods with standardized date ranges",
                confidence=0.88,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning="Detected consistent time series structure with monthly periods",
                proposed_changes={
                    "class_name": "FinancialPeriod",
                    "properties": {
                        "period_name": {"type": "string", "required": True},
                        "start_date": {"type": "date", "required": True},
                        "end_date": {"type": "date", "required": True},
                        "period_type": {"type": "enum", "values": ["monthly", "quarterly", "yearly"]},
                        "fiscal_year": {"type": "integer"}
                    }
                },
                supporting_data=analysis.time_series_data,
                data_sources=[source_info],
                estimated_impact="Enables time-based financial analysis and trending",
                cluster_info={
                    "cluster_type": "temporal",
                    "pattern": "monthly_periods",
                    "count": len(analysis.time_series_data)
                }
            ))
        
        # Proposal 3: Financial Line Items with Relationships
        line_items = [e for e in analysis.detected_entities if e["type"] == "financial_line_item"]
        if line_items:
            proposals.append(OntologyProposal(
                id=str(uuid.uuid4()),
                type=ProposalType.RELATIONSHIP,
                title="Financial Line Item Relationships",
                description="Create relationships between financial line items and their parent reports",
                confidence=0.82,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning="Detected hierarchical structure in financial line items with clear parent-child relationships",
                proposed_changes={
                    "relationship_name": "belongs_to_report",
                    "from_class": "FinancialLineItem",
                    "to_class": "FinancialReport",
                    "properties": {
                        "line_order": {"type": "integer"},
                        "is_subtotal": {"type": "boolean"},
                        "calculation_formula": {"type": "string", "optional": True}
                    }
                },
                supporting_data=line_items[:5],  # Sample data
                data_sources=[source_info],
                estimated_impact="Enables hierarchical financial analysis and automated calculations"
            ))
        
        # Proposal 4: Vector Embeddings for Semantic Search
        if len(line_items) > 10:
            proposals.append(OntologyProposal(
                id=str(uuid.uuid4()),
                type=ProposalType.VECTOR_EMBEDDING,
                title="Financial Account Semantic Embeddings",
                description="Create vector embeddings for financial account names to enable semantic search and clustering",
                confidence=0.75,
                confidence_level=ConfidenceLevel.MEDIUM,
                reasoning="Large number of financial line items would benefit from semantic search capabilities",
                proposed_changes={
                    "embedding_model": "text-embedding-ada-002",
                    "vector_dimension": 1536,
                    "similarity_threshold": 0.7,
                    "index_type": "ivfflat"
                },
                supporting_data=[{"account_name": item["properties"]["account_name"]} for item in line_items[:10]],
                data_sources=[source_info],
                estimated_impact="Enables intelligent account matching and financial data categorization",
                embedding_data={
                    "total_items": len(line_items),
                    "unique_accounts": len(set(item["properties"]["account_name"] for item in line_items)),
                    "estimated_vectors": len(line_items)
                }
            ))
        
        return proposals
    
    async def process_user_message(
        self, 
        message: str, 
        json_data: Optional[Dict[str, Any]] = None,
        source_info: Optional[DataSource] = None
    ) -> EnhancedChatResponse:
        """Process user message and generate enhanced response with proposals"""
        
        start_time = datetime.now()
        
        # Generate natural language response
        response_text = await self._generate_natural_response(message, json_data)
        
        proposals = []
        integration_summary = None
        
        # If JSON data is provided, analyze it
        if json_data and source_info:
            analysis = await self.analyze_json_data(json_data, source_info)
            proposals = await self.generate_ontology_proposals(analysis, source_info, message)
            
            integration_summary = DataIntegrationSummary(
                total_records_processed=len(analysis.detected_entities),
                successful_integrations=len(analysis.detected_entities),
                failed_integrations=0,
                new_entities_created=0,  # Will be updated after user accepts proposals
                existing_entities_updated=0,
                clusters_identified=1 if analysis.time_series_data else 0,
                embedding_vectors_created=0
            )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EnhancedChatResponse(
            response=response_text,
            tool_used="enhanced_ontology_agent",
            proposals=proposals,
            integration_summary=integration_summary,
            requires_dashboard_refresh=len(proposals) > 0,
            human_actions_required=["review_proposals"] if proposals else [],
            processing_time_ms=int(processing_time),
            session_id=str(uuid.uuid4())
        )
    
    async def _generate_natural_response(self, message: str, json_data: Optional[Dict] = None) -> str:
        """Generate natural language response using OpenAI"""
        
        context = ""
        if json_data:
            # Analyze the JSON structure for context
            if "data" in json_data and "Header" in json_data["data"]:
                header = json_data["data"]["Header"]
                context = f"I can see you have a {header.get('ReportName', 'financial report')} " \
                         f"from {header.get('StartPeriod')} to {header.get('EndPeriod')} " \
                         f"in {header.get('Currency', 'USD')}. "
        
        try:
            completion = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial ontology expert helping users understand and organize their financial data. Be helpful and suggest concrete next steps."},
                    {"role": "user", "content": f"{context}User message: {message}"}
                ],
                max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"I understand you're asking about: {message}. {context}I've analyzed your data and have some suggestions for organizing it better in our ontology system."
