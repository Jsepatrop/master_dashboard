# backend/app/api/v1/endpoints/metrics.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
from datetime import datetime, timedelta
import json
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user, get_current_agent
from app.models.metrics import MetricData as MetricModel, MetricType
from app.models.machine import Machine as MachineModel
from app.schemas.metrics import (
    MetricData, MetricDataCreate, MetricsList, MetricsQuery,
    MetricsExport, MetricsBatch, RealTimeMetrics
)

router = APIRouter()

@router.get("/", response_model=MetricsList)
async def list_metrics(
    machine_ids: Optional[List[uuid.UUID]] = Query(None),
    metric_types: Optional[List[MetricType]] = Query(None),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get metrics with filtering and pagination"""
    query = db.query(MetricModel)
    
    # Apply filters
    if machine_ids:
        query = query.filter(MetricModel.machine_id.in_(machine_ids))
    if metric_types:
        query = query.filter(MetricModel.metric_type.in_(metric_types))
    if start_time:
        query = query.filter(MetricModel.timestamp >= start_time)
    if end_time:
        query = query.filter(MetricModel.timestamp <= end_time)
    
    # Order by timestamp descending
    query = query.order_by(desc(MetricModel.timestamp))
    
    total = query.count()
    metrics = query.offset(skip).limit(limit).all()
    
    return MetricsList(
        metrics=metrics,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=List[MetricData])
async def submit_metrics(
    metrics: List[MetricDataCreate],
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    """Submit metrics from client agent"""
    db_metrics = []
    
    for metric in metrics:
        # Verify machine belongs to the agent
        machine = db.query(MachineModel).filter(MachineModel.id == metric.machine_id).first()
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Machine {metric.machine_id} not found"
            )
        
        db_metric = MetricModel(
            **metric.dict(),
            timestamp=metric.timestamp or datetime.utcnow()
        )
        db.add(db_metric)
        db_metrics.append(db_metric)
    
    db.commit()
    
    # Refresh all metrics
    for metric in db_metrics:
        db.refresh(metric)
    
    return db_metrics

@router.post("/batch", response_model=List[MetricData])
async def submit_metrics_batch(
    batch: MetricsBatch,
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    """Submit batch of metrics from client agent"""
    # Verify machine exists
    machine = db.query(MachineModel).filter(MachineModel.id == batch.machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine {batch.machine_id} not found"
        )
    
    db_metrics = []
    timestamp = batch.timestamp or datetime.utcnow()
    
    for metric in batch.metrics:
        db_metric = MetricModel(
            machine_id=batch.machine_id,
            timestamp=timestamp,
            **metric.dict()
        )
        db.add(db_metric)
        db_metrics.append(db_metric)
    
    # Update machine last metrics update
    machine.last_metrics_update = timestamp
    machine.last_seen = timestamp
    
    db.commit()
    
    # Refresh all metrics
    for metric in db_metrics:
        db.refresh(metric)
    
    return db_metrics

@router.get("/realtime")
async def get_realtime_metrics(
    machine_ids: Optional[List[uuid.UUID]] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get latest metrics for real-time display"""
    query = db.query(MachineModel)
    
    if machine_ids:
        query = query.filter(MachineModel.id.in_(machine_ids))
    
    machines = query.all()
    realtime_data = {}
    
    for machine in machines:
        # Get latest metrics for each type
        latest_metrics = {}
        for metric_type in MetricType:
            latest = db.query(MetricModel).filter(
                and_(
                    MetricModel.machine_id == machine.id,
                    MetricModel.metric_type == metric_type
                )
            ).order_by(desc(MetricModel.timestamp)).first()
            
            if latest:
                latest_metrics[metric_type.value] = {
                    "value": latest.value,
                    "unit": latest.unit,
                    "timestamp": latest.timestamp.isoformat(),
                    "component_name": latest.component_name
                }
        
        realtime_data[str(machine.id)] = {
            "machine_name": machine.name,
            "status": machine.status.value,
            "metrics": latest_metrics,
            "last_seen": machine.last_seen.isoformat() if machine.last_seen else None
        }
    
    return realtime_data

@router.get("/export")
async def export_metrics(
    format: str = Query(..., regex="^(json|csv|xlsx)$"),
    machine_ids: Optional[List[uuid.UUID]] = Query(None),
    metric_types: Optional[List[MetricType]] = Query(None),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    include_metadata: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export metrics data"""
    query = db.query(MetricModel)
    
    # Apply filters
    if machine_ids:
        query = query.filter(MetricModel.machine_id.in_(machine_ids))
    if metric_types:
        query = query.filter(MetricModel.metric_type.in_(metric_types))
    if start_time:
        query = query.filter(MetricModel.timestamp >= start_time)
    if end_time:
        query = query.filter(MetricModel.timestamp <= end_time)
    
    metrics = query.order_by(MetricModel.timestamp).all()
    
    if format == "json":
        data = []
        for metric in metrics:
            metric_data = {
                "id": str(metric.id),
                "machine_id": str(metric.machine_id),
                "metric_type": metric.metric_type.value,
                "component_name": metric.component_name,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp.isoformat()
            }
            if include_metadata:
                metric_data["metadata"] = metric.metadata
            data.append(metric_data)
        
        json_str = json.dumps(data, indent=2)
        return StreamingResponse(
            io.StringIO(json_str),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=metrics.json"}
        )
    
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = ["id", "machine_id", "metric_type", "component_name", "value", "unit", "timestamp"]
        if include_metadata:
            headers.append("metadata")
        writer.writerow(headers)
        
        # Write data
        for metric in metrics:
            row = [
                str(metric.id),
                str(metric.machine_id),
                metric.metric_type.value,
                metric.component_name or "",
                metric.value,
                metric.unit or "",
                metric.timestamp.isoformat()
            ]
            if include_metadata:
                row.append(json.dumps(metric.metadata) if metric.metadata else "")
            writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=metrics.csv"}
        )

@router.get("/summary/{machine_id}")
async def get_metrics_summary(
    machine_id: uuid.UUID,
    hours: int = Query(24, ge=1, le=168),  # Last 1-168 hours
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get metrics summary for a machine"""
    # Verify machine exists
    machine = db.query(MachineModel).filter(MachineModel.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    summary = {}
    
    for metric_type in MetricType:
        metrics = db.query(MetricModel).filter(
            and_(
                MetricModel.machine_id == machine_id,
                MetricModel.metric_type == metric_type,
                MetricModel.timestamp >= start_time
            )
        ).all()
        
        if metrics:
            values = [m.value for m in metrics]
            summary[metric_type.value] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "unit": metrics[0].unit,
                "latest": values[-1],
                "latest_timestamp": metrics[-1].timestamp.isoformat()
            }
    
    return {
        "machine_id": str(machine_id),
        "machine_name": machine.name,
        "period_hours": hours,
        "summary": summary
    }

@router.delete("/cleanup")
async def cleanup_old_metrics(
    days: int = Query(30, ge=1, le=365),
    dry_run: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clean up old metrics data"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(MetricModel).filter(MetricModel.timestamp < cutoff_date)
    count = query.count()
    
    if not dry_run:
        query.delete()
        db.commit()
        message = f"Deleted {count} metrics older than {days} days"
    else:
        message = f"Would delete {count} metrics older than {days} days (dry run)"
    
    return {
        "message": message,
        "count": count,
        "cutoff_date": cutoff_date.isoformat(),
        "dry_run": dry_run
    }