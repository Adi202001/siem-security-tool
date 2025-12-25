from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.rule import DetectionRule
from app.schemas.rule import DetectionRule as RuleSchema, DetectionRuleCreate, DetectionRuleUpdate
from app.services.rule_engine import rule_engine

router = APIRouter()


@router.post("/", response_model=RuleSchema)
async def create_rule(
    rule: DetectionRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new detection rule"""
    # Check if rule with same name exists
    result = await db.execute(
        select(DetectionRule).where(DetectionRule.name == rule.name)
    )
    existing_rule = result.scalar_one_or_none()

    if existing_rule:
        raise HTTPException(status_code=400, detail="Rule with this name already exists")

    db_rule = DetectionRule(**rule.model_dump())
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)

    # Reload rules in engine
    await rule_engine.load_rules(db)

    return db_rule


@router.get("/", response_model=List[RuleSchema])
async def get_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = False,
    rule_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detection rules"""
    query = select(DetectionRule)

    if active_only:
        query = query.where(DetectionRule.is_active == True)
    if rule_type:
        query = query.where(DetectionRule.rule_type == rule_type)

    query = query.order_by(desc(DetectionRule.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    rules = list(result.scalars().all())

    return rules


@router.get("/{rule_id}", response_model=RuleSchema)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific detection rule"""
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return rule


@router.patch("/{rule_id}", response_model=RuleSchema)
async def update_rule(
    rule_id: int,
    rule_update: DetectionRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a detection rule"""
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Update fields
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)

    # Reload rules in engine
    await rule_engine.load_rules(db)

    return rule


@router.post("/{rule_id}/toggle", response_model=RuleSchema)
async def toggle_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle rule active status"""
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.is_active = not rule.is_active
    await db.commit()
    await db.refresh(rule)

    # Reload rules in engine
    await rule_engine.load_rules(db)

    return rule


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a detection rule"""
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    await db.delete(rule)
    await db.commit()

    # Reload rules in engine
    await rule_engine.load_rules(db)

    return {"message": "Rule deleted successfully"}
