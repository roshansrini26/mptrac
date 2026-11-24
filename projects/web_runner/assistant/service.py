"""Handle one chat turn: text -> extract -> merge -> validate -> form fields."""
from pydantic import ValidationError

from assistant.llm_client import extract
from assistant.mapper import map_to_form
from assistant.merge import merge
from assistant.schema import SimulationRequest
from assistant.validator import ValidationResult, validate

# How to ask for each required field in the chat.
FIELD_QUESTIONS = {
    "start_time": "the start date and time (UTC)",
    "latitude": "the release latitude",
    "longitude": "the release longitude",
    "altitude_min_km": "the release height or height range (km)",
    "altitude_max_km": "the release height or height range (km)",
}


def build_reply(result: ValidationResult) -> str:
    """Turn the validation result into the assistant's chat message."""
    parts = list(result.errors)
    if result.missing:
        # dict.fromkeys removes duplicates but keeps the order
        asks = list(dict.fromkeys(FIELD_QUESTIONS[name] for name in result.missing))
        parts.append("I still need " + ", ".join(asks) + ".")
    if not parts:
        return "All set. I filled in the form. Please review the highlighted fields and press Run."
    return " ".join(parts)


def handle_message(message: str, previous: dict | None) -> dict:
    """Process one user message. `previous` is the request so far, sent back by the browser."""
    prev = None
    if previous:
        try:
            prev = SimulationRequest.model_validate(previous)
        except ValidationError:
            prev = None          # broken state from the browser: start fresh

    new = extract(message)       # LLM errors are handled by the Flask route
    req = merge(prev, new)
    result = validate(req)

    return {
        "reply": build_reply(result),
        "request": req.model_dump(mode="json"),   # the browser keeps this for the next turn
        "fields": map_to_form(req) if result.ok else {},
        "warnings": result.warnings,
    }