from pydantic import BaseModel, Field, field_validator
from typing import List

class AccessRequestFilter(BaseModel):
    status: str = Field(..., description="Status of request: PENDING, APPROVED, REJECTED")

    @field_validator("status")
    def validate_status(cls, value):
        allowed = {"PENDING", "APPROVED", "REJECTED"}
        value = value.upper()

        if value not in allowed:
            raise ValueError(f"Status must be one of {allowed}")

        return value

class AccessRequestItem(BaseModel):
    request_id: str
    user_id: str
    user_name: str
    resource_id: str
    resource_name: str
    requested_action: str
    status: str
    created_at: str

class AccessRequestListResponse(BaseModel):
    count: int
    data: List[AccessRequestItem]