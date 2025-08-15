#!/usr/bin/env python3
"""
Mock N8N Webhook Server for Testing Kudwa Dashboard
Returns realistic responses to test the full UI flow
"""

from fastapi import FastAPI, Request
import uvicorn
import json
from datetime import datetime
import uuid

app = FastAPI(title="Mock N8N Webhook", description="Test webhook for Kudwa dashboard")

@app.post("/webhook/ontology-extension")
async def ontology_extension_webhook(request: Request):
    """Mock ontology extension webhook that returns realistic responses"""
    try:
        body = await request.json()
        print(f"📨 Received webhook request: {json.dumps(body, indent=2)}")
        
        # Extract message and file info
        message = body.get('message', '')
        filename = body.get('filename', '')
        file_content = body.get('file_content', '')
        
        # Simulate processing delay
        import time
        time.sleep(1)
        
        # Generate realistic response based on input
        if filename:
            response = {
                "response": f"🔍 Analyzed document '{filename}' and found several potential ontology extensions. Here are my recommendations for improving your financial data model:",
                "response_type": "ontology_proposal",
                "confidence_score": 0.92,
                "requires_user_input": True,
                "ontology_extensions": [
                    {
                        "id": f"ext-{uuid.uuid4().hex[:8]}",
                        "entity_type": "PaymentTransaction",
                        "description": "Financial transaction entity with amount, currency, and parties involved",
                        "properties": [
                            {"name": "amount", "type": "decimal", "required": True},
                            {"name": "currency", "type": "string", "required": True},
                            {"name": "transaction_date", "type": "datetime", "required": True},
                            {"name": "reference_number", "type": "string", "required": False}
                        ],
                        "relationships": [
                            {"target_entity": "Account", "relationship_type": "debits_from", "description": "Source account for transaction"},
                            {"target_entity": "Account", "relationship_type": "credits_to", "description": "Destination account for transaction"}
                        ],
                        "justification": "Document contains transaction data that needs structured representation",
                        "confidence": 0.92
                    },
                    {
                        "id": f"ext-{uuid.uuid4().hex[:8]}",
                        "entity_type": "Counterparty",
                        "description": "External party involved in financial transactions",
                        "properties": [
                            {"name": "name", "type": "string", "required": True},
                            {"name": "identifier", "type": "string", "required": False},
                            {"name": "type", "type": "string", "required": True}
                        ],
                        "relationships": [
                            {"target_entity": "PaymentTransaction", "relationship_type": "participates_in", "description": "Links counterparty to transactions"}
                        ],
                        "justification": "Need to track external parties in transactions",
                        "confidence": 0.87
                    }
                ],
                "data_entry_proposals": [
                    {
                        "id": f"data-{uuid.uuid4().hex[:8]}",
                        "entity_type": "PaymentTransaction",
                        "proposed_data": {
                            "amount": 1250.00,
                            "currency": "USD",
                            "transaction_date": "2024-01-15T10:30:00Z",
                            "reference_number": "TXN-2024-001"
                        },
                        "source_reference": f"Extracted from {filename}",
                        "confidence": 0.95
                    }
                ],
                "suggested_actions": [
                    {
                        "id": "action-1",
                        "label": "Review Ontology Extensions",
                        "action_type": "review_proposal",
                        "target": "ontology_extensions",
                        "style": "primary"
                    },
                    {
                        "id": "action-2",
                        "label": "Upload More Documents",
                        "action_type": "upload_document",
                        "target": "document_processor",
                        "style": "info"
                    }
                ],
                "context_needed": [],
                "sources": [
                    {
                        "document_id": filename,
                        "page": 1,
                        "section": "transaction_data",
                        "relevance_score": 0.95
                    }
                ]
            }
        else:
            # Chat-only response
            response = {
                "response": f"💬 I understand you're asking: '{message}'\n\nI can help extend your ontology by analyzing documents and suggesting new entities, relationships, and properties. Upload a document to get started, or ask me specific questions about ontology modeling for financial systems.",
                "response_type": "conversational",
                "confidence_score": 0.85,
                "requires_user_input": False,
                "ontology_extensions": [],
                "data_entry_proposals": [],
                "suggested_actions": [
                    {
                        "id": "action-upload",
                        "label": "Upload Financial Document",
                        "action_type": "upload_document",
                        "target": "document_processor",
                        "style": "primary"
                    },
                    {
                        "id": "action-ask",
                        "label": "Ask Specific Question",
                        "action_type": "request_clarification",
                        "target": "chat_input",
                        "style": "info"
                    }
                ],
                "context_needed": ["Upload a document or ask a specific ontology question"],
                "sources": []
            }
        
        print(f"📤 Sending response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return {
            "response": f"⚠️ Error processing your request: {str(e)}",
            "response_type": "conversational",
            "confidence_score": 0.0,
            "requires_user_input": False,
            "ontology_extensions": [],
            "data_entry_proposals": [],
            "suggested_actions": [],
            "context_needed": ["Please try again or contact support"],
            "sources": []
        }

@app.get("/")
async def root():
    return {
        "message": "Mock N8N Webhook Server for Kudwa",
        "endpoints": {
            "ontology_extension": "/webhook/ontology-extension"
        },
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🚀 Starting Mock N8N Webhook Server...")
    print("📍 Ontology Extension Webhook: http://localhost:8052/webhook/ontology-extension")
    print("🔍 Health Check: http://localhost:8052/health")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8052, log_level="info")
