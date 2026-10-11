
from pydantic import BaseModel, ConfigDict, Field


class UserProfileResponse(BaseModel):
    """Public profile fields returned by the User API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class UserProfileUpdateRequest(BaseModel):
    """Fields that can be updated through the User API."""

    full_name: str = Field(min_length=1, max_length=100)
