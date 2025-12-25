from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class DetectionRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str
    severity: str
    conditions: Dict[str, Any]


class DetectionRuleCreate(DetectionRuleBase):
    created_by: str
    is_active: bool = True


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DetectionRuleInDB(DetectionRuleBase):
    id: int
    is_active: bool
    created_by: str
    last_triggered: Optional[datetime] = None
    trigger_count: int
    false_positive_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DetectionRule(DetectionRuleInDB):
    pass
