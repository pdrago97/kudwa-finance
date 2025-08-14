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
                "assistant_text": f"🔍 Analyzed document '{filename}' and found several potential ontology extensions. Here are my recommendations:",
                "proposals": [
                    {
                        "id": f"prop-{uuid.uuid4().hex[:8]}",
                        "type": "Entity",
                        "name": "PaymentTransaction",
                        "description": "Financial transaction entity with amount, currency, and parties",
                        "action": "add",
                        "confidence": 0.92
                    },
                    {
                        "id": f"prop-{uuid.uuid4().hex[:8]}",
                        "type": "Relationship", 
                        "name": "involves_counterparty",
                        "description": "Links transactions to counterparty entities",
                        "action": "add",
                        "confidence": 0.87
                    },
                    {
                        "id": f"prop-{uuid.uuid4().hex[:8]}",
                        "type": "Property",
                        "name": "transaction_date",
                        "description": "ISO date when transaction occurred",
                        "action": "add",
                        "confidence": 0.95
                    }
                ],
                "extracted_entities": [
                    {"type": "Amount", "value": "$1,250.00", "confidence": 0.98},
                    {"type": "Date", "value": "2024-01-15", "confidence": 0.94},
                    {"type": "Company", "value": "Acme Corp", "confidence": 0.89}
                ],
                "meta": {
                    "processing_time_ms": 1200,
                    "document_type": "financial_document",
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            # Chat-only response
            response = {
                "assistant_text": f"💬 I understand you're asking: '{message}'\n\nI can help extend your ontology by analyzing documents and suggesting new entities, relationships, and properties. Upload a document to get started, or ask me specific questions about ontology modeling for financial systems.",
                "suggestions": [
                    "Upload a financial document (PDF, CSV, TXT) to extract entities",
                    "Ask about specific entity types like 'What properties should a Transaction have?'",
                    "Request relationship modeling: 'How should Customers relate to Accounts?'"
                ],
                "meta": {
                    "processing_time_ms": 300,
                    "status": "success", 
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        print(f"📤 Sending response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return {
            "assistant_text": f"⚠️ Error processing your request: {str(e)}",
            "meta": {
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
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
    print("📍 Ontology Extension Webhook: http://localhost:8765/webhook/ontology-extension")
    print("🔍 Health Check: http://localhost:8765/health")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
