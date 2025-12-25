from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from datetime import datetime
from app.db.database import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String, index=True)
    destination_ip = Column(String, index=True)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String)
    event_type = Column(String, index=True)  # login, firewall, intrusion, etc.
    severity = Column(String, index=True)  # low, medium, high, critical
    message = Column(Text)
    raw_log = Column(Text)
    parsed_data = Column(JSON)  # Additional parsed fields
    hostname = Column(String, index=True)
    user = Column(String, index=True)
    action = Column(String)  # allow, deny, alert
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
