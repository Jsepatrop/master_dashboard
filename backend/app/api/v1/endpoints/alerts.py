# backend/app/api/v1/endpoints/alerts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.alerts import Alert as AlertModel, AlertRule as AlertRuleModel, AlertStatus
from app.models.machine import Machine as MachineModel
from app.schemas.alerts import (
    Alert, AlertCreate, AlertUpdate, AlertsList,
    AlertRule, AlertRuleCreate, AlertRuleUpdate, AlertSummary
)

router = APIRouter()

# Alert Rules Management
@router.get("/rules", response_model=List[AlertRule])
async def list_alert_rules(
    machine_id: Optional[uuid.UUID] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of alert rules"""
    query = db.query(AlertRuleModel)
    
    if machine_id:
        query = query.filter(AlertRuleModel.machine_id == machine_id)
    if enabled is not None:
        query = query.filter(AlertRuleModel.enabled == enabled)
    
    return query.all()

@router.post("/rules", response_model=AlertRule)
async def create_alert_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new alert rule"""
    # Verify machine exists
    machine = db.query(MachineModel).filter(MachineModel.id == rule.machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    db_rule = AlertRuleModel(
        **rule.dict(),
        created_by=current_user.get("sub", "admin")
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return db_rule

@router.get("/rules/{rule_id}", response_model=AlertRule)
async def get_alert_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alert rule by ID"""
    rule = db.query(AlertRuleModel).filter(AlertRuleModel.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    return rule

@router.put("/rules/{rule_id}", response_model=AlertRule)
async def update_alert_rule(
    rule_id: uuid.UUID,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update alert rule"""
    rule = db.query(AlertRuleModel).filter(AlertRuleModel.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    update_data = rule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    rule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rule)
    
    return rule

@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete alert rule"""
    rule = db.query(AlertRuleModel).filter(AlertRuleModel.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Alert rule deleted successfully"}

# Alerts Management
@router.get("/", response_model=AlertsList)
async def list_alerts(
    machine_id: Optional[uuid.UUID] = None,
    status: Optional[AlertStatus] = None,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of alerts with filtering"""
    query = db.query(AlertModel)
    
    if machine_id:
        query = query.filter(AlertModel.machine_id == machine_id)
    if status:
        query = query.filter(AlertModel.status == status)
    if severity:
        query = query.filter(AlertModel.severity == severity)
    
    # Order by triggered_at descending
    query = query.order_by(desc(AlertModel.triggered_at))
    
    total = query.count()
    alerts = query.offset(skip).limit(limit).all()
    
    return AlertsList(
        alerts=alerts,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=Alert)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new alert"""
    db_alert = AlertModel(**alert.dict())
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alert by ID"""
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert

@router.put("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: uuid.UUID,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update alert (acknowledge, resolve, etc.)"""
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    update_data = alert_update.dict(exclude_unset=True)
    current_time = datetime.utcnow()
    current_username = current_user.get("sub", "admin")
    
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    # Set timestamps based on status changes
    if alert_update.status == AlertStatus.ACKNOWLEDGED and not alert.acknowledged_at:
        alert.acknowledged_at = current_time
        alert.acknowledged_by = current_username
    elif alert_update.status == AlertStatus.RESOLVED and not alert.resolved_at:
        alert.resolved_at = current_time
        alert.resolved_by = current_username
    
    db.commit()
    db.refresh(alert)
    
    return alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete alert"""
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}

@router.get("/summary/dashboard", response_model=AlertSummary)
async def get_alerts_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts summary for dashboard"""
    total_alerts = db.query(AlertModel).count()
    active_alerts = db.query(AlertModel).filter(AlertModel.status == AlertStatus.ACTIVE).count()
    critical_alerts = db.query(AlertModel).filter(
        and_(AlertModel.severity == "critical", AlertModel.status == AlertStatus.ACTIVE)
    ).count()
    high_alerts = db.query(AlertModel).filter(
        and_(AlertModel.severity == "high", AlertModel.status == AlertStatus.ACTIVE)
    ).count()
    medium_alerts = db.query(AlertModel).filter(
        and_(AlertModel.severity == "medium", AlertModel.status == AlertStatus.ACTIVE)
    ).count()
    low_alerts = db.query(AlertModel).filter(
        and_(AlertModel.severity == "low", AlertModel.status == AlertStatus.ACTIVE)
    ).count()
    
    return AlertSummary(
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        medium_alerts=medium_alerts,
        low_alerts=low_alerts
    )

@router.post("/bulk-acknowledge")
async def bulk_acknowledge_alerts(
    alert_ids: List[uuid.UUID],
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge multiple alerts at once"""
    current_time = datetime.utcnow()
    current_username = current_user.get("sub", "admin")
    
    updated_count = 0
    
    for alert_id in alert_ids:
        alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
        if alert and alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = current_time
            alert.acknowledged_by = current_username
            if notes:
                alert.notes = notes
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Acknowledged {updated_count} alerts",
        "updated_count": updated_count
    }

@router.post("/bulk-resolve")
async def bulk_resolve_alerts(
    alert_ids: List[uuid.UUID],
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resolve multiple alerts at once"""
    current_time = datetime.utcnow()
    current_username = current_user.get("sub", "admin")
    
    updated_count = 0
    
    for alert_id in alert_ids:
        alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
        if alert and alert.status != AlertStatus.RESOLVED:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = current_time
            alert.resolved_by = current_username
            if notes:
                alert.notes = notes
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Resolved {updated_count} alerts",
        "updated_count": updated_count
    }