from pydantic import BaseModel, ConfigDict


class NotificationPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    email_enabled: bool
    browser_push_enabled: bool
    notify_on_price_change: bool
    notify_on_stock_change: bool


class UpdateNotificationPreferenceRequest(BaseModel):
    email_enabled: bool = True
    browser_push_enabled: bool = True
    notify_on_price_change: bool = True
    notify_on_stock_change: bool = True