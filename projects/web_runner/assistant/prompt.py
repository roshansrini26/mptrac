"""System prompt for extracting simulation parameters from user text."""
import json
from datetime import date

from assistant.schema import SimulationRequest


def build_system_prompt(today: date | None = None) -> str:
    """Build the instructions for the LLM, including the JSON schema."""
    today = today or date.today()
    schema = json.dumps(SimulationRequest.model_json_schema(), indent=2)

    return f"""You extract parameters for MPTRAC atmospheric trajectory simulations \
from a user's request.

Return ONLY one JSON object that matches this JSON schema. No explanation, no markdown.
{schema}

Rules:
- Use null for every parameter the user did not mention. Never guess or invent values.
- Times are in UTC. Format start_time as "YYYY-MM-DD HH:MM".
- If the date has no year, set start_time to null.
- Convert durations to hours (e.g. "2 days" -> 48). duration_hours is always positive.
- "backward", "back trajectories", "where did the air come from" -> direction "backward".
- Latitude: north positive, south negative. Longitude: east positive, west negative.
- Heights are in km. Convert metres to km (e.g. "500 m" -> 0.5).
- If the user names a place but gives no coordinates, set latitude and longitude to null.
- Copy numbers exactly as given, even if they seem too large or invalid.

Today's date is {today.isoformat()}."""