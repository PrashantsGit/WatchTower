from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateRuleRequest(BaseModel):
    rule_type: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    target_value: str = Field(min_length=1)


class UpdateRuleRequest(BaseModel):
    rule_type: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    target_value: str = Field(min_length=1)
    is_enabled: bool


class RuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    rule_type: str
    operator: str
    target_value: str
    is_enabled: bool
    created_at: datetime
    updated_at: datetime