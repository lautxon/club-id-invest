"""
Investment API Endpoints
Handles investment creation, validation, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas import (
    InvestmentCreate,
    InvestmentResponse,
    InvestmentValidate,
    InvestmentValidationResult,
    InvestmentStatus,
)
from app.services.investment_service import InvestmentService
from app.tasks.scheduled_tasks import process_investment_payment

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.post("/validate", response_model=InvestmentValidationResult)
def validate_investment(
    validation: InvestmentValidate,
    db: Session = Depends(get_db),
):
    """
    Validate an investment before creation.
    
    Checks:
    - Project capacity and status
    - User membership and limits
    - Investment amount limits by category
    - Maximum investments per user
    """
    service = InvestmentService(db)
    is_valid, errors, warnings = service.validate_investment(
        user_id=validation.user_id,
        project_id=validation.project_id,
        amount=validation.investment_amount,
    )
    
    # Get project for additional info
    from app.models.projects import Project
    project = db.query(Project).filter(Project.id == validation.project_id).first()
    
    return InvestmentValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        max_allowed=project.maximum_investment if project else None,
        remaining_capacity=project.remaining_amount if project else None,
    )


@router.post("/", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def create_investment(
    investment: InvestmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """
    Create a new investment.
    
    Requirements:
    - Active membership
    - Under investment limits
    - Project accepts investments
    """
    service = InvestmentService(db)
    
    try:
        new_investment = service.create_investment(
            user_id=current_user_id,
            project_id=investment.project_id,
            amount=investment.investment_amount,
            payment_method="bank_transfer",
            legal_entity_id=investment.legal_entity_id,
            notes=investment.notes,
        )
        
        # Queue payment processing task
        process_investment_payment.delay(new_investment.id)
        
        return InvestmentResponse.model_validate(new_investment)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{investment_id}", response_model=InvestmentResponse)
def get_investment(
    investment_id: int,
    db: Session = Depends(get_db),
):
    """Get investment details by ID."""
    from app.models.investments import Investment
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found",
        )
    
    return InvestmentResponse.model_validate(investment)


@router.get("/", response_model=List[InvestmentResponse])
def list_investments(
    status_filter: Optional[InvestmentStatus] = None,
    project_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """
    List investments with optional filters.
    
    Filters:
    - status: Filter by investment status
    - project_id: Filter by project
    """
    from app.models.investments import Investment
    
    query = db.query(Investment).filter(Investment.user_id == current_user_id)
    
    if status_filter:
        query = query.filter(Investment.status == status_filter)
    
    if project_id:
        query = query.filter(Investment.project_id == project_id)
    
    investments = query.order_by(Investment.created_at.desc()).offset(offset).limit(limit).all()
    
    return [InvestmentResponse.model_validate(inv) for inv in investments]


@router.post("/{investment_id}/confirm")
def confirm_investment(
    investment_id: int,
    db: Session = Depends(get_db),
):
    """
    Manually confirm an investment payment.
    Used for testing or manual processing.
    """
    from app.models.investments import Investment, InvestmentStatusEnum
    from datetime import datetime
    
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found",
        )
    
    investment.status = InvestmentStatusEnum.CONFIRMED
    investment.payment_confirmed_at = datetime.utcnow()
    investment.confirmed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "investment_id": investment_id,
        "status": "confirmed",
    }
