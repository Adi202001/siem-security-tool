from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.log import SecurityLog
from app.models.alert import Alert
from app.schemas.log import SecurityLog as SecurityLogSchema, SecurityLogCreate, LogBatch
from app.schemas.alert import AlertCreate
from app.services.log_parser import log_parser
from app.services.rule_engine import rule_engine
from app.ml.anomaly_detector import anomaly_detector

router = APIRouter()


@router.post("/ingest", response_model=SecurityLogSchema)
async def ingest_log(
    log_data: SecurityLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ingest a single security log"""
    # Parse the log if raw_log is provided
    if log_data.parsed_data is None:
        parsed = log_parser.parse(log_data.raw_log)
        # Update log_data with parsed information
        for key, value in parsed.items():
            if hasattr(log_data, key) and value is not None:
                setattr(log_data, key, value)

    # Create log entry
    log = SecurityLog(**log_data.model_dump())

    # Check for anomalies using ML
    try:
        is_anomaly, anomaly_score = anomaly_detector.predict_single(log_data.model_dump())
        log.is_anomaly = is_anomaly
        log.anomaly_score = anomaly_score
    except Exception as e:
        print(f"Anomaly detection error: {e}")
        log.is_anomaly = False
        log.anomaly_score = None

    db.add(log)
    await db.commit()
    await db.refresh(log)

    # Evaluate against detection rules
    await rule_engine.load_rules(db)
    alerts = await rule_engine.evaluate_log(log_data.model_dump(), db)

    # Create anomaly alert if detected
    if log.is_anomaly and log.anomaly_score and log.anomaly_score > 0.7:
        alerts.append(AlertCreate(
            alert_type="anomaly",
            severity="high" if log.anomaly_score > 0.85 else "medium",
            title="Anomaly detected",
            description=f"Machine learning detected anomalous behavior (score: {log.anomaly_score:.2f})",
            source=log.source_ip,
            destination=log.destination_ip,
            log_id=log.id
        ))

    # Create alert records
    for alert_data in alerts:
        alert = Alert(**alert_data.model_dump(), log_id=log.id)
        db.add(alert)

    await db.commit()

    return log


@router.post("/ingest/batch", response_model=List[SecurityLogSchema])
async def ingest_batch(
    batch: LogBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ingest multiple logs in batch"""
    created_logs = []

    for log_data in batch.logs:
        # Parse the log
        if log_data.parsed_data is None:
            parsed = log_parser.parse(log_data.raw_log)
            for key, value in parsed.items():
                if hasattr(log_data, key) and value is not None:
                    setattr(log_data, key, value)

        log = SecurityLog(**log_data.model_dump())
        db.add(log)
        created_logs.append(log)

    await db.commit()

    # Refresh all logs
    for log in created_logs:
        await db.refresh(log)

    # Run anomaly detection and rule evaluation in background
    # (In production, use Celery for this)

    return created_logs


@router.get("/", response_model=List[SecurityLogSchema])
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    source_ip: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    anomalies_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get security logs with filtering"""
    query = select(SecurityLog)

    # Apply filters
    filters = []
    if severity:
        filters.append(SecurityLog.severity == severity)
    if event_type:
        filters.append(SecurityLog.event_type == event_type)
    if source_ip:
        filters.append(SecurityLog.source_ip == source_ip)
    if start_time:
        filters.append(SecurityLog.timestamp >= start_time)
    if end_time:
        filters.append(SecurityLog.timestamp <= end_time)
    if anomalies_only:
        filters.append(SecurityLog.is_anomaly == True)

    if filters:
        query = query.where(and_(*filters))

    # Order by timestamp descending
    query = query.order_by(desc(SecurityLog.timestamp)).offset(skip).limit(limit)

    result = await db.execute(query)
    logs = list(result.scalars().all())

    return logs


@router.get("/stats")
async def get_log_stats(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get log statistics for dashboard"""
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Total logs
    total_result = await db.execute(
        select(func.count(SecurityLog.id)).where(SecurityLog.timestamp >= start_time)
    )
    total_logs = total_result.scalar()

    # Logs by severity
    severity_result = await db.execute(
        select(SecurityLog.severity, func.count(SecurityLog.id))
        .where(SecurityLog.timestamp >= start_time)
        .group_by(SecurityLog.severity)
    )
    logs_by_severity = {row[0]: row[1] for row in severity_result.all()}

    # Anomalies
    anomaly_result = await db.execute(
        select(func.count(SecurityLog.id))
        .where(and_(
            SecurityLog.timestamp >= start_time,
            SecurityLog.is_anomaly == True
        ))
    )
    anomalies = anomaly_result.scalar()

    # Top source IPs
    top_ips_result = await db.execute(
        select(SecurityLog.source_ip, func.count(SecurityLog.id).label('count'))
        .where(SecurityLog.timestamp >= start_time)
        .group_by(SecurityLog.source_ip)
        .order_by(desc('count'))
        .limit(10)
    )
    top_source_ips = [{"ip": row[0], "count": row[1]} for row in top_ips_result.all()]

    return {
        "total_logs": total_logs,
        "logs_by_severity": logs_by_severity,
        "anomalies": anomalies,
        "top_source_ips": top_source_ips,
        "time_range_hours": hours
    }


@router.get("/{log_id}", response_model=SecurityLogSchema)
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific log by ID"""
    result = await db.execute(select(SecurityLog).where(SecurityLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return log
