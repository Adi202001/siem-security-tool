from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AlertBase(BaseModel):
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None


class AlertCreate(AlertBase):
    rule_id: Optional[int] = None
    log_id: Optional[int] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    is_acknowledged: Optional[bool] = None


class AlertInDB(AlertBase):
    id: int
    timestamp: datetime
    rule_id: Optional[int] = None
    log_id: Optional[int] = None
    status: str
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Alert(AlertInDB):
    pass
