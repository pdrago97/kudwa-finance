"""
Agno-based agents for advanced financial document processing and reasoning
Integrates with existing CrewAI system while providing enhanced capabilities
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
from agents.rag_graph_manager import RAGGraphManager

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class AgnoFinancialSystem:
    """
    Advanced multi-agent system using Agno framework for financial document processing,
    ontology management, and intelligent reasoning
    """

    def __init__(self):
        self.supabase = SupabaseService()
        self.rag_manager = RAGGraphManager()
        
        # Initialize models
        self.claude_model = Claude(id="claude-sonnet-4-20250514")
        self.openai_model = OpenAIChat(id="gpt-4o")
        
        # Initialize specialized agents
        self._create_agents()
        self._create_teams()

    def _create_agents(self):
        """Create specialized Agno agents for different tasks"""
        
        # Document Processing Agent with Reasoning
        self.document_processor = Agent(
            name="Financial Document Processor",
            role="Process and analyze financial documents with advanced reasoning",
            model=self.claude_model,
            tools=[
                ReasoningTools(add_instructions=True),
                FileTools(read_file=True, write_file=True)
            ],
            instructions=[
                "You are an expert financial document analyst with advanced reasoning capabilities",
                "Always use reasoning tools to break down complex financial documents step by step",
                "Extract structured data including accounts, amounts, periods, and relationships",
                "Identify potential ontology classes and suggest data modeling improvements",
                "Provide detailed analysis with confidence scores for extracted information"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Ontology Management Agent
        self.ontology_manager = Agent(
            name="Ontology Manager",
            role="Manage financial ontology and data relationships",
            model=self.claude_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in financial ontology design and data modeling",
                "Use reasoning to analyze data patterns and suggest ontology improvements",
                "Create comprehensive proposals for new classes, relationships, and attributes",
                "Ensure ontology consistency and avoid redundancy",
                "Provide clear justifications for all ontology changes"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Advanced RAG Agent
        self.rag_agent = Agent(
            name="RAG Specialist",
            role="Provide intelligent answers using semantic search and knowledge graphs",
            model=self.openai_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in financial data analysis and semantic search",
                "Use reasoning to understand complex financial queries",
                "Provide comprehensive answers based on available data",
                "Include relevant context and data sources in your responses",
                "Suggest follow-up questions or analyses when appropriate"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Interface Creator Agent
        self.interface_creator = Agent(
            name="Interface Creator",
            role="Create dynamic user interfaces and visualizations",
            model=self.openai_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in creating dynamic user interfaces for financial data",
                "Use reasoning to understand user requirements and create appropriate interfaces",
                "Generate HTML, CSS, and JavaScript for interactive components",
                "Create visualizations that help users understand financial data",
                "Ensure interfaces are responsive and user-friendly"
            ],
            markdown=True,
            show_tool_calls=True
        )

    def _create_teams(self):
        """Create agent teams for complex workflows"""
        
        # Document Processing Team
        self.document_team = Team(
            mode="coordinate",
            members=[self.document_processor, self.ontology_manager],
            model=self.claude_model,
            success_criteria="Complete document analysis with ontology recommendations",
            instructions=[
                "Coordinate to provide comprehensive document analysis",
                "Ensure all financial data is properly extracted and categorized",
                "Provide actionable ontology improvement suggestions"
            ],
            show_tool_calls=True,
            markdown=True
        )

        # Chat and Analysis Team
        self.chat_team = Team(
            mode="coordinate", 
            members=[self.rag_agent, self.interface_creator],
            model=self.openai_model,
            success_criteria="Provide comprehensive answers with appropriate visualizations",
            instructions=[
                "Work together to provide the best possible user experience",
                "Combine data analysis with appropriate visualizations",
                "Create interactive elements when beneficial"
            ],
            show_tool_calls=True,
            markdown=True
        )

    async def process_document_upload(self, file_content: str, file_name: str, 
                                    file_type: str) -> Dict[str, Any]:
        """
        Process uploaded document using Agno agents with advanced reasoning
        """
        try:
            start_time = datetime.now()
            
            logger.info("agno.document_processing.start", 
                       file_name=file_name, file_type=file_type)

            # Use document processing team
            prompt = f"""
            Analyze the uploaded financial document:
            
            File Name: {file_name}
            File Type: {file_type}
            Content: {file_content[:2000]}...
            
            Please:
            1. Extract all financial data with reasoning
            2. Identify account types, amounts, and periods
            3. Suggest ontology improvements
            4. Provide confidence scores for extracted data
            """

            result = self.document_team.print_response(
                prompt,
                stream=False,
                show_full_reasoning=True
            )

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "analysis": str(result),
                "processing_time_ms": int(processing_time),
                "agent_type": "agno_document_team",
                "file_processed": file_name
            }

        except Exception as e:
            logger.error("agno.document_processing.error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "agent_type": "agno_document_team"
            }

    async def handle_chat_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle chat messages using Agno agents with advanced reasoning
        """
        try:
            start_time = datetime.now()
            context = context or {}
            
            logger.info("agno.chat.start", message=message[:100])

            # Determine if we need interface creation
            needs_interface = any(word in message.lower() for word in 
                                ["create", "build", "interface", "dashboard", "widget", "visualization"])

            if needs_interface:
                # Use chat team with interface creation
                result = self.chat_team.print_response(
                    f"User request: {message}\nContext: {json.dumps(context, indent=2)}",
                    stream=False,
                    show_full_reasoning=True
                )
            else:
                # Use RAG agent for data queries
                result = self.rag_agent.print_response(
                    f"Financial query: {message}\nContext: {json.dumps(context, indent=2)}",
                    stream=False,
                    show_full_reasoning=True
                )

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "response": str(result),
                "processing_time_ms": int(processing_time),
                "agent_type": "agno_chat_team" if needs_interface else "agno_rag_agent",
                "reasoning_used": True
            }

        except Exception as e:
            logger.error("agno.chat.error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "agent_type": "agno_system"
            }

    async def create_dynamic_interface(self, requirements: str) -> Dict[str, Any]:
        """
        Create dynamic interface components using Agno interface creator
        """
        try:
            prompt = f"""
            Create a dynamic interface component for the following requirements:
            {requirements}
            
            Generate:
            1. HTML structure
            2. CSS styling
            3. JavaScript functionality
            4. Integration instructions
            
            Make it responsive and user-friendly for financial data interaction.
            """

            result = self.interface_creator.print_response(
                prompt,
                stream=False,
                show_full_reasoning=True
            )

            return {
                "success": True,
                "interface_code": str(result),
                "agent_type": "agno_interface_creator"
            }

        except Exception as e:
            logger.error("agno.interface_creation.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of Agno system"""
        return {
            "agno_version": "1.8.1",
            "agents_initialized": True,
            "models_available": {
                "claude": "claude-sonnet-4-20250514",
                "openai": "gpt-4o"
            },
            "teams_configured": ["document_team", "chat_team"],
            "reasoning_enabled": True,
            "multi_modal_support": True
        }


# Global instance
agno_system = None

def get_agno_system() -> AgnoFinancialSystem:
    """Get or create global Agno system instance"""
    global agno_system
    if agno_system is None:
        agno_system = AgnoFinancialSystem()
    return agno_system
