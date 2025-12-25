from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from datetime import datetime
from app.db.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String, index=True)  # low, medium, high, critical
    status = Column(String, default="open")  # open, investigating, contained, resolved
    category = Column(String, index=True)  # malware, intrusion, data_breach, etc.
    affected_systems = Column(JSON)  # List of affected IPs, hostnames
    indicators = Column(JSON)  # IOCs (Indicators of Compromise)
    assigned_to = Column(String, nullable=True)
    priority = Column(Integer, default=3)  # 1-5, 1 being highest
    created_by = Column(String)
    resolved_by = Column(String, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    containment_actions = Column(JSON, nullable=True)
    related_alerts = Column(JSON, nullable=True)  # Array of alert IDs
    timeline = Column(JSON, nullable=True)  # Timeline of events
    started_at = Column(DateTime, default=datetime.utcnow)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
