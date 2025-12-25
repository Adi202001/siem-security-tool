from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SecurityLogBase(BaseModel):
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    event_type: str
    severity: str
    message: str
    hostname: Optional[str] = None
    user: Optional[str] = None
    action: Optional[str] = None


class SecurityLogCreate(SecurityLogBase):
    raw_log: str
    parsed_data: Optional[Dict[str, Any]] = None


class SecurityLogUpdate(BaseModel):
    severity: Optional[str] = None
    is_anomaly: Optional[bool] = None
    anomaly_score: Optional[float] = None


class SecurityLogInDB(SecurityLogBase):
    id: int
    timestamp: datetime
    raw_log: str
    parsed_data: Optional[Dict[str, Any]] = None
    is_anomaly: bool
    anomaly_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SecurityLog(SecurityLogInDB):
    pass


class LogBatch(BaseModel):
    logs: list[SecurityLogCreate]
