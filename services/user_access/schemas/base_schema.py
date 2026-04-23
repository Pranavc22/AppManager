from pydantic import BaseModel, Field, validator


class AccessRequestFilter(BaseModel):
    status: str = Field(..., description="Status of request: PENDING, APPROVED, REJECTED")

    @validator("status")
    def validate_status(cls, value):
        allowed = {"PENDING", "APPROVED", "REJECTED"}
        value = value.upper()

        if value not in allowed:
            raise ValueError(f"Status must be one of {allowed}")

        return value