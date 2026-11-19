from datetime import timedelta

from assistant.schema import SimulationRequest
from assistant.validator import DEFAULT_DURATION_HOURS, MAX_PARTICLES

TIME_FORMAT = "%Y-%m-%d %H:%M"

#lars confirmation on diffusion and convection values
DIFFUSION_ON = {
    "turb_dx_pbl": 50.0, "turb_dx_trop": 50.0, "turb_dx_strat": 0.0,
    "turb_dz_pbl": 0.0,  "turb_dz_trop": 0.0,  "turb_dz_strat": 0.1,
}
DIFFUSION_OFF = {name: 0.0 for name in DIFFUSION_ON}

CONVECTION_OFF = {"conv_cape": -999.0, "conv_cin": -999.0}
CONVECTION_ON = {"conv_cape": 0.0, "conv_cin": 0.0}

def _fmt(value: float) -> str:
    """Format a number for a form field without losing precision, e.g. 4 -> '4.0'."""
    return str(float(value))

def map_to_form(req: SimulationRequest) -> dict[str, str]:
    fields: dict[str, str] = {}

    #time fields
    duration = req.duration_hours if req.duration_hours is not None else DEFAULT_DURATION_HOURS
    sign = -1 if req.direction == "backward" else 1
    stop_time = req.start_time + sign * timedelta(hours=duration)
    fields["start_time"] = req.start_time.strftime(TIME_FORMAT)
    fields["stop_time"] = stop_time.strftime(TIME_FORMAT)

    #location fields
    fields["mlat"] = _fmt(req.latitude)
    fields["mlon"] = _fmt(req.longitude)
    for name in ["ulat", "ulon", "slat", "slon"]:
        fields[name] = "0.0"

    #altitude fields
    fields["mz"] = _fmt((req.altitude_max_km + req.altitude_min_km) / 2)
    fields["uz"] = _fmt(req.altitude_max_km - req.altitude_min_km)
    fields["sz"] = "0.0"

    #particle fields
    fields["rep"] = str(req.num_particles if req.num_particles is not None else MAX_PARTICLES)

    #diffusion fields
    if req.diffusion is True:
        for name, value in DIFFUSION_ON.items():
            fields[name] = _fmt(value)
    elif req.diffusion is False:
        for name, value in DIFFUSION_OFF.items():
            fields[name] = _fmt(value)

    #convection fields
    if req.convection is True:
        for name, value in CONVECTION_ON.items():
            fields[name] = _fmt(value)
    elif req.convection is False:
        for name, value in CONVECTION_OFF.items():
            fields[name] = _fmt(value)

    return fields