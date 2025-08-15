"""
Simplified CrewAI framework for Kudwa financial data processing
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class KudwaCrewManager:
    """Simplified manager for CrewAI crews and agents"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize agents
        self._create_agents()

    def _create_agents(self):
        """Create specialized agents"""

        self.document_processor_agent = Agent(
            role='Document Processing Specialist',
            goal='Process uploaded financial documents and extract structured data',
            backstory="""You are an expert in financial document analysis with deep knowledge
            of various financial data formats including P&L statements, balance sheets, and transaction records.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        self.ontology_manager_agent = Agent(
            role='Ontology Management Expert',
            goal='Analyze data patterns and propose intelligent ontology extensions',
            backstory="""You are a knowledge engineer specializing in financial ontologies.
            You understand how to model financial entities, relationships, and processes in a structured way.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        self.rag_specialist_agent = Agent(
            role='RAG and Knowledge Graph Specialist',
            goal='Generate high-quality insights using semantic search and knowledge graphs',
            backstory="""You are an expert in retrieval-augmented generation and knowledge graphs.
            You know how to extract meaningful insights from financial data using advanced AI techniques.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_document_processing_crew(self, document_content: str, filename: str, user_id: str) -> Crew:
        """Create crew for document processing pipeline"""

        process_task = Task(
            description=f"""Process the uploaded financial document:
            1. Parse the document content and extract financial entities
            2. Analyze the data structure and identify entity types
            3. Provide a structured summary of the findings

            Document filename: {filename}
            User ID: {user_id}
            Document content: {document_content[:1000]}...
            """,
            agent=self.document_processor_agent,
            expected_output="Structured report with extracted entities and processing summary"
        )

        ontology_task = Task(
            description=f"""Analyze the processed document and suggest ontology improvements:
            1. Review the extracted financial entities
            2. Identify potential new ontology classes or relationships
            3. Provide recommendations for data modeling

            Based on the document processing results.
            """,
            agent=self.ontology_manager_agent,
            expected_output="Ontology recommendations and data modeling suggestions"
        )

        return Crew(
            agents=[self.document_processor_agent, self.ontology_manager_agent],
            tasks=[process_task, ontology_task],
            process=Process.sequential,
            verbose=True
        )

    def create_chat_crew(self, user_message: str, context: Dict[str, Any] = None) -> Crew:
        """Create crew for handling chat interactions"""

        context = context or {}

        chat_task = Task(
            description=f"""Respond to the user's financial data query:

            User message: {user_message}
            Context: {json.dumps(context, indent=2)}

            Provide a helpful, accurate response based on available financial data and knowledge.
            """,
            agent=self.rag_specialist_agent,
            expected_output="Comprehensive response to the user's query with relevant insights"
        )

        return Crew(
            agents=[self.rag_specialist_agent],
            tasks=[chat_task],
            process=Process.sequential,
            verbose=True
        )
