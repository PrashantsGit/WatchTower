
from datetime import datetime

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
)


class BrowserPushSubscriptionKeysRequest(BaseModel):
    p256dh: str = Field(min_length=1)
    auth: str = Field(min_length=1)


class RegisterBrowserPushSubscriptionRequest(BaseModel):
    endpoint: str = Field(min_length=1)
    keys: BrowserPushSubscriptionKeysRequest
    expiration_time: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "expirationTime",
            "expiration_time",
        ),
    )


class BrowserPushSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    endpoint: str
    expiration_time: datetime | None
    created_at: datetime
