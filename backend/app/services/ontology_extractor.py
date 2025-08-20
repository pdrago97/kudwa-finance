import json
import os
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class OntologyExtractor:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-placeholder"):
            print(f"Warning: OPENAI_API_KEY not properly set for ontology extraction")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=api_key,
                temperature=0.1
            )
    
    def extract_ontology_from_json(self, json_data: dict, filename: str) -> Dict[str, List[Dict]]:
        """Extract entities, relations, and instances from JSON data"""

        if not self.llm:
            print("Warning: No LLM available for ontology extraction")
            return {"entities": [], "relations": [], "instances": []}

        # Convert JSON to string for analysis - limit size more aggressively
        json_str = json.dumps(json_data, indent=2)

        # If too large, truncate more aggressively
        if len(json_str) > 2000:
            # Try to get a representative sample
            if isinstance(json_data, dict):
                # Take first few keys and their values
                sample_data = {}
                count = 0
                for key, value in json_data.items():
                    if count >= 3:  # Only take first 3 keys
                        break
                    if isinstance(value, list) and len(value) > 2:
                        # For arrays, take first 2 items
                        sample_data[key] = value[:2]
                    else:
                        sample_data[key] = value
                    count += 1
                json_str = json.dumps(sample_data, indent=2)
            elif isinstance(json_data, list):
                # For arrays, take first 3 items
                json_str = json.dumps(json_data[:3], indent=2)

        # Final safety truncation
        json_str = json_str[:1500]
        
        system_prompt = """You are an expert in ontology design and financial data modeling. 
        
        Your task is to analyze JSON data and propose ontology extensions following this financial domain model:

        REFERENCE ONTOLOGY (use as guidance):
        Classes: Report, Section, Account, Period, Observation
        Properties: reportBasis, currency, startDate, endDate, accountId, accountName, sectionName, periodKey, amount
        Relations: hasSection, hasAccount, hasPeriod, forReport, forSection, forAccount, forPeriod

        Analyze the provided JSON and return ONLY a valid JSON response with three arrays:

        {
          "entities": [
            {"name": "EntityName", "properties": {"prop1": "description", "prop2": "description"}}
          ],
          "relations": [
            {"source": "EntityA", "target": "EntityB", "type": "relationName", "properties": {}}
          ],
          "instances": [
            {"entity": "EntityName", "properties": {"prop1": "value1", "prop2": "value2"}}
          ]
        }

        Focus on:
        1. Identifying core business entities (like Report, Account, Period, etc.)
        2. Finding repeated data patterns that represent instances
        3. Discovering relationships between entities
        4. Extracting meaningful properties and their values

        Be conservative and only propose clear, well-defined entities and relations."""

        human_prompt = f"""Analyze this JSON data from file '{filename}':

        {json_str}

        Extract the ontology (entities, relations, instances) as JSON."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        print(f"Sending {len(json_str)} characters to LLM for ontology extraction")
        response = self.llm.invoke(messages)
        print(f"LLM response received: {len(response.content)} characters")
        
        try:
            # Clean the response content (remove markdown code blocks if present)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove ```
            content = content.strip()

            # Parse the cleaned JSON
            result = json.loads(content)

            # Validate structure
            if not all(key in result for key in ["entities", "relations", "instances"]):
                raise ValueError("Missing required keys in ontology extraction")

            return result
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Response: {response.content}")
            # Return empty structure on parse failure
            return {"entities": [], "relations": [], "instances": []}
    
    def create_proposals(self, ontology_data: Dict[str, List[Dict]], file_id: str) -> List[Dict]:
        """Convert ontology extraction into proposal format"""
        proposals = []
        
        # Entity proposals
        for entity in ontology_data.get("entities", []):
            proposals.append({
                "type": "entity",
                "payload": {
                    "name": entity["name"],
                    "properties": entity.get("properties", {}),
                    "source_file_id": file_id
                }
            })
        
        # Relation proposals
        for relation in ontology_data.get("relations", []):
            proposals.append({
                "type": "relation",
                "payload": {
                    "source": relation["source"],
                    "target": relation["target"],
                    "rel_type": relation["type"],
                    "properties": relation.get("properties", {}),
                    "source_file_id": file_id
                }
            })
        
        # Instance proposals
        for instance in ontology_data.get("instances", []):
            proposals.append({
                "type": "instance",
                "payload": {
                    "entity": instance["entity"],
                    "properties": instance.get("properties", {}),
                    "source_file_id": file_id
                }
            })
        
        return proposals

# Global instance
ontology_extractor = OntologyExtractor()
