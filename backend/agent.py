import os
import yaml
import json
from openai import OpenAI
from typing import Dict, Any

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
    try:
        # Initialize OpenAI Client (assumes OPENAI_API_KEY is in environment)
        client = OpenAI()
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
            "note": "NOTE: MOCK DATA. Ensure OPENAI_API_KEY is set for real orchestration."
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
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": sys_instruct},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.4
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "message": "Failed to generate travel plan from OpenAI."}
