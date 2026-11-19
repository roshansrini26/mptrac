"""Unit tests for assistant/mapper.py (no LLM calls)."""
from datetime import datetime

from assistant.mapper import DIFFUSION_ON, map_to_form
from assistant.schema import SimulationRequest


def valid_request(**overrides) -> SimulationRequest:
    data = dict(
        start_time=datetime(2010, 4, 15, 12, 0),
        duration_hours=96,
        direction="forward",
        latitude=63.633,
        longitude=-19.633,
        altitude_min_km=0,
        altitude_max_km=8,
        num_particles=5_000,
    )
    data.update(overrides)
    return SimulationRequest(**data)


# --- Time ---

def test_forward_stop_time():
    fields = map_to_form(valid_request())
    assert fields["start_time"] == "2010-04-15 12:00"
    assert fields["stop_time"] == "2010-04-19 12:00"


def test_backward_stop_time():
    fields = map_to_form(valid_request(direction="backward"))
    assert fields["stop_time"] == "2010-04-11 12:00"


def test_stop_time_across_year_boundary():
    fields = map_to_form(valid_request(start_time=datetime(2025, 12, 31, 12, 0),
                                       duration_hours=48))
    assert fields["stop_time"] == "2026-01-02 12:00"


def test_missing_duration_uses_default_96_hours():
    fields = map_to_form(valid_request(duration_hours=None))
    assert fields["stop_time"] == "2010-04-19 12:00"


def test_missing_direction_means_forward():
    fields = map_to_form(valid_request(direction=None))
    assert fields["stop_time"] == "2010-04-19 12:00"


# --- Location ---

def test_coordinates_keep_full_precision():
    fields = map_to_form(valid_request())
    assert fields["mlat"] == "63.633"
    assert fields["mlon"] == "-19.633"


def test_point_release_has_no_horizontal_spread():
    fields = map_to_form(valid_request())
    for name in ["ulat", "ulon", "slat", "slon"]:
        assert fields[name] == "0.0"


# --- Altitude ---

def test_altitude_range_to_centre_and_width():
    fields = map_to_form(valid_request(altitude_min_km=10, altitude_max_km=12))
    assert fields["mz"] == "11.0"
    assert fields["uz"] == "2.0"
    assert fields["sz"] == "0.0"


def test_single_height_has_zero_width():
    fields = map_to_form(valid_request(altitude_min_km=11, altitude_max_km=11))
    assert fields["mz"] == "11.0"
    assert fields["uz"] == "0.0"


# --- Particles ---

def test_particles_are_written_as_integer():
    fields = map_to_form(valid_request(num_particles=5_000))
    assert fields["rep"] == "5000"     # app.py uses int(), so no ".0"


def test_missing_particles_uses_max():
    fields = map_to_form(valid_request(num_particles=None))
    assert fields["rep"] == "10000"


# --- Physics ---

def test_diffusion_off_sets_all_turb_fields_to_zero():
    fields = map_to_form(valid_request(diffusion=False))
    for name in DIFFUSION_ON:
        assert fields[name] == "0.0"


def test_diffusion_on_uses_form_defaults():
    fields = map_to_form(valid_request(diffusion=True))
    assert fields["turb_dx_trop"] == "50.0"
    assert fields["turb_dz_strat"] == "0.1"


def test_diffusion_none_leaves_turb_fields_untouched():
    fields = map_to_form(valid_request(diffusion=None))
    assert not any(name.startswith("turb_") for name in fields)


def test_convection_off_sets_minus_999():
    fields = map_to_form(valid_request(convection=False))
    assert fields["conv_cape"] == "-999.0"
    assert fields["conv_cin"] == "-999.0"


def test_convection_none_leaves_conv_fields_untouched():
    fields = map_to_form(valid_request(convection=None))
    assert "conv_cape" not in fields