from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import List, Optional
from datetime import datetime
import secrets

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.incident import Incident
from app.schemas.incident import Incident as IncidentSchema, IncidentCreate, IncidentUpdate

router = APIRouter()


def generate_incident_id() -> str:
    """Generate a unique incident ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"INC-{timestamp}-{random_part}"


@router.post("/", response_model=IncidentSchema)
async def create_incident(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new security incident"""
    incident_data = incident.model_dump()
    incident_data["incident_id"] = generate_incident_id()

    db_incident = Incident(**incident_data)
    db.add(db_incident)
    await db.commit()
    await db.refresh(db_incident)

    return db_incident


@router.get("/", response_model=List[IncidentSchema])
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get security incidents"""
    query = select(Incident)

    # Apply filters
    filters = []
    if status:
        filters.append(Incident.status == status)
    if severity:
        filters.append(Incident.severity == severity)
    if category:
        filters.append(Incident.category == category)
    if assigned_to:
        filters.append(Incident.assigned_to == assigned_to)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(desc(Incident.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    incidents = list(result.scalars().all())

    return incidents


@router.get("/{incident_id}", response_model=IncidentSchema)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific incident by incident_id"""
    result = await db.execute(
        select(Incident).where(Incident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.patch("/{incident_id}", response_model=IncidentSchema)
async def update_incident(
    incident_id: str,
    incident_update: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an incident"""
    result = await db.execute(
        select(Incident).where(Incident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Update fields
    update_data = incident_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    # Set resolved_at if status changed to resolved
    if incident_update.status == "resolved" and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()
        incident.resolved_by = current_user.username

    # Add timeline entry
    if not incident.timeline:
        incident.timeline = []

    timeline_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": "updated",
        "user": current_user.username,
        "changes": update_data
    }
    incident.timeline.append(timeline_entry)

    await db.commit()
    await db.refresh(incident)

    return incident


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an incident"""
    result = await db.execute(
        select(Incident).where(Incident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    await db.delete(incident)
    await db.commit()

    return {"message": "Incident deleted successfully"}
