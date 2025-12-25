from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str
    category: str
    affected_systems: Optional[List[str]] = None
    indicators: Optional[Dict[str, Any]] = None
    priority: int = 3


class IncidentCreate(IncidentBase):
    created_by: str
    related_alerts: Optional[List[int]] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[int] = None
    containment_actions: Optional[Dict[str, Any]] = None
    resolution_notes: Optional[str] = None


class IncidentInDB(IncidentBase):
    id: int
    incident_id: str
    status: str
    assigned_to: Optional[str] = None
    created_by: str
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    containment_actions: Optional[Dict[str, Any]] = None
    related_alerts: Optional[List[int]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    started_at: datetime
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Incident(IncidentInDB):
    pass
