#!/usr/bin/env python3
"""
Conversational Ontology Extension Agent
Simple chatbot that understands current ontology and proposes extensions
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from pydantic import BaseModel

class OntologyProposal(BaseModel):
    """Ontology extension proposal from the agent"""
    id: str
    type: str  # "class", "relation", "property"
    title: str
    description: str
    details: Dict[str, Any]
    reasoning: str
    confidence: float
    timestamp: datetime

class ConversationalOntologyAgent:
    """
    Conversational agent for ontology extension and discussion
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.pending_proposals = []
        
        # System prompt for ontology-aware conversation
        self.system_prompt = """
You are an expert ontology consultant and conversational AI assistant specializing in financial and business ontologies. Your role is to:

1. **Understand the Current Ontology**: You have deep knowledge of the existing ontology structure, including classes, relations, and data instances.

2. **Natural Conversation**: Engage in natural, helpful conversations about the ontology, answering questions about entities, relationships, and how data flows through the system.

3. **Propose Extensions**: When appropriate, suggest specific ontology extensions (new classes, relations, or properties) that would improve the system.

4. **Context Awareness**: Always consider the existing ontology structure when making suggestions to ensure consistency and avoid conflicts.

**Current Ontology Context** (you should reference this in conversations):
- **Domain**: Financial/Business ontology for fintech applications
- **Key Classes**: Revenue Account, Expense Account, Financial Transaction, Customer, Invoice, Payment Method, Tax Category, Business Process, Data Source
- **Key Relations**: contains, uses, generates, receives, applies, processes, manages
- **Data Types**: Monetary amounts, dates, account IDs, transaction records
- **Patterns**: Account → Transaction → Payment flows, Customer → Invoice → Revenue cycles

**When proposing extensions**, format them as:
```
PROPOSAL: [Type] - [Title]
DESCRIPTION: [Clear description]
DETAILS: [Specific implementation details]
REASONING: [Why this extension is valuable]
CONFIDENCE: [0.0-1.0]
```

**Guidelines**:
- Be conversational and helpful
- Ask clarifying questions when needed
- Reference existing ontology elements
- Explain relationships and data flows clearly
- Only propose extensions when they add clear value
- Consider real-world business scenarios
"""

    async def chat(self, user_message: str, current_ontology_state: Dict = None) -> Dict[str, Any]:
        """
        Process user message and return response with any proposals
        """
        try:
            # Add current ontology context to the conversation
            context_message = ""
            if current_ontology_state:
                classes_count = len(current_ontology_state.get("classes", []))
                relations_count = len(current_ontology_state.get("relations", []))
                observations_count = len(current_ontology_state.get("observations", []))
                
                context_message = f"""
Current Ontology State:
- {classes_count} ontology classes
- {relations_count} relations  
- {observations_count} data observations
- Recent classes: {', '.join([c.get('label', 'Unknown') for c in current_ontology_state.get('classes', [])[:5]])}
"""

            # Prepare conversation for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt + context_message}
            ]
            
            # Add conversation history (last 10 messages)
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            # Extract any proposals from the response
            proposals = self._extract_proposals(assistant_response)
            
            return {
                "response": assistant_response,
                "proposals": proposals,
                "conversation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "proposals": [],
                "error": str(e)
            }

    def _extract_proposals(self, response_text: str) -> List[OntologyProposal]:
        """
        Extract structured proposals from agent response
        """
        proposals = []
        lines = response_text.split('\n')
        
        current_proposal = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('PROPOSAL:'):
                if current_proposal:
                    # Save previous proposal
                    proposals.append(self._create_proposal(current_proposal))
                
                # Start new proposal
                proposal_info = line.replace('PROPOSAL:', '').strip()
                if ' - ' in proposal_info:
                    prop_type, title = proposal_info.split(' - ', 1)
                    current_proposal = {
                        'type': prop_type.strip().lower(),
                        'title': title.strip()
                    }
                else:
                    current_proposal = {
                        'type': 'class',
                        'title': proposal_info
                    }
            
            elif line.startswith('DESCRIPTION:'):
                current_proposal['description'] = line.replace('DESCRIPTION:', '').strip()
            
            elif line.startswith('DETAILS:'):
                current_proposal['details'] = line.replace('DETAILS:', '').strip()
            
            elif line.startswith('REASONING:'):
                current_proposal['reasoning'] = line.replace('REASONING:', '').strip()
            
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence_str = line.replace('CONFIDENCE:', '').strip()
                    current_proposal['confidence'] = float(confidence_str)
                except:
                    current_proposal['confidence'] = 0.8
        
        # Don't forget the last proposal
        if current_proposal:
            proposals.append(self._create_proposal(current_proposal))
        
        return proposals

    def _create_proposal(self, proposal_data: Dict) -> OntologyProposal:
        """
        Create a structured proposal object
        """
        return OntologyProposal(
            id=str(uuid.uuid4()),
            type=proposal_data.get('type', 'class'),
            title=proposal_data.get('title', 'Untitled Proposal'),
            description=proposal_data.get('description', ''),
            details=self._parse_details(proposal_data.get('details', '')),
            reasoning=proposal_data.get('reasoning', ''),
            confidence=proposal_data.get('confidence', 0.8),
            timestamp=datetime.now()
        )

    def _parse_details(self, details_text: str) -> Dict[str, Any]:
        """
        Parse details text into structured data
        """
        details = {"raw_text": details_text}
        
        # Try to extract structured information
        if "class_id:" in details_text.lower():
            # Extract class details
            for line in details_text.split(','):
                if ':' in line:
                    key, value = line.split(':', 1)
                    details[key.strip().lower()] = value.strip()
        
        return details

    def approve_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Mark a proposal as approved for implementation
        """
        for proposal in self.pending_proposals:
            if proposal.id == proposal_id:
                proposal_dict = proposal.dict()
                proposal_dict['status'] = 'approved'
                proposal_dict['approved_at'] = datetime.now().isoformat()
                
                # Remove from pending
                self.pending_proposals = [p for p in self.pending_proposals if p.id != proposal_id]
                
                return {
                    "success": True,
                    "message": f"Approved proposal: {proposal.title}",
                    "proposal": proposal_dict
                }
        
        return {
            "success": False,
            "message": "Proposal not found"
        }

    def reject_proposal(self, proposal_id: str, reason: str = "") -> Dict[str, Any]:
        """
        Mark a proposal as rejected
        """
        for proposal in self.pending_proposals:
            if proposal.id == proposal_id:
                # Remove from pending
                self.pending_proposals = [p for p in self.pending_proposals if p.id != proposal_id]
                
                return {
                    "success": True,
                    "message": f"Rejected proposal: {proposal.title}",
                    "reason": reason
                }
        
        return {
            "success": False,
            "message": "Proposal not found"
        }

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get summary of current conversation and proposals
        """
        return {
            "conversation_length": len(self.conversation_history),
            "pending_proposals": len(self.pending_proposals),
            "recent_topics": self._extract_topics(),
            "proposals": [p.dict() for p in self.pending_proposals]
        }

    def _extract_topics(self) -> List[str]:
        """
        Extract main topics from recent conversation
        """
        topics = []
        recent_messages = self.conversation_history[-6:]  # Last 3 exchanges
        
        for msg in recent_messages:
            if msg["role"] == "user":
                # Simple keyword extraction
                content = msg["content"].lower()
                if "account" in content:
                    topics.append("accounts")
                if "transaction" in content:
                    topics.append("transactions")
                if "customer" in content:
                    topics.append("customers")
                if "process" in content:
                    topics.append("business processes")
        
        return list(set(topics))

# Global agent instance
ontology_agent = None

def get_ontology_agent() -> ConversationalOntologyAgent:
    """Get or create the ontology agent"""
    global ontology_agent
    if ontology_agent is None:
        ontology_agent = ConversationalOntologyAgent()
    return ontology_agent
