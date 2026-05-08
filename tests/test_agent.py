import pytest
import json
from unittest.mock import MagicMock
from backend.agent import query_travel_engine, construct_system_instruction

@pytest.fixture
def mock_gemini_client():
    client = MagicMock()
    # Mock response object
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "destination": "Test City",
        "itinerary": [{"day": 1, "activities": ["Test Activity"]}],
        "compliance_status": "Valid"
    })
    client.models.generate_content.return_value = mock_response
    return client

def test_construct_system_instruction():
    """Verify that the system instruction is built and contains key info."""
    instruction = construct_system_instruction()
    assert "Travel Planning & Experience Engine" in instruction
    assert "Intent:" in instruction

def test_query_travel_engine_with_mock(mock_gemini_client):
    """Test the engine logic with a mocked Gemini client."""
    request_data = {
        "destination": "Kyoto",
        "budget": "$2000"
    }
    
    result = query_travel_engine(request_data, client=mock_gemini_client)
    
    assert result["destination"] == "Test City"
    assert "itinerary" in result
    mock_gemini_client.models.generate_content.assert_called_once()

def test_query_travel_engine_fallback(monkeypatch):
    """Test the fallback mechanism when client initialization fails."""
    
    def mock_fail():
        raise Exception("Client init failed")
    
    # Patch get_gemini_client in the agent module
    monkeypatch.setattr("backend.agent.get_gemini_client", mock_fail)
    
    request_data = {"destination": "Mars", "budget": "Expensive"}
    result = query_travel_engine(request_data, client=None)
    
    assert "NOTE: MOCK DATA" in result.get("note", "")
    assert result["destination"] == "Mars"
