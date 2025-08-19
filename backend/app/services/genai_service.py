"""
GenAI Service - Real AI/LLM integration for intelligent responses
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
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

    def generate_component_specification(
        self,
        user_prompt: str,
        entities: List[Dict],
        relations: List[Dict],
        instances: List[Dict]
    ) -> Dict[str, Any]:
        """Generate a component specification based on user prompt and ontology data"""

        print(f"\n🎨 === COMPONENT GENERATION PROCESSING STARTED ===")
        print(f"📝 User Prompt: '{user_prompt}'")
        print(f"📊 Context: {len(entities)} entities, {len(relations)} relations, {len(instances)} instances")

        if not self.use_openai:
            return self._fallback_component_response(user_prompt, entities, relations, instances)

        try:
            # Build rich context for component generation
            context = self._build_ai_context(entities, relations, instances)

            # Create the AI prompt for component generation
            system_prompt = self._create_component_system_prompt()
            user_prompt_formatted = self._create_component_user_prompt(user_prompt, context)

            print(f"🧠 Sending component generation request to GPT-4...")
            print(f"📏 System prompt: {len(system_prompt)} chars")
            print(f"📏 User prompt: {len(user_prompt_formatted)} chars")

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_formatted}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            ai_response = response.choices[0].message.content

            print(f"✅ GPT-4 Component Response: {len(ai_response)} characters")
            print(f"💰 Token usage: {response.usage.total_tokens} tokens")

            # Parse the AI response to extract component specification
            component_spec = self._parse_component_response(ai_response)

            print(f"🎨 === COMPONENT GENERATION PROCESSING COMPLETED ===\n")

            return component_spec

        except Exception as e:
            print(f"❌ Component GenAI Error: {e}")
            return self._fallback_component_response(user_prompt, entities, relations, instances)
    
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

    def _create_component_system_prompt(self) -> str:
        """Create system prompt for component generation"""
        return """You are an expert UI/UX designer and data visualization specialist working with the Kudwa Financial Platform.

Your role is to analyze user requests and generate component specifications for dynamic interface elements. You work with financial ontology data consisting of:
- ENTITIES: Core financial concepts (Reports, Accounts, Periods, Observations, etc.)
- RELATIONSHIPS: How entities connect to each other
- INSTANCES: Actual data records with real financial values

COMPONENT TYPES YOU CAN CREATE:
1. **metric_card**: Single KPI or metric display
2. **chart**: Bar charts, line charts, area charts for data visualization
3. **table**: Data tables showing detailed records
4. **kpi_dashboard**: Multiple related metrics in a dashboard layout

RESPONSE FORMAT:
You must respond with a valid JSON object containing:
{
  "type": "metric_card|chart|table|kpi_dashboard",
  "title": "Component Title",
  "description": "Brief description of what this component shows",
  "data": {
    // Component-specific data structure
  },
  "chart_type": "bar|line|area" // Only for chart components
}

COMPONENT DATA STRUCTURES:

For metric_card:
{
  "type": "metric_card",
  "title": "Total Revenue",
  "data": {
    "label": "Total Revenue",
    "value": "1,234,567",
    "delta": "+12.5%"
  }
}

For chart:
{
  "type": "chart",
  "chart_type": "bar",
  "title": "Revenue by Account",
  "data": {
    "Account A": 100000,
    "Account B": 150000,
    "Account C": 200000
  }
}

For table:
{
  "type": "table",
  "title": "Recent Transactions",
  "data": [
    {"account": "Account A", "amount": 1000, "date": "2024-01-01"},
    {"account": "Account B", "amount": 1500, "date": "2024-01-02"}
  ]
}

For kpi_dashboard:
{
  "type": "kpi_dashboard",
  "title": "Financial Overview",
  "data": {
    "kpis": [
      {"label": "Total Revenue", "value": "1.2M", "delta": "+5%"},
      {"label": "Total Expenses", "value": "800K", "delta": "-2%"},
      {"label": "Net Profit", "value": "400K", "delta": "+15%"}
    ]
  }
}

IMPORTANT:
- Always use real data from the provided ontology context
- Calculate actual values, don't use placeholder numbers
- Ensure the component type matches the user's request
- Make titles descriptive and professional
- Use appropriate chart types for the data being displayed"""

    def _create_component_user_prompt(self, user_prompt: str, context: str) -> str:
        """Create user prompt for component generation"""

        # Extract and summarize numerical data for better component generation
        data_summary = self._extract_data_summary_for_components(context)

        return f"""USER REQUEST: {user_prompt}

AVAILABLE ONTOLOGY DATA:
{context}

DATA SUMMARY FOR VISUALIZATION:
{data_summary}

Based on the user request and available data, generate a component specification that:
1. Matches the user's intent (chart, metric, table, etc.)
2. Uses real data from the ontology context above
3. Provides meaningful insights from the financial data
4. Follows the exact JSON format specified in the system prompt
5. IMPORTANT: Use actual numerical values from the data summary above

Respond with ONLY the JSON component specification, no additional text."""

    def _extract_data_summary_for_components(self, context: str) -> str:
        """Extract numerical data summary from context for component generation"""
        summary_parts = []

        # Look for numerical patterns in the context
        import re

        # Find amounts/values
        amount_pattern = r'amount[:\s]*([0-9,.-]+)'
        amounts = re.findall(amount_pattern, context, re.IGNORECASE)
        if amounts:
            try:
                numeric_amounts = [float(a.replace(',', '')) for a in amounts if a.replace(',', '').replace('-', '').replace('.', '').isdigit()]
                if numeric_amounts:
                    summary_parts.append(f"Found {len(numeric_amounts)} amount values: {numeric_amounts[:5]}")
                    summary_parts.append(f"Total: {sum(numeric_amounts)}, Average: {sum(numeric_amounts)/len(numeric_amounts):.2f}")
            except:
                pass

        # Find dates for time series
        date_pattern = r'(20\d{2}[-/]\d{1,2}[-/]\d{1,2})'
        dates = re.findall(date_pattern, context)
        if dates:
            unique_dates = list(set(dates))
            summary_parts.append(f"Found {len(unique_dates)} unique dates: {sorted(unique_dates)[:5]}")

        # Find account names/entities
        entity_pattern = r"Entity '([^']+)'"
        entities = re.findall(entity_pattern, context)
        if entities:
            unique_entities = list(set(entities))
            summary_parts.append(f"Available entities: {unique_entities[:5]}")

        # Find properties with numerical values
        prop_pattern = r'(\w+):\s*([0-9,.-]+)'
        props = re.findall(prop_pattern, context)
        if props:
            numerical_props = {}
            for prop_name, prop_value in props:
                try:
                    num_val = float(prop_value.replace(',', ''))
                    if prop_name not in numerical_props:
                        numerical_props[prop_name] = []
                    numerical_props[prop_name].append(num_val)
                except:
                    continue

            if numerical_props:
                summary_parts.append("Numerical properties found:")
                for prop, values in numerical_props.items():
                    summary_parts.append(f"  - {prop}: {len(values)} values, total: {sum(values)}")

        return "\n".join(summary_parts) if summary_parts else "No numerical data found in context"

    def _parse_component_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response to extract component specification"""
        try:
            # Try to extract JSON from the response
            import json
            import re

            # Look for JSON content in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                component_spec = json.loads(json_str)

                # Validate required fields
                if "type" not in component_spec:
                    component_spec["type"] = "metric_card"
                if "title" not in component_spec:
                    component_spec["title"] = "Generated Component"
                if "data" not in component_spec:
                    component_spec["data"] = {}

                return component_spec
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"❌ Error parsing component response: {e}")
            print(f"📝 Raw response: {ai_response}")

            # Return a fallback component
            return {
                "type": "metric_card",
                "title": "Component Generation Error",
                "description": "Failed to parse AI response",
                "data": {
                    "label": "Error",
                    "value": "N/A",
                    "delta": None
                }
            }

    def _fallback_component_response(self, user_prompt: str, entities: List[Dict], relations: List[Dict], instances: List[Dict]) -> Dict[str, Any]:
        """Fallback component response when AI is not available"""

        # Try to create a meaningful component based on the prompt
        prompt_lower = user_prompt.lower()

        if "chart" in prompt_lower or "graph" in prompt_lower or "time series" in prompt_lower:
            # Create a sample chart with dummy data
            return {
                "type": "chart",
                "chart_type": "line",
                "title": "Sample Time Series (AI Unavailable)",
                "description": "Sample data - enable AI for real analysis",
                "data": {
                    "2024-01": 1000,
                    "2024-02": 1200,
                    "2024-03": 1100,
                    "2024-04": 1300
                }
            }
        elif "metric" in prompt_lower or "kpi" in prompt_lower:
            return {
                "type": "metric_card",
                "title": "Sample Metric",
                "description": "Sample metric - enable AI for real analysis",
                "data": {
                    "label": "Total Records",
                    "value": str(len(instances)),
                    "delta": "+5%"
                }
            }
        elif "table" in prompt_lower:
            # Create a table with sample instance data
            table_data = []
            for i, instance in enumerate(instances[:5]):
                properties = instance.get('properties', {})
                row = {"id": i+1}
                row.update(properties)
                table_data.append(row)

            return {
                "type": "table",
                "title": "Sample Data Table",
                "description": "Sample data - enable AI for real analysis",
                "data": table_data if table_data else [{"message": "No data available"}]
            }
        else:
            # Default KPI dashboard
            return {
                "type": "kpi_dashboard",
                "title": "Ontology Overview",
                "description": f"Basic overview of your ontology data (AI unavailable)",
                "data": {
                    "kpis": [
                        {"label": "Entities", "value": str(len(entities)), "delta": None},
                        {"label": "Relations", "value": str(len(relations)), "delta": None},
                        {"label": "Instances", "value": str(len(instances)), "delta": None}
                    ]
                }
            }

    def refresh_component_data(
        self,
        component_spec: Dict[str, Any],
        entities: List[Dict],
        relations: List[Dict],
        instances: List[Dict]
    ) -> Dict[str, Any]:
        """Refresh component data with latest ontology information"""

        print(f"\n🔄 === COMPONENT DATA REFRESH PROCESSING ===")

        try:
            # Extract the original prompt/intent from component if available
            original_title = component_spec.get("title", "Component")
            component_type = component_spec.get("type", "metric_card")

            # Create a refresh prompt based on the component
            refresh_prompt = f"Update the '{original_title}' {component_type} with the latest data"

            # Use the same generation logic but with fresh data
            if self.use_openai:
                context = self._build_ai_context(entities, relations, instances)
                system_prompt = self._create_component_system_prompt()
                user_prompt = self._create_component_user_prompt(refresh_prompt, context)

                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )

                ai_response = response.choices[0].message.content
                refreshed_spec = self._parse_component_response(ai_response)

                print(f"✅ Component data refreshed with AI")
                return refreshed_spec
            else:
                # Fallback: just update basic metrics
                if component_type == "kpi_dashboard":
                    return {
                        "type": "kpi_dashboard",
                        "title": original_title,
                        "description": "Refreshed ontology overview",
                        "data": {
                            "kpis": [
                                {"label": "Entities", "value": str(len(entities)), "delta": None},
                                {"label": "Relations", "value": str(len(relations)), "delta": None},
                                {"label": "Instances", "value": str(len(instances)), "delta": None}
                            ]
                        }
                    }
                else:
                    # Return the original component with updated timestamp
                    refreshed_spec = component_spec.copy()
                    refreshed_spec["last_updated"] = datetime.now().isoformat()
                    return refreshed_spec

        except Exception as e:
            print(f"❌ Component refresh error: {e}")
            # Return original component if refresh fails
            return component_spec


# Global service instance
genai_service = GenAIService()
