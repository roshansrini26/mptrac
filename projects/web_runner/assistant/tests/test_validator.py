"""Unit tests for assistant/validator.py (no LLM calls)."""
from datetime import datetime

import pytest

from assistant.schema import SimulationRequest
from assistant.validator import REQUIRED_FIELDS, validate


def valid_request(**overrides) -> SimulationRequest:
    """A complete, valid request. Tests change only the field they care about."""
    data = dict(
        start_time=datetime(2010, 4, 15, 12, 0),
        duration_hours=96,
        direction="forward",
        latitude=63.6,
        longitude=-19.6,
        altitude_min_km=0,
        altitude_max_km=8,
        num_particles=5_000,
        diffusion=True,
        convection=False,
    )
    data.update(overrides)
    return SimulationRequest(**data)


# --- Particles ---

def test_too_many_particles_is_an_error():
    result = validate(SimulationRequest(num_particles=100_000))
    assert any("particles" in e for e in result.errors)


def test_valid_particle_count_has_no_error():
    result = validate(SimulationRequest(num_particles=5_000))
    assert result.errors == []


def test_missing_particles_gives_warning():
    result = validate(SimulationRequest())
    assert any("particles" in w for w in result.warnings)


def test_given_particles_gives_no_particle_warning():
    result = validate(valid_request(num_particles=5_000))
    assert not any("particles" in w for w in result.warnings)


# --- Location ---

@pytest.mark.parametrize("lat", [-91, 95, 180])
def test_invalid_latitude_is_an_error(lat):
    result = validate(valid_request(latitude=lat))
    assert any("Latitude" in e for e in result.errors)


@pytest.mark.parametrize("lon", [-181, 200])
def test_invalid_longitude_is_an_error(lon):
    result = validate(valid_request(longitude=lon))
    assert any("Longitude" in e for e in result.errors)


# --- Altitude ---

def test_min_above_max_altitude_is_an_error():
    result = validate(valid_request(altitude_min_km=12, altitude_max_km=10))
    assert any("lower release height" in e.lower() for e in result.errors)


def test_max_altitude_out_of_range_is_an_error():
    result = validate(valid_request(altitude_max_km=500))
    assert any("Upper release height" in e for e in result.errors)


def test_single_height_is_valid():
    result = validate(valid_request(altitude_min_km=11, altitude_max_km=11))
    assert result.errors == []


# --- Duration ---

@pytest.mark.parametrize("hours", [0, -5, 721])
def test_invalid_duration_is_an_error(hours):
    result = validate(valid_request(duration_hours=hours))
    assert any("Duration" in e for e in result.errors)


def test_missing_duration_gives_warning():
    result = validate(valid_request(duration_hours=None))
    assert any("Duration" in w for w in result.warnings)


# --- Required fields and overall result ---

def test_empty_request_lists_all_required_fields_as_missing():
    result = validate(SimulationRequest())
    assert set(result.missing) == set(REQUIRED_FIELDS)
    assert result.ok is False


def test_complete_valid_request_is_ok():
    result = validate(valid_request())
    assert result.errors == []
    assert result.missing == []
    assert result.ok is True