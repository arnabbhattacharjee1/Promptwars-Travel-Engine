import pytest
import json
from backend.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    """Test that the root endpoint serves the index.html."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data

def test_plan_travel_api_mocked(client, monkeypatch):
    """Test the POST endpoint with mocked engine logic."""
    
    def mock_query(request_data):
        return {"destination": "Mocked Kyoto", "status": "Success"}
    
    # Patch the engine query in main
    monkeypatch.setattr("backend.main.query_travel_engine", mock_query)
    
    payload = {
        "destination": "Kyoto",
        "travel_dates": "Oct 2026",
        "traveler_preferences": "Tea",
        "budget": "$1000",
        "constraints": "None"
    }
    
    response = client.post('/api/plan-travel', 
                            data=json.dumps(payload),
                            content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["destination"] == "Mocked Kyoto"
