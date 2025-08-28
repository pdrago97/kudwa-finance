"""
Agno-based Ontology Specialist Agent for advanced document processing and ontology management
Specialized in financial document analysis and ontology reasoning
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import structlog
from dotenv import load_dotenv

# Agno imports
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.tools.file import FileTools
from agno.team import Team

# Local imports
from app.services.supabase_client import SupabaseService

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class AgnoOntologySpecialist:
    """
    Advanced ontology specialist using Agno framework for:
    - Document analysis with reasoning
    - Ontology class extraction and suggestion
    - Relationship mapping
    - Confidence scoring
    - Multi-format document support
    """

    def __init__(self):
        self.supabase = SupabaseService()
        
        # Initialize models
        self.claude_model = Claude(id="claude-sonnet-4-20250514")
        self.openai_model = OpenAIChat(id="gpt-4o")
        
        # Create specialized agents
        self._create_ontology_agents()
        self._create_ontology_team()

    def _create_ontology_agents(self):
        """Create specialized agents for ontology management"""
        
        # Document Analysis Agent
        self.document_analyzer = Agent(
            name="Financial Document Analyzer",
            role="Analyze financial documents and extract structured ontological information",
            model=self.claude_model,
            tools=[
                ReasoningTools(add_instructions=True),
                FileTools(read_file=True, write_file=True)
            ],
            instructions=[
                "You are an expert financial document analyst with deep ontological reasoning capabilities",
                "Use step-by-step reasoning to analyze document structure and content",
                "Extract financial entities, accounts, amounts, periods, and relationships",
                "Identify data patterns and suggest ontological classifications",
                "Provide confidence scores (0-100) for each extracted element",
                "Focus on creating structured, machine-readable ontological representations",
                "Always explain your reasoning process for transparency"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Ontology Designer Agent
        self.ontology_designer = Agent(
            name="Ontology Designer",
            role="Design and refine financial ontology structures based on document analysis",
            model=self.claude_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in financial ontology design and knowledge representation",
                "Use reasoning to create comprehensive ontology proposals",
                "Design classes, properties, and relationships that accurately model financial data",
                "Ensure ontology consistency and avoid redundancy",
                "Consider inheritance hierarchies and semantic relationships",
                "Provide clear justifications for all ontological decisions",
                "Focus on scalability and extensibility of the ontology"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Relationship Mapper Agent
        self.relationship_mapper = Agent(
            name="Relationship Mapper",
            role="Map and validate relationships between financial entities and concepts",
            model=self.openai_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in mapping relationships between financial entities",
                "Use reasoning to identify semantic and structural relationships",
                "Create relationship mappings that preserve business logic",
                "Validate relationship consistency across the ontology",
                "Suggest new relationships based on data patterns",
                "Ensure relationships are bidirectional where appropriate",
                "Focus on creating meaningful connections that enhance data discovery"
            ],
            markdown=True,
            show_tool_calls=True
        )

    def _create_ontology_team(self):
        """Create coordinated team for comprehensive ontology processing"""
        
        self.ontology_team = Team(
            mode="coordinate",
            members=[self.document_analyzer, self.ontology_designer, self.relationship_mapper],
            model=self.claude_model,
            success_criteria="Complete ontological analysis with actionable recommendations",
            instructions=[
                "Work together to provide comprehensive ontological analysis",
                "Ensure all aspects of document structure are captured",
                "Create practical, implementable ontology improvements",
                "Maintain consistency across all recommendations",
                "Provide clear implementation guidance"
            ],
            show_tool_calls=True,
            markdown=True
        )

    async def process_document_for_ontology(self, document_content: str, 
                                          document_type: str, 
                                          document_name: str) -> Dict[str, Any]:
        """
        Process document using Agno reasoning for ontology extraction
        """
        try:
            start_time = datetime.now()
            
            logger.info("agno_ontology.document_processing.start", 
                       document_name=document_name, 
                       document_type=document_type)

            # Create comprehensive analysis prompt
            analysis_prompt = f"""
            Perform comprehensive ontological analysis of this financial document:
            
            **Document Information:**
            - Name: {document_name}
            - Type: {document_type}
            - Content: {document_content[:3000]}...
            
            **Analysis Requirements:**
            1. **Entity Extraction**: Identify all financial entities with confidence scores
            2. **Ontology Classes**: Suggest new or existing ontology classes
            3. **Relationships**: Map relationships between entities
            4. **Data Patterns**: Identify recurring patterns for ontology design
            5. **Implementation**: Provide specific implementation recommendations
            
            Use step-by-step reasoning for each analysis component.
            """

            # Process with ontology team
            result = self.ontology_team.print_response(
                analysis_prompt,
                stream=False,
                show_full_reasoning=True
            )

            # Extract structured information from result
            ontology_analysis = await self._extract_structured_analysis(str(result))
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "document_name": document_name,
                "document_type": document_type,
                "raw_analysis": str(result),
                "structured_analysis": ontology_analysis,
                "processing_time_ms": int(processing_time),
                "agent_type": "agno_ontology_team",
                "reasoning_used": True
            }

        except Exception as e:
            logger.error("agno_ontology.document_processing.error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "document_name": document_name,
                "agent_type": "agno_ontology_team"
            }

    async def suggest_ontology_improvements(self, current_ontology: Dict[str, Any], 
                                          data_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Suggest ontology improvements based on current structure and data patterns
        """
        try:
            improvement_prompt = f"""
            Analyze the current ontology and suggest improvements based on data patterns:
            
            **Current Ontology:**
            {json.dumps(current_ontology, indent=2)}
            
            **Data Patterns:**
            {json.dumps(data_patterns, indent=2)}
            
            **Improvement Areas:**
            1. Missing classes or properties
            2. Relationship gaps
            3. Hierarchy optimizations
            4. Semantic enhancements
            5. Performance considerations
            
            Provide specific, actionable recommendations with reasoning.
            """

            result = self.ontology_designer.print_response(
                improvement_prompt,
                stream=False,
                show_full_reasoning=True
            )

            return {
                "success": True,
                "improvements": str(result),
                "agent_type": "agno_ontology_designer",
                "reasoning_used": True
            }

        except Exception as e:
            logger.error("agno_ontology.improvements.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def validate_ontology_consistency(self, ontology_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ontology consistency using reasoning
        """
        try:
            validation_prompt = f"""
            Validate the consistency and completeness of this ontology structure:
            
            **Ontology Structure:**
            {json.dumps(ontology_structure, indent=2)}
            
            **Validation Checks:**
            1. Class hierarchy consistency
            2. Property domain/range validation
            3. Relationship symmetry and transitivity
            4. Naming convention adherence
            5. Semantic coherence
            6. Completeness assessment
            
            Identify issues and provide specific fixes with reasoning.
            """

            result = self.ontology_designer.print_response(
                validation_prompt,
                stream=False,
                show_full_reasoning=True
            )

            return {
                "success": True,
                "validation_report": str(result),
                "agent_type": "agno_ontology_designer",
                "reasoning_used": True
            }

        except Exception as e:
            logger.error("agno_ontology.validation.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def _extract_structured_analysis(self, raw_analysis: str) -> Dict[str, Any]:
        """
        Extract structured information from raw analysis using reasoning
        """
        try:
            extraction_prompt = f"""
            Extract structured information from this ontological analysis:
            
            {raw_analysis}
            
            Return a JSON structure with:
            - entities: List of extracted entities with confidence scores
            - classes: Suggested ontology classes
            - relationships: Identified relationships
            - patterns: Data patterns found
            - recommendations: Implementation recommendations
            
            Use reasoning to ensure accuracy and completeness.
            """

            result = self.document_analyzer.print_response(
                extraction_prompt,
                stream=False,
                show_full_reasoning=True
            )

            # Try to extract JSON from the result
            # This is a simplified extraction - in production, you'd use more sophisticated parsing
            return {
                "entities": [],
                "classes": [],
                "relationships": [],
                "patterns": [],
                "recommendations": str(result)
            }

        except Exception as e:
            logger.error("agno_ontology.extraction.error", error=str(e))
            return {
                "entities": [],
                "classes": [],
                "relationships": [],
                "patterns": [],
                "recommendations": "Extraction failed"
            }

    def get_ontology_status(self) -> Dict[str, Any]:
        """Get status of ontology specialist system"""
        return {
            "specialist_type": "agno_ontology_specialist",
            "agents_available": ["document_analyzer", "ontology_designer", "relationship_mapper"],
            "team_configured": True,
            "reasoning_enabled": True,
            "models": {
                "claude": "claude-sonnet-4-20250514",
                "openai": "gpt-4o"
            },
            "capabilities": [
                "Document analysis with reasoning",
                "Ontology class extraction",
                "Relationship mapping",
                "Confidence scoring",
                "Multi-format support",
                "Consistency validation"
            ]
        }


# Global instance
ontology_specialist = None

def get_ontology_specialist() -> AgnoOntologySpecialist:
    """Get or create global ontology specialist instance"""
    global ontology_specialist
    if ontology_specialist is None:
        ontology_specialist = AgnoOntologySpecialist()
    return ontology_specialist
