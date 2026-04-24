from pydantic import BaseModel, field_validator
from typing import List

class IncidentStatus(BaseModel):
    status: str

    @field_validator("status")
    def validate_status(cls, value):
        allowed = {"in progress", "open", "closed", "resolved"}
        value_lower = value.lower()

        if value_lower not in allowed:
            raise ValueError(f"Status must be one of {allowed}")

        return value_lower

class IncidentSummary(BaseModel):
    number: str
    short_description: str
    assigned_to: str
    state: str

class IncidentListResponse(BaseModel):
    count: int
    incidents: List[IncidentSummary]