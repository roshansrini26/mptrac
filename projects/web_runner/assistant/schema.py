from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Simulation parameters extracted by the LLM from the user's text.

    Every field is optional: None means the user did not mention it.
    """

    start_time: datetime | None = Field(
        None, description="Release start time in UTC")

    duration_hours: float | None = Field(
        None, description="Length of the simulation in hours, always positive. "
                          "Use 'direction' for backward runs. Example: '5 days' -> 120")

    direction: Literal["forward", "backward"] | None = Field(
        None, description="Time direction of the trajectory calculation")


    latitude: float | None = Field(
        None, description="Release latitude in degrees, north positive")

    longitude: float | None = Field(
        None, description="Release longitude in degrees, east positive")

    altitude_min_km: float | None = Field(
        None, description="Lower bound of the release height in km. "
                          "If only one height is given, set min and max to the same value")

    altitude_max_km: float | None = Field(
        None, description="Upper bound of the release height in km. "
                          "If only one height is given, set min and max to the same value")

    num_particles: int | None = Field(
        None, description="Number of air parcels (particles, trajectories) to release")

    diffusion: bool | None = Field(
        None, description="true if the user asks for diffusion, false if they "
                          "explicitly turn it off, null if not mentioned")

    convection: bool | None = Field(
        None, description="true if the user asks for convection, false if they "
                          "explicitly turn it off, null if not mentioned")