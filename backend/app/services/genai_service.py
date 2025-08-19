"""
GenAI Service - Real AI/LLM integration for intelligent responses
"""
import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser


class GenAIService:
    """Service for AI-powered responses using OpenAI/LangChain"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = bool(self.openai_api_key)
        
        if self.use_openai:
            print("🤖 GenAI Service: Using OpenAI GPT-4")
            self.client = OpenAI(api_key=self.openai_api_key)
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                openai_api_key=self.openai_api_key
            )
        else:
            print("⚠️  GenAI Service: No OpenAI API key found - using fallback responses")
            self.client = None
            self.llm = None
    
    def generate_ontology_response(
        self, 
        user_message: str,
        entities: List[Dict],
        relations: List[Dict], 
        instances: List[Dict]
    ) -> Dict[str, Any]:
        """Generate AI-powered response about ontology data"""
        
        print(f"\n🤖 === GenAI PROCESSING STARTED ===")
        print(f"📝 User Query: '{user_message}'")
        print(f"📊 Context: {len(entities)} entities, {len(relations)} relations, {len(instances)} instances")
        
        if not self.use_openai:
            return self._fallback_response(user_message, entities, relations, instances)
        
        try:
            # Build rich context for the AI
            context = self._build_ai_context(entities, relations, instances)
            
            # Create the AI prompt
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(user_message, context)
            
            print(f"🧠 Sending to GPT-4...")
            print(f"📏 System prompt: {len(system_prompt)} chars")
            print(f"📏 User prompt: {len(user_prompt)} chars")
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            print(f"✅ GPT-4 Response: {len(ai_response)} characters")
            print(f"💰 Token usage: {response.usage.total_tokens} tokens")
            print(f"🤖 === GenAI PROCESSING COMPLETED ===\n")
            
            return {
                "text": ai_response,
                "widgets": [],
                "metadata": {
                    "model": "gpt-4",
                    "tokens_used": response.usage.total_tokens,
                    "context_entities": len(entities),
                    "context_relations": len(relations),
                    "context_instances": len(instances)
                }
            }
            
        except Exception as e:
            print(f"❌ GenAI Error: {e}")
            return self._fallback_response(user_message, entities, relations, instances)
    
    def _build_ai_context(self, entities: List[Dict], relations: List[Dict], instances: List[Dict]) -> str:
        """Build rich context for AI"""
        context_parts = []
        
        # Entities with properties
        if entities:
            context_parts.append("=== ENTITIES ===")
            for entity in entities:
                name = entity.get('name', 'Unknown')
                props = entity.get('properties', {})
                if props:
                    prop_list = [f"{k}: {v}" for k, v in props.items()]
                    context_parts.append(f"Entity '{name}' has properties: {', '.join(prop_list)}")
                else:
                    context_parts.append(f"Entity '{name}' (no properties defined)")
        
        # Relations
        if relations:
            context_parts.append("\n=== RELATIONSHIPS ===")
            entity_lookup = {str(e.get('id')): e.get('name', 'Unknown') for e in entities}
            
            for relation in relations:
                rel_type = relation.get('rel_type', 'unknown')
                source_id = str(relation.get('source_entity_id', ''))
                target_id = str(relation.get('target_entity_id', ''))
                
                source_name = entity_lookup.get(source_id, 'Unknown')
                target_name = entity_lookup.get(target_id, 'Unknown')
                
                context_parts.append(f"{source_name} --{rel_type}--> {target_name}")
        
        # Sample instances with data
        if instances:
            context_parts.append(f"\n=== DATA INSTANCES ({len(instances)} total) ===")
            entity_lookup = {str(e.get('id')): e.get('name', 'Unknown') for e in entities}
            
            # Group by entity type
            by_entity = {}
            for instance in instances:
                entity_id = str(instance.get('entity_id', ''))
                entity_name = entity_lookup.get(entity_id, 'Unknown')
                
                if entity_name not in by_entity:
                    by_entity[entity_name] = []
                by_entity[entity_name].append(instance)
            
            for entity_name, entity_instances in by_entity.items():
                context_parts.append(f"\n{entity_name} instances ({len(entity_instances)}):")
                
                # Show first few instances with their properties
                for i, instance in enumerate(entity_instances[:3]):
                    props = instance.get('properties', {})
                    if props:
                        prop_summary = []
                        for k, v in props.items():
                            if isinstance(v, (int, float)) and v != 0:
                                prop_summary.append(f"{k}: {v}")
                            elif isinstance(v, str) and len(v) < 50:
                                prop_summary.append(f"{k}: {v}")
                        
                        if prop_summary:
                            context_parts.append(f"  - {', '.join(prop_summary)}")
                
                if len(entity_instances) > 3:
                    context_parts.append(f"  ... and {len(entity_instances) - 3} more")
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the AI"""
        return """You are an expert financial data analyst and ontology specialist working with the Kudwa Financial Platform.

Your role is to help users understand and analyze their financial ontology data, which consists of:
- ENTITIES: Core financial concepts (Reports, Accounts, Periods, Observations, etc.)
- RELATIONSHIPS: How entities connect to each other
- INSTANCES: Actual data records with real financial values

Key capabilities:
1. **Financial Analysis**: Calculate totals, analyze trends, identify patterns
2. **Ontology Explanation**: Explain entity relationships and data structure  
3. **Data Insights**: Provide meaningful insights from the available data
4. **Query Answering**: Answer specific questions about amounts, accounts, periods, etc.

Guidelines:
- Be precise and data-driven in your responses
- Use the provided context data to give accurate answers
- Format financial amounts clearly (e.g., $1,234,567.89)
- Explain your reasoning when doing calculations
- If data is missing or unclear, say so explicitly
- Focus on actionable insights, not just raw data dumps

The user's ontology context will be provided with their question."""
    
    def _create_user_prompt(self, user_message: str, context: str) -> str:
        """Create user prompt with context"""
        return f"""Based on my financial ontology data below, please answer this question:

QUESTION: {user_message}

ONTOLOGY CONTEXT:
{context}

Please provide a clear, insightful response based on the actual data shown above."""
    
    def _fallback_response(self, user_message: str, entities: List[Dict], relations: List[Dict], instances: List[Dict]) -> Dict[str, Any]:
        """Fallback response when AI is not available"""
        return {
            "text": f"""I'd love to help analyze your question: "{user_message}"

However, I need an OpenAI API key to provide intelligent responses. Currently I can see:
- {len(entities)} entities in your ontology
- {len(relations)} relationships mapped
- {len(instances)} data instances

To enable AI-powered analysis, please set your OPENAI_API_KEY environment variable.""",
            "widgets": [],
            "metadata": {
                "model": "fallback",
                "ai_enabled": False
            }
        }


# Global service instance
genai_service = GenAIService()
