"""
Contracts API Endpoints
Handles contract generation and signing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas import (
    ContractCreate,
    ContractResponse,
    ContractSignRequest,
)

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
):
    """Generate a new contract for an investment."""
    from app.services.contract_service import ContractService
    
    service = ContractService(db)
    
    try:
        new_contract = service.generate_contract(
            project_id=contract.project_id,
            investment_id=contract.investment_id,
            legal_entity_id=contract.legal_entity_id,
            contract_type=contract.contract_type,
            title=contract.title,
        )
        
        return ContractResponse.model_validate(new_contract)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{contract_id}/generate-pdf")
def generate_pdf(
    contract_id: int,
    db: Session = Depends(get_db),
):
    """Generate PDF for a contract."""
    from app.services.contract_service import ContractService
    
    service = ContractService(db)
    result = service.generate_pdf(contract_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to generate PDF"),
        )
    
    return result


@router.post("/{contract_id}/send-signature")
def send_for_signature(
    contract_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """Send contract for electronic signature."""
    from app.services.contract_service import ContractService
    
    service = ContractService(db)
    result = service.send_for_signature(contract_id, current_user_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send for signature"),
        )
    
    return result


@router.post("/{contract_id}/sign")
def sign_contract(
    contract_id: int,
    sign_request: ContractSignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """Sign contract electronically."""
    from app.services.contract_service import ContractService
    
    # Get client info from request
    ip_address = request.client.host if request.client else sign_request.ip_address
    user_agent = request.headers.get("user-agent", "unknown")
    
    service = ContractService(db)
    result = service.sign_contract(
        contract_id=contract_id,
        user_id=current_user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to sign contract"),
        )
    
    return result


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
):
    """Get contract details by ID."""
    from app.models.contracts import Contract
    
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    
    return ContractResponse.model_validate(contract)


@router.get("/", response_model=List[ContractResponse])
def list_contracts(
    status_filter: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
):
    """List contracts for current user."""
    from app.models.contracts import Contract
    
    query = db.query(Contract).filter(Contract.signed_by_user_id == current_user_id)
    
    if status_filter:
        query = query.filter(Contract.status == status_filter)
    
    contracts = query.order_by(Contract.created_at.desc()).limit(limit).all()
    
    return [ContractResponse.model_validate(c) for c in contracts]
