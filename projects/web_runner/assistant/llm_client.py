"""Call the Blablador LLM and turn its answer into a SimulationRequest."""
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from assistant.prompt import build_system_prompt
from assistant.schema import SimulationRequest

load_dotenv()

BASE_URL = "https://api.blablador.fz-juelich.de/v1/"
MODEL = os.getenv("BLABLADOR_MODEL", "alias-large")
MAX_ATTEMPTS = 2


class ExtractionError(Exception):
    """The LLM did not return a usable answer."""


def clean_response(text: str) -> str:
    """Return only the JSON object from the model's answer.

    Removes <think>...</think> reasoning blocks and any text or
    markdown fences around the JSON.
    """
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match is None:
        raise ValueError("No JSON object found in the model's answer")
    return match.group(0)


def _client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["BLABLADOR_API_KEY"],
        base_url=BASE_URL,
        timeout=60,
    )


def extract(user_text: str) -> SimulationRequest:
    """Send the user's text to the LLM and return the parsed request."""
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": user_text},
    ]
    client = _client()
    last_error = None

    for _ in range(MAX_ATTEMPTS):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0)
        raw = response.choices[0].message.content or ""
        try:
            data = json.loads(clean_response(raw))
            return SimulationRequest.model_validate(data)
        except (ValueError, ValidationError) as e:
            last_error = e
            # Show the model its mistake and ask again.
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content":
                f"Your answer was not valid: {e}. Reply with only the corrected JSON object."})

    raise ExtractionError(f"No valid answer after {MAX_ATTEMPTS} attempts: {last_error}")


if __name__ == "__main__":
    # Quick manual test of the whole pipeline from the terminal.
    import sys
    from assistant.mapper import map_to_form
    from assistant.validator import validate

    text = " ".join(sys.argv[1:]) or (
        "Run 5000 particles from 50N 7E between 10 and 12 km for 5 days, "
        "starting 15 October 2025 at 12 UTC, with diffusion.")

    req = extract(text)
    print("EXTRACTED:\n", req.model_dump_json(indent=2))

    result = validate(req)
    print("\nERRORS:  ", result.errors)
    print("MISSING: ", result.missing)
    print("WARNINGS:", result.warnings)
    if result.ok:
        print("\nFORM FIELDS:\n", json.dumps(map_to_form(req), indent=2))