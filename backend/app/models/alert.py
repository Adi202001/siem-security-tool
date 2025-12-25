from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_type = Column(String, index=True)  # rule-based, anomaly, manual
    severity = Column(String, index=True)  # low, medium, high, critical
    title = Column(String, nullable=False)
    description = Column(Text)
    source = Column(String)  # IP, hostname, or system that triggered alert
    destination = Column(String)
    rule_id = Column(Integer, ForeignKey("detection_rules.id"), nullable=True)
    log_id = Column(Integer, ForeignKey("security_logs.id"), nullable=True)
    status = Column(String, default="open")  # open, investigating, resolved, false_positive
    assigned_to = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
