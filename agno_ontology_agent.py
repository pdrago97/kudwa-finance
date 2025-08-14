#!/usr/bin/env python3
"""
Simple N8N Webhook Caller for Ontology Agent
Calls n8n webhook with MCP tools and Supabase integration
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
from pydantic import BaseModel

class N8NOntologyAgent:
    """
    Simple agent that calls n8n webhook for ontology management
    """

    def __init__(self):
        # N8N webhook URL
        self.n8n_webhook_url = "https://n8n-moveup-u53084.vm.elestio.app/webhook-test/9ba11544-5c4e-4f91-818a-08a4ecb596c5"

        # Optional context from environment
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    async def chat_with_n8n_agent(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send message to n8n webhook agent
        """
        try:
            # Prepare payload for n8n webhook
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
                "supabase_config": {
                    "url": self.supabase_url,
                    "key": self.supabase_key
                } if self.supabase_url and self.supabase_key else None
            }

            # Call n8n webhook
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.n8n_webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "kudwa-ontology-agent-2024"
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": result.get("response", "N8N agent processed your request"),
                        "proposals": result.get("proposals", []),
                        "tool_results": result.get("tool_results", {}),
                        "n8n_status": "success",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "response": f"N8N webhook returned status {response.status_code}: {response.text}",
                        "proposals": [],
                        "tool_results": {},
                        "n8n_status": "error",
                        "error": f"HTTP {response.status_code}"
                    }

        except httpx.TimeoutException:
            return {
                "response": "N8N webhook request timed out. The agent may still be processing your request.",
                "proposals": [],
                "tool_results": {},
                "n8n_status": "timeout",
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "response": f"Error calling N8N webhook: {str(e)}",
                "proposals": [],
                "tool_results": {},
                "n8n_status": "error",
                "error": str(e)
            }

    async def test_n8n_webhook(self) -> Dict[str, Any]:
        """
        Test the n8n webhook connection
        """
        return await self.chat_with_n8n_agent("Test connection", {"test": True})

# Global agent instance
n8n_agent = None

def get_n8n_agent() -> N8NOntologyAgent:
    """Get or create n8n agent instance"""
    global n8n_agent
    if n8n_agent is None:
        n8n_agent = N8NOntologyAgent()
    return n8n_agent
