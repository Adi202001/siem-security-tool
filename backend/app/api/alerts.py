from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import Alert as AlertSchema, AlertCreate, AlertUpdate

router = APIRouter()


@router.post("/", response_model=AlertSchema)
async def create_alert(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new alert manually"""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


@router.get("/", response_model=List[AlertSchema])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    unacknowledged_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alerts with filtering"""
    query = select(Alert)

    # Apply filters
    filters = []
    if severity:
        filters.append(Alert.severity == severity)
    if status:
        filters.append(Alert.status == status)
    if alert_type:
        filters.append(Alert.alert_type == alert_type)
    if start_time:
        filters.append(Alert.timestamp >= start_time)
    if end_time:
        filters.append(Alert.timestamp <= end_time)
    if unacknowledged_only:
        filters.append(Alert.is_acknowledged == False)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit)

    result = await db.execute(query)
    alerts = list(result.scalars().all())

    return alerts


@router.get("/stats")
async def get_alert_stats(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert statistics"""
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Total alerts
    total_result = await db.execute(
        select(func.count(Alert.id)).where(Alert.timestamp >= start_time)
    )
    total_alerts = total_result.scalar()

    # Alerts by severity
    severity_result = await db.execute(
        select(Alert.severity, func.count(Alert.id))
        .where(Alert.timestamp >= start_time)
        .group_by(Alert.severity)
    )
    alerts_by_severity = {row[0]: row[1] for row in severity_result.all()}

    # Alerts by status
    status_result = await db.execute(
        select(Alert.status, func.count(Alert.id))
        .where(Alert.timestamp >= start_time)
        .group_by(Alert.status)
    )
    alerts_by_status = {row[0]: row[1] for row in status_result.all()}

    # Unacknowledged alerts
    unack_result = await db.execute(
        select(func.count(Alert.id))
        .where(and_(
            Alert.timestamp >= start_time,
            Alert.is_acknowledged == False
        ))
    )
    unacknowledged = unack_result.scalar()

    return {
        "total_alerts": total_alerts,
        "alerts_by_severity": alerts_by_severity,
        "alerts_by_status": alerts_by_status,
        "unacknowledged": unacknowledged,
        "time_range_hours": hours
    }


@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.patch("/{alert_id}", response_model=AlertSchema)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update fields
    update_data = alert_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    # Set resolved_at if status changed to resolved
    if alert_update.status == "resolved" and not alert.resolved_at:
        alert.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(alert)

    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertSchema)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge an alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = current_user.username

    await db.commit()
    await db.refresh(alert)

    return alert


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()

    return {"message": "Alert deleted successfully"}
