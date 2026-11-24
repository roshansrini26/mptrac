from assistant.schema import SimulationRequest

def merge(previous: SimulationRequest | None, new: SimulationRequest) -> SimulationRequest:
    if previous is None:
        return new
    updates = new.model_dump(exclude_none=True)
    return previous.model_copy(update=updates)
