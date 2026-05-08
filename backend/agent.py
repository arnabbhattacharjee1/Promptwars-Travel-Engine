import os
import yaml
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env
load_dotenv()

# Load Agent Specification
with open(os.path.join(os.path.dirname(__file__), '..', 'docs', 'agent_specification.yaml'), 'r') as f:
    AGENT_SPEC = yaml.safe_load(f)

def construct_system_instruction() -> str:
    return f"""
    You are the {AGENT_SPEC['role']}.
    Intent: {AGENT_SPEC['intent']}
    
    Context:
    {yaml.dump(AGENT_SPEC['context'])}
    
    Enforcement Rules:
    {yaml.dump(AGENT_SPEC['enforcement'])}
    
    Decision Logic:
    {yaml.dump(AGENT_SPEC['decision_logic'])}
    
    Validation Rules:
    {yaml.dump(AGENT_SPEC['validation_rules'])}
    """

def query_travel_engine(request_data: Dict[str, Any]) -> dict:
    api_key = os.getenv("GOOGLE_API_KEY")
    
    try:
        # Initialize Gemini Client
        # Note: If api_key is missing, this will raise an error and go to fallback
        client = genai.Client(api_key=api_key)
    except Exception:
        # Fallback dummy response for testing
        return {
            "destination": request_data.get('destination'),
            "travel_dates": request_data.get('travel_dates'),
            "itinerary": [
                {"day": 1, "activities": ["Arrive at destination", "Check-in to hotel"]},
                {"day": 2, "activities": ["Sightseeing and cultural exploration"]}
            ],
            "transport": "Sample Optimized Transit",
            "accommodation": "Premium accommodation within budget",
            "activities": ["Cultural tours", "Local dining"],
            "dining": ["Traditional cuisine recommendations"],
            "estimated_budget": request_data.get('budget'),
            "live_alerts": [{"severity": "low", "message": "Weather is clear."}],
            "contingency_plan": ["Fallback transit options identified."],
            "traveler_advisories": ["Standard safety precautions apply."],
            "compliance_status": "Valid",
            "note": "NOTE: MOCK DATA. Ensure GOOGLE_API_KEY is correctly set in your .env for Gemini."
        }

    sys_instruct = construct_system_instruction()
    user_prompt = f"""
    Generate a travel plan for the following request:
    Destination: {request_data.get('destination')}
    Dates: {request_data.get('travel_dates')}
    Preferences: {request_data.get('traveler_preferences')}
    Budget: {request_data.get('budget')}
    Constraints: {request_data.get('constraints')}
    
    Return pure JSON mapping exactly to this output schema:
    {yaml.dump(AGENT_SPEC['output_schema'])}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                response_mime_type="application/json",
                temperature=0.4
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e), "message": "Failed to generate travel plan from Gemini."}
