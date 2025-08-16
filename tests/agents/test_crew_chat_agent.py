import pytest
from agents.crew_chat_agent import CrewChatAgent

@pytest.mark.asyncio
async def test_visualization_handling():
    agent = CrewChatAgent()
    message = "Visualize monthly revenue as a bar chart"
    context = {"user_id": "test_user"}
    
    response = await agent.process_chat_message(message, context)
    
    assert response["success"] is True
    assert "gadget_spec" in response
    assert response["agent_type"] == "visualization_engineer"
    assert "bar" in response["response"].lower()
    assert "interactive visualization" in response["gadget_spec"].lower()
