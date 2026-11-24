"""Unit tests for assistant/merge.py (no LLM calls)."""
from datetime import datetime

from assistant.merge import merge
from assistant.schema import SimulationRequest


def test_no_previous_returns_new_unchanged():
    new = SimulationRequest(latitude=50, longitude=7)
    assert merge(None, new) == new


def test_new_values_are_added_to_previous():
    previous = SimulationRequest(latitude=50, longitude=7)
    new = SimulationRequest(start_time=datetime(2025, 10, 15, 12, 0))
    result = merge(previous, new)
    assert result.latitude == 50
    assert result.longitude == 7
    assert result.start_time == datetime(2025, 10, 15, 12, 0)


def test_new_value_overwrites_previous():
    previous = SimulationRequest(altitude_max_km=12)
    new = SimulationRequest(altitude_max_km=8)
    result = merge(previous, new)
    assert result.altitude_max_km == 8


def test_explicit_false_overwrites_true():
    previous = SimulationRequest(diffusion=True)
    new = SimulationRequest(diffusion=False)
    result = merge(previous, new)
    assert result.diffusion is False


def test_none_keeps_previous_value():
    previous = SimulationRequest(diffusion=True)
    new = SimulationRequest()
    result = merge(previous, new)
    assert result.diffusion is True