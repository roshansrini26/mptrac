"""Check a SimulationRequest against the Web Runner's rules.

The validator only reports problems; it never changes the request.
Limits mirror the checks in app.py (see the /run route).
"""
from dataclasses import dataclass, field

from assistant.schema import SimulationRequest

MAX_PARTICLES = 10_000
MAX_DURATION_HOURS = 30 * 24       # 30 days
DEFAULT_DURATION_HOURS = 96        # 4 days

REQUIRED_FIELDS = [
    "start_time",       
    "latitude",         
    "longitude",        
    "altitude_min_km",  
    "altitude_max_km",  
]                       


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.missing


def validate(req: SimulationRequest) -> ValidationResult:
    result = ValidationResult()

    for name in REQUIRED_FIELDS:
        if getattr(req, name) is None:
            result.missing.append(name)

    if req.num_particles is not None and not (1 <= req.num_particles <= MAX_PARTICLES):
        result.errors.append(                                   
            f"Number of particles must be between 1 and {MAX_PARTICLES:,} "
            f"(you asked for {req.num_particles:,}).")

    # latitude between -90 and 90
    if req.latitude is not None and not (-90 <= req.latitude <= 90):
        result.errors.append(
            f"Latitude must be between -90° and 90° (got {req.latitude}°).")

    # longitude between -180 and 180
    if req.longitude is not None and not (-180 <= req.longitude <= 180):
        result.errors.append(
            f"Longitude must be between -180° and 180° (got {req.longitude}°).")

    # duration_hours > 0 and <= MAX_DURATION_HOURS
    if req.duration_hours is not None and not (0 < req.duration_hours <= MAX_DURATION_HOURS):
        result.errors.append(                                   # FIX: 0 is not allowed
            f"Duration must be longer than 0 and at most {MAX_DURATION_HOURS} hours "
            f"(30 days); you asked for {req.duration_hours} hours.")

    # altitudes between -100 and 100 km
    for name, label in [("altitude_min_km", "Lower"),          
                        ("altitude_max_km", "Upper")]:
        value = getattr(req, name)
        if value is not None and not (-100 <= value <= 100):
            result.errors.append(
                f"{label} release height must be between -100 and 100 km (got {value} km).")

    # altitude_min_km <= altitude_max_km (only if both are given)
    if (req.altitude_min_km is not None and req.altitude_max_km is not None
            and req.altitude_min_km > req.altitude_max_km):
        result.errors.append(
            f"The lower release height ({req.altitude_min_km} km) is above "
            f"the upper one ({req.altitude_max_km} km).")

    # num_particles not given -> default
    if req.num_particles is None:
        result.warnings.append(f"Number of particles not given, using {MAX_PARTICLES:,}.")

    #duration not given -> default
    if req.duration_hours is None:
        result.warnings.append(
            f"Duration not given, using {DEFAULT_DURATION_HOURS} hours (4 days).")

    # direction not given -> forward
    if req.direction is None:
        result.warnings.append("Direction not given, using forward.")

    return result