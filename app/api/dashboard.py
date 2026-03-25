"""
Dashboard API Endpoints
Provides dashboard data and alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.schemas import (
    DashboardResponse,
    InvestmentAlert,
    ProjectProgress,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """
    Get complete dashboard data for a user.
    
    Includes:
    - Total invested amount
    - Active investments count
    - Pending alerts (deadlines, payments)
    - Active projects progress
    - Membership status
    """
    from app.models.investments import Investment, InvestmentStatusEnum
    from app.models.projects import Project, ProjectStatusEnum
    from app.models.memberships import Membership
    
    # Get investment summary
    investment_stats = db.query(
        func.count(Investment.id).label("count"),
        func.sum(Investment.investment_amount).label("total"),
    ).filter(
        Investment.user_id == current_user_id,
        Investment.status.in_([InvestmentStatusEnum.ACTIVE, InvestmentStatusEnum.CONFIRMED]),
    ).first()
    
    total_invested = float(investment_stats.total or 0)
    active_count = investment_stats.count or 0
    
    # Get pending alerts
    alerts = get_pending_alerts(db, current_user_id)
    
    # Get active projects progress
    projects = get_active_projects_progress(db, current_user_id)
    
    # Get membership status
    membership = db.query(Membership).filter(Membership.user_id == current_user_id).first()
    membership_status = membership.status.value if membership else None
    
    return DashboardResponse(
        total_invested=total_invested,
        active_investments_count=active_count,
        total_returns=0.0,  # TODO: Calculate actual returns
        pending_alerts=alerts,
        active_projects=projects,
        membership_status=membership_status,
    )


def get_pending_alerts(db: Session, user_id: int) -> List[InvestmentAlert]:
    """Get pending alerts for user investments."""
    from app.models.investments import Investment, InvestmentStatusEnum
    from app.models.projects import Project
    
    alerts = []
    today = datetime.utcnow()
    
    # Get user's active investments
    investments = db.query(Investment).join(Project).filter(
        Investment.user_id == user_id,
        Investment.status.in_([InvestmentStatusEnum.PENDING, InvestmentStatusEnum.ACTIVE]),
    ).all()
    
    for inv in investments:
        project = inv.project
        
        # Check funding deadline (2 weeks warning)
        if project.funding_deadline:
            days_remaining = (project.funding_deadline - today).days
            if 0 < days_remaining <= 14:
                alerts.append(InvestmentAlert(
                    investment_id=inv.id,
                    project_title=project.title,
                    alert_type="funding_deadline",
                    message=f"Funding deadline in {days_remaining} days",
                    days_remaining=days_remaining,
                    severity="warning" if days_remaining <= 7 else "info",
                ))
        
        # Check pending payment
        if inv.status == InvestmentStatusEnum.PENDING:
            days_pending = (today - inv.created_at).days
            if days_pending > 3:
                alerts.append(InvestmentAlert(
                    investment_id=inv.id,
                    project_title=project.title,
                    alert_type="payment_pending",
                    message=f"Payment pending for {days_pending} days",
                    days_remaining=None,
                    severity="critical" if days_pending > 7 else "warning",
                ))
    
    return alerts


def get_active_projects_progress(db: Session, user_id: int) -> List[ProjectProgress]:
    """Get progress for projects user has invested in."""
    from app.models.investments import Investment, InvestmentStatusEnum
    from app.models.projects import Project, ProjectStatusEnum
    
    # Get distinct projects user invested in
    investments = db.query(Investment).filter(
        Investment.user_id == user_id,
        Investment.status.in_([InvestmentStatusEnum.ACTIVE, InvestmentStatusEnum.CONFIRMED]),
    ).all()
    
    project_ids = list(set(inv.project_id for inv in investments))
    
    projects = db.query(Project).filter(
        Project.id.in_(project_ids),
        Project.status.in_([ProjectStatusEnum.FUNDING, ProjectStatusEnum.ACTIVE]),
    ).all()
    
    today = datetime.utcnow()
    progress_list = []
    
    for project in projects:
        days_remaining = None
        if project.funding_deadline:
            days_remaining = max(0, (project.funding_deadline - today).days)
        
        progress_list.append(ProjectProgress(
            project_id=project.id,
            title=project.title,
            raised_percent=project.raised_percent,
            target_amount=project.target_amount,
            raised_amount=project.raised_amount,
            days_remaining=days_remaining,
            club_contribution_triggered=project.club_contribution_triggered,
        ))
    
    return progress_list


@router.get("/alerts", response_model=List[InvestmentAlert])
def get_alerts(
    severity: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """
    Get pending alerts with optional severity filter.
    
    Severity levels: info, warning, critical
    """
    alerts = get_pending_alerts(db, current_user_id)
    
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    return alerts[:limit]


@router.get("/projects", response_model=List[ProjectProgress])
def get_project_progress(
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """Get progress for all active projects user invested in."""
    return get_active_projects_progress(db, current_user_id)
