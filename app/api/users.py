"""
Users API Endpoints
User management (admin only).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_admin_user, get_current_user
from app.schemas import UserResponse, UserRole
from app.models.users import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def list_users(
    role_filter: Optional[UserRole] = None,
    active_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    List all users (admin only).
    
    Filters:
    - role: Filter by user role
    - active_only: Only show active users
    """
    query = db.query(User)
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    if active_only:
        query = query.filter(User.is_active == True)
    
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user details by ID (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Activate a user account (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = True
    
    # Audit log
    from app.models.audit_logs import AuditLog
    from app.core.config import AuditActionEnum
    
    audit_entry = AuditLog.log_action(
        action=AuditActionEnum.STATUS_CHANGE,
        resource_type="user",
        resource_id=user_id,
        actor_user_id=current_user.id,
        changes_summary="Account activated by admin",
        severity="INFO",
    )
    db.add(audit_entry)
    db.commit()
    
    return {
        "success": True,
        "message": "User activated successfully",
        "user_id": user_id,
    }


@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Deactivate a user account (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    user.is_active = False
    
    # Audit log
    from app.models.audit_logs import AuditLog
    from app.core.config import AuditActionEnum
    
    audit_entry = AuditLog.log_action(
        action=AuditActionEnum.STATUS_CHANGE,
        resource_type="user",
        resource_id=user_id,
        actor_user_id=current_user.id,
        changes_summary="Account deactivated by admin",
        severity="WARNING",
    )
    db.add(audit_entry)
    db.commit()
    
    return {
        "success": True,
        "message": "User deactivated successfully",
        "user_id": user_id,
    }


@router.patch("/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user role (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    old_role = user.role
    user.role = new_role
    
    # Audit log
    from app.models.audit_logs import AuditLog
    from app.core.config import AuditActionEnum
    
    audit_entry = AuditLog.log_action(
        action=AuditActionEnum.STATUS_CHANGE,
        resource_type="user",
        resource_id=user_id,
        actor_user_id=current_user.id,
        old_values={"role": old_role.value},
        new_values={"role": new_role.value},
        changes_summary=f"Role changed from {old_role.value} to {new_role.value}",
        severity="WARNING",
    )
    db.add(audit_entry)
    db.commit()
    
    return {
        "success": True,
        "message": "User role updated successfully",
        "user_id": user_id,
        "new_role": new_role.value,
    }
