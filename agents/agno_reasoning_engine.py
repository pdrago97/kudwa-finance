"""
Agno Reasoning Engine for Advanced Financial Analysis
Implements sophisticated reasoning patterns for financial document processing and analysis
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
from agno.tools.yfinance import YFinanceTools
from agno.team import Team

# Local imports
from app.services.supabase_client import SupabaseService
from agents.rag_graph_manager import RAGGraphManager

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class AgnoReasoningEngine:
    """
    Advanced reasoning engine using Agno framework for:
    - Step-by-step financial analysis
    - Complex problem decomposition
    - Multi-perspective reasoning
    - Confidence assessment
    - Decision support
    """

    def __init__(self):
        self.supabase = SupabaseService()
        self.rag_manager = RAGGraphManager()
        
        # Initialize models
        self.claude_model = Claude(id="claude-sonnet-4-20250514")
        self.openai_model = OpenAIChat(id="gpt-4o")
        
        # Create reasoning agents
        self._create_reasoning_agents()
        self._create_reasoning_teams()

    def _create_reasoning_agents(self):
        """Create specialized reasoning agents"""
        
        # Financial Reasoning Specialist
        self.financial_reasoner = Agent(
            name="Financial Reasoning Specialist",
            role="Perform step-by-step financial analysis with detailed reasoning",
            model=self.claude_model,
            tools=[
                ReasoningTools(add_instructions=True),
                YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)
            ],
            instructions=[
                "You are an expert financial analyst with advanced reasoning capabilities",
                "Always break down complex financial problems into clear, logical steps",
                "Use reasoning tools to show your thought process transparently",
                "Provide confidence scores for your analysis and recommendations",
                "Consider multiple perspectives and potential risks in your analysis",
                "Support your conclusions with data and clear logical reasoning",
                "Explain financial concepts in accessible terms while maintaining accuracy"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Risk Assessment Agent
        self.risk_assessor = Agent(
            name="Risk Assessment Specialist",
            role="Analyze financial risks using systematic reasoning approaches",
            model=self.claude_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in financial risk assessment and management",
                "Use systematic reasoning to identify and evaluate financial risks",
                "Consider both quantitative and qualitative risk factors",
                "Provide risk mitigation strategies with clear reasoning",
                "Assess probability and impact of identified risks",
                "Use scenario analysis and stress testing in your reasoning",
                "Present risk assessments in clear, actionable formats"
            ],
            markdown=True,
            show_tool_calls=True
        )

        # Decision Support Agent
        self.decision_support = Agent(
            name="Decision Support Specialist",
            role="Provide structured decision support using multi-criteria reasoning",
            model=self.openai_model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "You are an expert in financial decision support and analysis",
                "Use structured reasoning frameworks for complex decisions",
                "Consider multiple criteria and stakeholder perspectives",
                "Provide clear pros and cons analysis with reasoning",
                "Use decision trees and frameworks where appropriate",
                "Quantify decision factors when possible",
                "Present recommendations with clear implementation steps"
            ],
            markdown=True,
            show_tool_calls=True
        )

    def _create_reasoning_teams(self):
        """Create coordinated reasoning teams"""
        
        # Comprehensive Analysis Team
        self.analysis_team = Team(
            mode="coordinate",
            members=[self.financial_reasoner, self.risk_assessor, self.decision_support],
            model=self.claude_model,
            success_criteria="Comprehensive financial analysis with clear reasoning and actionable recommendations",
            instructions=[
                "Work together to provide thorough financial analysis",
                "Ensure all perspectives are considered in the reasoning process",
                "Provide clear, step-by-step reasoning for all conclusions",
                "Include risk assessment and decision support in all analyses",
                "Present findings in a structured, actionable format"
            ],
            show_tool_calls=True,
            markdown=True
        )

    async def analyze_financial_scenario(self, scenario: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive financial scenario analysis with reasoning
        """
        try:
            start_time = datetime.now()
            context = context or {}
            
            logger.info("agno_reasoning.scenario_analysis.start", scenario=scenario[:100])

            # Create comprehensive analysis prompt
            analysis_prompt = f"""
            Perform comprehensive financial scenario analysis using step-by-step reasoning:
            
            **Scenario:**
            {scenario}
            
            **Context:**
            {json.dumps(context, indent=2)}
            
            **Analysis Framework:**
            1. **Situation Assessment**: Break down the current financial situation
            2. **Key Factors Identification**: Identify critical financial factors and variables
            3. **Risk Analysis**: Assess potential risks and uncertainties
            4. **Scenario Modeling**: Consider different possible outcomes
            5. **Decision Options**: Evaluate available courses of action
            6. **Recommendations**: Provide clear, actionable recommendations
            
            Use detailed reasoning for each step and provide confidence scores for your analysis.
            """

            # Process with analysis team
            result = self.analysis_team.print_response(
                analysis_prompt,
                stream=False,
                show_full_reasoning=True
            )

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "scenario": scenario,
                "analysis": str(result),
                "processing_time_ms": int(processing_time),
                "agent_type": "agno_reasoning_team",
                "reasoning_used": True,
                "confidence_level": "high"
            }

        except Exception as e:
            logger.error("agno_reasoning.scenario_analysis.error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "scenario": scenario
            }

    async def perform_risk_assessment(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform detailed risk assessment with reasoning
        """
        try:
            risk_prompt = f"""
            Perform comprehensive risk assessment using systematic reasoning:
            
            **Financial Data:**
            {json.dumps(financial_data, indent=2)}
            
            **Risk Assessment Framework:**
            1. **Risk Identification**: Systematically identify potential risks
            2. **Risk Categorization**: Classify risks by type and source
            3. **Probability Assessment**: Evaluate likelihood of each risk
            4. **Impact Analysis**: Assess potential financial impact
            5. **Risk Prioritization**: Rank risks by severity and probability
            6. **Mitigation Strategies**: Develop risk mitigation approaches
            
            Use detailed reasoning and provide confidence scores for each assessment.
            """

            result = self.risk_assessor.print_response(
                risk_prompt,
                stream=False,
                show_full_reasoning=True
            )

            return {
                "success": True,
                "risk_assessment": str(result),
                "agent_type": "agno_risk_assessor",
                "reasoning_used": True
            }

        except Exception as e:
            logger.error("agno_reasoning.risk_assessment.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def provide_decision_support(self, decision_context: str, options: List[str]) -> Dict[str, Any]:
        """
        Provide structured decision support with reasoning
        """
        try:
            decision_prompt = f"""
            Provide structured decision support using multi-criteria reasoning:
            
            **Decision Context:**
            {decision_context}
            
            **Available Options:**
            {json.dumps(options, indent=2)}
            
            **Decision Framework:**
            1. **Criteria Definition**: Define key decision criteria
            2. **Option Evaluation**: Evaluate each option against criteria
            3. **Trade-off Analysis**: Analyze trade-offs between options
            4. **Scenario Testing**: Test options under different scenarios
            5. **Recommendation**: Provide clear recommendation with reasoning
            6. **Implementation**: Suggest implementation approach
            
            Use systematic reasoning and provide confidence scores for recommendations.
            """

            result = self.decision_support.print_response(
                decision_prompt,
                stream=False,
                show_full_reasoning=True
            )

            return {
                "success": True,
                "decision_analysis": str(result),
                "agent_type": "agno_decision_support",
                "reasoning_used": True
            }

        except Exception as e:
            logger.error("agno_reasoning.decision_support.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def demonstrate_reasoning_capabilities(self) -> Dict[str, Any]:
        """
        Demonstrate advanced reasoning capabilities with a financial example
        """
        try:
            demo_scenario = """
            Company ABC is considering three strategic options:
            
            1. Expand operations internationally (requires $2M investment, potential 30% revenue increase)
            2. Develop new product line (requires $1.5M investment, potential 20% revenue increase)
            3. Acquire competitor (requires $3M investment, potential 50% revenue increase)
            
            Current financial position:
            - Annual Revenue: $10M
            - Operating Margin: 15%
            - Cash Available: $2.5M
            - Debt-to-Equity Ratio: 0.3
            - Market Growth Rate: 8% annually
            """

            result = await self.analyze_financial_scenario(demo_scenario)

            return {
                "success": True,
                "demo_type": "strategic_decision_analysis",
                "scenario": demo_scenario,
                "reasoning_demonstration": result.get("analysis"),
                "capabilities_shown": [
                    "Multi-step reasoning",
                    "Financial analysis",
                    "Risk assessment",
                    "Decision support",
                    "Confidence scoring",
                    "Scenario modeling"
                ]
            }

        except Exception as e:
            logger.error("agno_reasoning.demo.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    def get_reasoning_status(self) -> Dict[str, Any]:
        """Get status of reasoning engine"""
        return {
            "engine_type": "agno_reasoning_engine",
            "agents_available": ["financial_reasoner", "risk_assessor", "decision_support"],
            "teams_configured": ["analysis_team"],
            "reasoning_tools_enabled": True,
            "models": {
                "claude": "claude-sonnet-4-20250514",
                "openai": "gpt-4o"
            },
            "capabilities": [
                "Step-by-step financial analysis",
                "Risk assessment with reasoning",
                "Multi-criteria decision support",
                "Scenario analysis",
                "Confidence assessment",
                "Problem decomposition"
            ]
        }


# Global instance
reasoning_engine = None

def get_reasoning_engine() -> AgnoReasoningEngine:
    """Get or create global reasoning engine instance"""
    global reasoning_engine
    if reasoning_engine is None:
        reasoning_engine = AgnoReasoningEngine()
    return reasoning_engine
