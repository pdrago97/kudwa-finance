"""
CrewAI-based chat agent for intelligent financial data interaction
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.crew_base import KudwaCrewManager
from agents.rag_graph_manager import RAGGraphManager
from app.services.supabase_client import SupabaseService

logger = structlog.get_logger(__name__)


class CrewChatAgent:
    """Simplified CrewAI-based chat agent for financial data interaction"""

    def __init__(self):
        self.supabase = SupabaseService()
        self.rag_manager = RAGGraphManager()
        self.crew_manager = KudwaCrewManager()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )


    async def process_chat_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat message using CrewAI agents with intelligent action detection"""
        try:
            context = context or {}

            # Analyze the query for type and actions
            query_analysis = await self._analyze_query(message)

            # Generate intelligent response based on query type
            if query_analysis["type"] == "ontology_management":
                response = await self._handle_ontology_management(message, context, query_analysis)
            elif query_analysis["type"] == "financial_data":
                response = await self._handle_financial_data(message, context, query_analysis)
            elif query_analysis["type"] == "data_query":
                response = await self._handle_data_query(message, context)
            else:
                response = await self._handle_general_query(message, context)

            # Add action metadata for human-in-the-loop
            response["requires_approval"] = query_analysis.get("requires_approval", False)
            response["detected_action"] = query_analysis.get("action")
            response["query_type"] = query_analysis["type"]

            return response

        except Exception as e:
            logger.error("Chat message processing failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "I encountered an error processing your request. Please try again.",
                "requires_approval": False
            }


    async def _analyze_query(self, message: str) -> Dict[str, str]:
        """Analyze query to determine appropriate handling and detect action requests"""
        message_lower = message.lower()

        # Detect action requests that need human approval
        action_keywords = {
            "create": ["create", "add", "insert", "new"],
            "update": ["update", "modify", "change", "edit"],
            "extend": ["extend", "expand", "enhance", "improve"],
            "delete": ["delete", "remove", "drop"]
        }

        detected_action = None
        for action, keywords in action_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_action = action
                break

        # Detect entity types
        if any(word in message_lower for word in ["ontology", "class", "relationship", "entity type", "schema", "model"]):
            query_type = "ontology_management"
        elif any(word in message_lower for word in ["revenue", "expense", "profit", "loss", "financial", "account", "transaction", "dataset", "observation"]):
            query_type = "financial_data"
        elif any(word in message_lower for word in ["search", "find", "lookup", "retrieve", "show", "list"]):
            query_type = "data_query"
        else:
            query_type = "general"

        return {
            "type": query_type,
            "action": detected_action,
            "requires_approval": detected_action is not None
        }


    async def _handle_ontology_management(self, message: str, context: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ontology management requests with action detection"""

        action = query_analysis.get("action")

        if action == "create" or action == "extend":
            # User wants to extend the ontology
            crew = self.crew_manager.create_chat_crew(
                f"Ontology Extension Request: {message}. "
                f"Analyze this request and propose specific ontology classes, properties, and relationships that should be added. "
                f"Provide a detailed proposal with confidence scores.",
                context
            )
            result = crew.kickoff()

            return {
                "success": True,
                "response": f"🧠 **Ontology Extension Analysis:**\n\n{str(result)}\n\n"
                           f"⚠️ This request requires human approval before making changes to the ontology schema.",
                "agent_type": "ontology_manager",
                "proposed_action": {
                    "type": "ontology_extension",
                    "description": f"Extend ontology based on: {message}",
                    "details": str(result)
                }
            }
        else:
            # Regular ontology query
            crew = self.crew_manager.create_chat_crew(f"Ontology Query: {message}", context)
            result = crew.kickoff()

            return {
                "success": True,
                "response": str(result),
                "agent_type": "ontology_expert"
            }

    async def _handle_financial_data(self, message: str, context: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle financial data requests with action detection"""

        action = query_analysis.get("action")

        if action == "create" or action == "add":
            # User wants to add new financial data
            crew = self.crew_manager.create_chat_crew(
                f"Financial Data Creation Request: {message}. "
                f"Analyze this request and propose specific financial records that should be created. "
                f"Include all necessary fields, data types, and validation rules.",
                context
            )
            result = crew.kickoff()

            return {
                "success": True,
                "response": f"💰 **Financial Data Creation Analysis:**\n\n{str(result)}\n\n"
                           f"⚠️ This request requires human approval before adding new financial records.",
                "agent_type": "financial_analyst",
                "proposed_action": {
                    "type": "data_creation",
                    "description": f"Create financial data based on: {message}",
                    "details": str(result)
                }
            }
        elif action == "update" or action == "modify":
            # User wants to modify existing data
            crew = self.crew_manager.create_chat_crew(
                f"Financial Data Update Request: {message}. "
                f"Analyze this request and identify which records should be updated and how.",
                context
            )
            result = crew.kickoff()

            return {
                "success": True,
                "response": f"📝 **Financial Data Update Analysis:**\n\n{str(result)}\n\n"
                           f"⚠️ This request requires human approval before modifying existing records.",
                "agent_type": "financial_analyst",
                "proposed_action": {
                    "type": "data_update",
                    "description": f"Update financial data based on: {message}",
                    "details": str(result)
                }
            }
        else:
            # Regular financial analysis
            crew = self.crew_manager.create_chat_crew(f"Financial Analysis: {message}", context)
            result = crew.kickoff()

            return {
                "success": True,
                "response": str(result),
                "agent_type": "financial_analyst"
            }

    async def _handle_data_query(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data query and search requests"""

        crew = self.crew_manager.create_chat_crew(f"Data Search: {message}", context)
        result = crew.kickoff()

        return {
            "success": True,
            "response": str(result),
            "agent_type": "data_specialist"
        }

    async def _handle_financial_analysis(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle financial analysis queries"""

        crew = self.crew_manager.create_chat_crew(f"Financial Analysis: {message}", context)
        result = crew.kickoff()

        return {
            "success": True,
            "response": str(result),
            "agent_type": "financial_analyst",
            "query_type": "financial_analysis"
        }

    async def _handle_ontology_query(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ontology-related queries"""

        crew = self.crew_manager.create_chat_crew(f"Ontology Query: {message}", context)
        result = crew.kickoff()

        return {
            "success": True,
            "response": str(result),
            "agent_type": "ontology_expert",
            "query_type": "ontology_query"
        }

    async def _handle_data_integration(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data integration and search queries"""

        crew = self.crew_manager.create_chat_crew(f"Data Search: {message}", context)
        result = crew.kickoff()

        return {
            "success": True,
            "response": str(result),
            "agent_type": "data_integration",
            "query_type": "data_integration"
        }

    async def _handle_general_query(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries"""

        crew = self.crew_manager.create_chat_crew(message, context)
        result = crew.kickoff()

        return {
            "success": True,
            "response": str(result),
            "agent_type": "general",
            "query_type": "general"
        }
