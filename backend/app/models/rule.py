from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from datetime import datetime
from app.db.database import Base


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    rule_type = Column(String)  # signature, behavioral, correlation
    severity = Column(String, index=True)  # low, medium, high, critical
    conditions = Column(JSON)  # Rule conditions as JSON
    is_active = Column(Boolean, default=True)
    created_by = Column(String)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
