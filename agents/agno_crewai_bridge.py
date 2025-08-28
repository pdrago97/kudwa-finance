"""
Bridge between Agno and CrewAI systems for seamless integration
Provides unified interface for both frameworks while leveraging their strengths
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import structlog
from dotenv import load_dotenv

# Agno imports
from agents.agno_agents import get_agno_system
from agents.agno_ontology_specialist import get_ontology_specialist
from agents.agno_reasoning_engine import get_reasoning_engine

# CrewAI imports
from agents.crew_chat_agent import CrewChatAgent
from agents.crew_base import KudwaCrewManager
from agents.enhanced_ontology_agent import EnhancedOntologyAgent

# Local imports
from app.services.supabase_client import SupabaseService

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class AgnoCrewAIBridge:
    """
    Bridge system that integrates Agno and CrewAI frameworks
    
    Features:
    - Unified chat interface
    - Intelligent routing between frameworks
    - Performance comparison
    - Fallback mechanisms
    - Hybrid processing workflows
    """

    def __init__(self):
        self.supabase = SupabaseService()
        
        # Initialize Agno components
        self.agno_system = get_agno_system()
        self.agno_ontology = get_ontology_specialist()
        self.agno_reasoning = get_reasoning_engine()
        
        # Initialize CrewAI components
        self.crew_chat = CrewChatAgent()
        self.crew_manager = KudwaCrewManager()
        self.crew_ontology = EnhancedOntologyAgent()
        
        # Configuration
        self.default_framework = "agno"  # or "crewai"
        self.enable_comparison = True
        self.enable_fallback = True

    async def unified_chat_handler(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Unified chat handler that intelligently routes between Agno and CrewAI
        """
        try:
            start_time = datetime.now()
            context = context or {}
            
            # Analyze message to determine best framework
            framework_choice = await self._determine_framework(message, context)
            
            logger.info("bridge.chat.start", 
                       message=message[:100], 
                       framework=framework_choice,
                       context_keys=list(context.keys()))

            # Process with chosen framework
            if framework_choice == "agno":
                result = await self._process_with_agno(message, context)
            elif framework_choice == "crewai":
                result = await self._process_with_crewai(message, context)
            elif framework_choice == "hybrid":
                result = await self._process_hybrid(message, context)
            else:
                result = await self._process_with_agno(message, context)  # Default fallback

            # Add bridge metadata
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["bridge_info"] = {
                "framework_used": framework_choice,
                "processing_time_ms": int(processing_time),
                "fallback_available": self.enable_fallback,
                "comparison_enabled": self.enable_comparison
            }

            # Perform comparison if enabled
            if self.enable_comparison and framework_choice != "hybrid":
                comparison_result = await self._perform_comparison(message, context, framework_choice)
                result["comparison"] = comparison_result

            return result

        except Exception as e:
            logger.error("bridge.chat.error", error=str(e))
            
            # Fallback mechanism
            if self.enable_fallback:
                try:
                    fallback_result = await self._fallback_handler(message, context)
                    fallback_result["bridge_info"] = {
                        "framework_used": "fallback",
                        "original_error": str(e),
                        "fallback_triggered": True
                    }
                    return fallback_result
                except Exception as fallback_error:
                    logger.error("bridge.fallback.error", error=str(fallback_error))
            
            return {
                "success": False,
                "error": str(e),
                "framework_used": "none",
                "fallback_failed": True
            }

    async def unified_document_processing(self, document_content: str, 
                                        document_name: str, 
                                        document_type: str) -> Dict[str, Any]:
        """
        Unified document processing using both frameworks
        """
        try:
            logger.info("bridge.document.start", 
                       document_name=document_name, 
                       document_type=document_type)

            # Process with both frameworks for comparison
            agno_result = await self.agno_ontology.process_document_for_ontology(
                document_content=document_content,
                document_type=document_type,
                document_name=document_name
            )

            crew_result = await self.crew_ontology.process_document_with_reasoning(
                message=f"Process document: {document_name}",
                json_data={"content": document_content, "type": document_type},
                source_info={"name": document_name, "type": document_type}
            )

            # Combine results
            combined_result = {
                "success": True,
                "document_name": document_name,
                "document_type": document_type,
                "agno_analysis": agno_result,
                "crewai_analysis": crew_result,
                "combined_insights": await self._combine_document_insights(agno_result, crew_result),
                "processing_framework": "hybrid"
            }

            return combined_result

        except Exception as e:
            logger.error("bridge.document.error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "document_name": document_name
            }

    async def _determine_framework(self, message: str, context: Dict[str, Any]) -> str:
        """
        Determine which framework to use based on message analysis
        """
        message_lower = message.lower()
        
        # Agno is better for:
        agno_indicators = [
            "reasoning", "step by step", "analyze", "explain", "why", "how",
            "reasoning tools", "multi-modal", "interface", "visualization"
        ]
        
        # CrewAI is better for:
        crewai_indicators = [
            "crew", "team", "collaborate", "workflow", "process", "pipeline"
        ]
        
        # Hybrid for complex tasks:
        hybrid_indicators = [
            "comprehensive", "complete analysis", "full report", "compare"
        ]

        # Check for explicit framework requests
        if "agno" in message_lower or any(indicator in message_lower for indicator in agno_indicators):
            return "agno"
        elif "crew" in message_lower or any(indicator in message_lower for indicator in crewai_indicators):
            return "crewai"
        elif any(indicator in message_lower for indicator in hybrid_indicators):
            return "hybrid"
        
        # Default based on configuration
        return self.default_framework

    async def _process_with_agno(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message using Agno framework"""
        try:
            # Determine if reasoning is needed
            if any(word in message.lower() for word in ["analyze", "reasoning", "step", "explain"]):
                result = await self.agno_reasoning.analyze_financial_scenario(message, context)
                result["agno_component"] = "reasoning_engine"
            else:
                result = await self.agno_system.handle_chat_message(message, context)
                result["agno_component"] = "main_system"
            
            result["framework_used"] = "agno"
            return result
            
        except Exception as e:
            logger.error("bridge.agno.error", error=str(e))
            raise

    async def _process_with_crewai(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message using CrewAI framework"""
        try:
            result = await self.crew_chat.process_chat_message(message, context)
            result["framework_used"] = "crewai"
            return result
            
        except Exception as e:
            logger.error("bridge.crewai.error", error=str(e))
            raise

    async def _process_hybrid(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message using both frameworks and combine results"""
        try:
            # Process with both frameworks
            agno_result = await self._process_with_agno(message, context)
            crewai_result = await self._process_with_crewai(message, context)
            
            # Combine results intelligently
            combined_response = await self._combine_responses(agno_result, crewai_result, message)
            
            return {
                "success": True,
                "response": combined_response,
                "framework_used": "hybrid",
                "agno_result": agno_result,
                "crewai_result": crewai_result,
                "combination_strategy": "intelligent_merge"
            }
            
        except Exception as e:
            logger.error("bridge.hybrid.error", error=str(e))
            raise

    async def _fallback_handler(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback handler when primary processing fails"""
        try:
            # Try the alternative framework
            if self.default_framework == "agno":
                return await self._process_with_crewai(message, context)
            else:
                return await self._process_with_agno(message, context)
                
        except Exception as e:
            logger.error("bridge.fallback.error", error=str(e))
            # Last resort: simple response
            return {
                "success": True,
                "response": "I apologize, but I'm experiencing technical difficulties. Please try rephrasing your question or contact support.",
                "framework_used": "fallback",
                "error_handled": True
            }

    async def _perform_comparison(self, message: str, context: Dict[str, Any], primary_framework: str) -> Dict[str, Any]:
        """Compare results from both frameworks"""
        try:
            if primary_framework == "agno":
                alt_result = await self._process_with_crewai(message, context)
            else:
                alt_result = await self._process_with_agno(message, context)
            
            return {
                "alternative_framework": "crewai" if primary_framework == "agno" else "agno",
                "alternative_result": alt_result,
                "comparison_available": True
            }
            
        except Exception as e:
            logger.error("bridge.comparison.error", error=str(e))
            return {
                "comparison_available": False,
                "comparison_error": str(e)
            }

    async def _combine_responses(self, agno_result: Dict[str, Any], 
                               crewai_result: Dict[str, Any], 
                               original_message: str) -> str:
        """Intelligently combine responses from both frameworks"""
        try:
            agno_response = agno_result.get("response", "")
            crewai_response = crewai_result.get("response", "")
            
            # Simple combination strategy - in production, this could be more sophisticated
            combined = f"""
**Comprehensive Analysis (Agno + CrewAI)**

**Advanced Reasoning Analysis (Agno):**
{agno_response}

**Team-Based Analysis (CrewAI):**
{crewai_response}

**Synthesis:**
Both frameworks provide valuable insights. The Agno analysis offers detailed reasoning and step-by-step breakdown, while the CrewAI analysis provides collaborative team perspectives and workflow considerations.
"""
            return combined
            
        except Exception as e:
            logger.error("bridge.combine.error", error=str(e))
            return "Combined analysis unavailable due to processing error."

    async def _combine_document_insights(self, agno_result: Dict[str, Any], 
                                       crewai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Combine document processing insights from both frameworks"""
        try:
            return {
                "agno_strengths": [
                    "Detailed reasoning process",
                    "Confidence scoring",
                    "Multi-modal support",
                    "Advanced ontology suggestions"
                ],
                "crewai_strengths": [
                    "Team collaboration",
                    "Workflow integration",
                    "Process automation",
                    "Legacy system compatibility"
                ],
                "combined_recommendations": "Use both frameworks for comprehensive document analysis",
                "best_practices": [
                    "Use Agno for complex reasoning tasks",
                    "Use CrewAI for workflow automation",
                    "Combine both for critical documents"
                ]
            }
            
        except Exception as e:
            logger.error("bridge.combine_insights.error", error=str(e))
            return {"error": "Failed to combine insights"}

    def get_bridge_status(self) -> Dict[str, Any]:
        """Get status of the bridge system"""
        return {
            "bridge_active": True,
            "default_framework": self.default_framework,
            "comparison_enabled": self.enable_comparison,
            "fallback_enabled": self.enable_fallback,
            "agno_status": self.agno_system.get_system_status(),
            "crewai_status": "initialized",
            "supported_operations": [
                "unified_chat",
                "document_processing",
                "framework_comparison",
                "hybrid_processing",
                "intelligent_routing"
            ]
        }


# Global instance
bridge_system = None

def get_bridge_system() -> AgnoCrewAIBridge:
    """Get or create global bridge system instance"""
    global bridge_system
    if bridge_system is None:
        bridge_system = AgnoCrewAIBridge()
    return bridge_system
