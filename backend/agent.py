import os
import yaml
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

class TravelPlanRequest(BaseModel):
    destination: str
    travel_dates: str
    traveler_preferences: str
    budget: str
    constraints: str

# Use the yaml we just generated as the prompt context
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

def query_travel_engine(request: TravelPlanRequest) -> dict:
    # Initialize using Vertex AI explicitly with provided Project ID
    try:
        client = genai.Client(vertexai=True, project="promptwars-gurgaon", location="us-central1")
    except Exception as e:
        # Fallback dummy response if GenAI cannot be initialized (useful for visual testing without credentials)
        return {
            "destination": request.destination,
            "travel_dates": request.travel_dates,
            "itinerary": [
                {"day": 1, "activities": ["Arrive at destination", "Check-in to hotel", "Dinner at local restaurant"]},
                {"day": 2, "activities": ["Morning sightseeing", "Lunch", "Afternoon activity matching requirements"]}
            ],
            "transport": "Sample Recommended Flight + Local Transit",
            "accommodation": f"Premium hotel within {request.budget} budget",
            "activities": ["Sightseeing", "Relaxation"],
            "dining": ["Local recommendations based on dietary needs"],
            "estimated_budget": request.budget,
            "live_alerts": [{"severity": "low", "message": "Minor traffic expected near city center."}],
            "contingency_plan": ["If flight delayed, hotel late check-in is pre-arranged."],
            "traveler_advisories": ["Keep valuables secure in crowded areas."],
            "compliance_status": "Valid and Verified",
            "note": "NOTE: MOCK DATA. Make sure your ADC (gcloud auth application-default login) is active for project promptwars-gurgaon."
        }

    sys_instruct = construct_system_instruction()
    user_prompt = f"""
    Generate a travel plan for the following request:
    Destination: {request.destination}
    Dates: {request.travel_dates}
    Preferences: {request.traveler_preferences}
    Budget: {request.budget}
    Constraints: {request.constraints}
    
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
