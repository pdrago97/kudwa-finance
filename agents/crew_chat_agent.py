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
            import uuid
            import time

            context = context or {}
            request_id = context.get("request_id", str(uuid.uuid4()))
            start_time = time.time()

            logger.info("crew_chat.start", message=message[:120], request_id=request_id)

            # Analyze the query for type and actions
            query_analysis = await self._analyze_query(message)

            # Generate intelligent response based on query type
            if query_analysis["type"] == "ontology_management":
                response = await self._handle_ontology_management(message, context, query_analysis)
            elif query_analysis["type"] == "financial_data":
                response = await self._handle_financial_data(message, context, query_analysis)
            elif query_analysis["type"] == "data_query":
                response = await self._handle_data_query(message, context)
            elif query_analysis["type"] == "visualization":
                response = await self._handle_visualization_request(message, context)
            else:
                response = await self._handle_general_query(message, context)

            # Add action metadata for human-in-the-loop
            response["requires_approval"] = query_analysis.get("requires_approval", False)
            response["detected_action"] = query_analysis.get("action")
            response["query_type"] = query_analysis["type"]

            # Add debug info
            processing_time = int((time.time() - start_time) * 1000)
            response["debug"] = {
                "request_id": request_id,
                "executed_handler": response.get("executed_handler", "unknown"),
                "query_type": query_analysis["type"],
                "detected_action": query_analysis.get("action"),
                "processing_time_ms": processing_time,
                "vector_index_size": len(self.rag_manager.embeddings_data) if self.rag_manager.embeddings_data else 0
            }

            logger.info("crew_chat.complete", request_id=request_id,
                       query_type=query_analysis["type"],
                       processing_time_ms=processing_time)

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
        if any(word in message_lower for word in ["ontology", "class", "relationship", "entity type", "schema", "model", "entity", "entities"]):
            query_type = "ontology_management"
        elif any(word in message_lower for word in ["revenue", "expense", "profit", "loss", "financial", "account", "transaction", "dataset", "observation"]):
            query_type = "financial_data"
        elif any(word in message_lower for word in ["search", "find", "lookup", "retrieve", "show", "list"]):
            query_type = "data_query"
        elif any(word in message_lower for word in ["visualize", "graph", "chart", "diagram"]):
            query_type = "visualization"
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
            # Regular ontology query - fetch actual data from Supabase
            try:
                classes_result = self.supabase.client.table("kudwa_ontology_classes")\
                    .select("class_id, label, status, class_type")\
                    .eq("status", "active")\
                    .execute()

                classes = classes_result.data or []

                if classes:
                    class_list = ", ".join([f"{c['class_id']} ({c['label']})" for c in classes])
                    response_text = f"📋 **Active Ontology Classes ({len(classes)} total):**\n\n{class_list}"

                    # Create table gadget
                    gadget_spec = {
                        "type": "table",
                        "title": "Active Ontology Classes",
                        "columns": ["Class ID", "Label", "Type"],
                        "rows": [[c["class_id"], c["label"], c.get("class_type", "entity")] for c in classes]
                    }
                else:
                    response_text = "No active ontology classes found in the system."
                    gadget_spec = None

                return {
                    "success": True,
                    "response": response_text,
                    "agent_type": "ontology_expert",
                    "executed_handler": "_handle_ontology_management",
                    "gadget_spec": gadget_spec
                }

            except Exception as e:
                logger.error("Failed to fetch ontology classes", error=str(e))
                return {
                    "success": True,
                    "response": f"Error fetching ontology classes: {str(e)}",
                    "agent_type": "ontology_expert",
                    "executed_handler": "_handle_ontology_management"
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
        """Handle data query and search requests with RAG"""
        try:
            # Initialize RAG if needed
            if not self.rag_manager.embeddings_data:
                await self.rag_manager.initialize_vector_index()

            # Perform semantic search
            rag_results = await self.rag_manager.semantic_search(message, top_k=5)

            # Build response with RAG results
            if rag_results:
                response_text = f"🔍 **Search Results for:** {message}\n\n"
                for i, hit in enumerate(rag_results[:3], 1):
                    response_text += f"**{i}.** {hit['content'][:200]}...\n"
                    response_text += f"   *Similarity: {hit['similarity_score']:.3f} | Source: {hit['source_kind']}*\n\n"

                # Create results table gadget
                gadget_spec = {
                    "type": "table",
                    "title": f"RAG Search Results for: {message}",
                    "columns": ["Content", "Similarity", "Source"],
                    "rows": [[hit['content'][:100] + "...", f"{hit['similarity_score']:.3f}", hit['source_kind']] for hit in rag_results]
                }
            else:
                response_text = f"No relevant results found for: {message}\n\nVector index size: {len(self.rag_manager.embeddings_data)} embeddings"
                gadget_spec = None

            # Check for visualization requests in data queries
            if "visualize" in message.lower():
                viz_spec = self.rag_manager.generate_interactive_visualization()
                if viz_spec:
                    gadget_spec = {"type": "network", "path": viz_spec}

            return {
                "success": True,
                "response": response_text,
                "agent_type": "data_specialist",
                "executed_handler": "_handle_data_query",
                "gadget_spec": gadget_spec,
                "rag_results": rag_results
            }

        except Exception as e:
            logger.error("Data query failed", error=str(e))
            return {
                "success": True,
                "response": f"Error processing data query: {str(e)}",
                "agent_type": "data_specialist",
                "executed_handler": "_handle_data_query"
            }

    async def _handle_visualization_request(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visualization requests with POML integration"""

        # Extract visualization parameters from message
        viz_type = "network"  # Default visualization type
        if "bar chart" in message.lower():
            viz_type = "bar"
        elif "line chart" in message.lower():
            viz_type = "line"
        elif "pie chart" in message.lower():
            viz_type = "pie"

        # Generate POML visualization spec
        viz_spec = self.rag_manager.generate_interactive_visualization(viz_type)

        return {
            "success": True,
            "response": f"📊 Visualization requested. Here is your {viz_type} chart specification:",
            "agent_type": "visualization_engineer",
            "gadget_spec": viz_spec
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
