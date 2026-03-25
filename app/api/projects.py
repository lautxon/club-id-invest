"""
Projects API Endpoints
Handles project listing and details.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas import ProjectResponse, ProjectStatus

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    status_filter: Optional[ProjectStatus] = None,
    category: Optional[str] = None,
    min_raised_percent: Optional[float] = Query(None, ge=0, le=100),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List projects with optional filters.
    
    Filters:
    - status: Filter by project status
    - category: Filter by category (level_1, level_2, level_3)
    - min_raised_percent: Minimum funding percentage
    """
    from app.models.projects import Project
    
    query = db.query(Project)
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    if category:
        query = query.filter(Project.category == category)
    
    if min_raised_percent is not None:
        query = query.filter(Project.raised_percent >= min_raised_percent)
    
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()
    
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get project details by ID."""
    from app.models.projects import Project
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/investors")
def get_project_investors(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get list of investors for a project (anonymized)."""
    from app.models.investments import Investment, InvestmentStatusEnum
    
    investments = db.query(Investment).filter(
        Investment.project_id == project_id,
        Investment.status.in_([InvestmentStatusEnum.ACTIVE, InvestmentStatusEnum.CONFIRMED]),
    ).all()
    
    # Return anonymized data
    investors = [
        {
            "investor_id": f"INV-{inv.id:04d}",
            "amount": inv.investment_amount,
            "currency": inv.currency,
            "confirmed_at": inv.confirmed_at.isoformat() if inv.confirmed_at else None,
        }
        for inv in investments
    ]
    
    return {
        "project_id": project_id,
        "total_investors": len(investors),
        "investors": investors,
    }
