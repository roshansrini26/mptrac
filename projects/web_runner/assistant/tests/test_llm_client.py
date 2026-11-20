"""Unit tests for clean_response in assistant/llm_client.py (no LLM calls)."""
import pytest

from assistant.llm_client import clean_response


def test_plain_json_is_unchanged():
    assert clean_response('{"latitude": 50}') == '{"latitude": 50}'


def test_markdown_fences_are_removed():
    raw = '```json\n{"latitude": 50}\n```'
    assert clean_response(raw) == '{"latitude": 50}'


def test_think_block_is_removed():
    # The reasoning block contains braces too, so it MUST be removed first,
    # otherwise the regex would grab from the "{" inside <think>.
    raw = '<think>The user wants {lat: 50}, so...</think>\n{"latitude": 50}'
    assert clean_response(raw) == '{"latitude": 50}'


def test_text_around_json_is_removed():
    raw = 'Here is the result: {"latitude": 50} Let me know if you need more.'
    assert clean_response(raw) == '{"latitude": 50}'


def test_answer_without_json_raises_value_error():
    with pytest.raises(ValueError):
        clean_response("Sorry, I can't help with that.")