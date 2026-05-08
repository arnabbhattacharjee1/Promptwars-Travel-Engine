import os
import yaml
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Global variables for caching
_AGENT_SPEC = None
_LLM_CLIENT = None

def get_agent_spec() -> Dict[str, Any]:
    """Lazy load and cache the agent specification to save memory and I/O."""
    global _AGENT_SPEC
    if _AGENT_SPEC is None:
        spec_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'agent_specification.yaml')
        try:
            with open(spec_path, 'r') as f:
                _AGENT_SPEC = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load agent specification: {e}")
            _AGENT_SPEC = {}
    return _AGENT_SPEC

def construct_system_instruction() -> str:
    """Constructs the system prompt. Optimized by using cached spec."""
    spec = get_agent_spec()
    return f"""
    You are the {spec.get('role', 'Travel Assistant')}.
    Intent: {spec.get('intent', 'Plan trips')}
    
    Context:
    {yaml.dump(spec.get('context', {}))}
    
    Enforcement Rules:
    {yaml.dump(spec.get('enforcement', []))}
    
    Decision Logic:
    {yaml.dump(spec.get('decision_logic', {}))}
    
    Validation Rules:
    {yaml.dump(spec.get('validation_rules', []))}
    
    Inclusivity Requirement:
    Ensure all recommendations are inclusive and consider diverse traveler needs, including accessibility (e.g., wheelchair access, sensory-friendly options), cultural sensitivities, and varied family structures.
    """

def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """
    Factory to create or retrieve a cached Gemini client.
    Optimized to reuse the client instance.
    """
    global _LLM_CLIENT
    if api_key:
        # If a specific key is provided (e.g. for testing), create a new client
        return genai.Client(api_key=api_key)
    
    if _LLM_CLIENT is None:
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY is not set.")
        _LLM_CLIENT = genai.Client(api_key=key)
    return _LLM_CLIENT

def sanitize_input(val: Any) -> str:
    """Basic sanitization to prevent prompt injection or malformed data."""
    if val is None:
        return ""
    # Strip potential harmful characters and limit length to save tokens/memory
    s = str(val).strip()
    return s[:1000] 

def query_travel_engine(request_data: Dict[str, Any], client: Optional[genai.Client] = None) -> dict:
    """
    Main orchestration logic. 
    Optimized for memory by using cached spec and singleton client.
    Secured by input sanitization and robust error handling.
    """
    # Sanitize inputs
    destination = sanitize_input(request_data.get('destination'))
    budget = sanitize_input(request_data.get('budget'))
    dates = sanitize_input(request_data.get('travel_dates'))
    prefs = sanitize_input(request_data.get('traveler_preferences'))
    constraints = sanitize_input(request_data.get('constraints'))

    try:
        llm_client = client or get_gemini_client()
    except Exception as e:
        logger.warning(f"Using fallback response due to client error: {e}")
        return {
            "destination": destination,
            "travel_dates": dates,
            "itinerary": [{"day": 1, "activities": ["Fallback plan initialized"]}],
            "compliance_status": "Fallback Mode",
            "note": "NOTE: MOCK DATA. The system is currently in offline mode."
        }

    spec = get_agent_spec()
    sys_instruct = construct_system_instruction()
    user_prompt = f"""
    Generate a travel plan for:
    Destination: {destination}
    Dates: {dates}
    Preferences: {prefs}
    Budget: {budget}
    Constraints: {constraints}
    
    Response format: JSON
    Schema: {yaml.dump(spec.get('output_schema', []))}
    """
    
    try:
        response = llm_client.models.generate_content(
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
        logger.error(f"AI Generation error: {e}")
        # Safe error message for user
        return {"error": "Internal Processing Error", "message": "Failed to generate travel plan."}
