"""
Authentication API Endpoints
Handles login, registration, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import AuthenticationService
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.
    
    Requirements:
    - Valid email format
    - Password minimum 8 characters
    - Email not already registered
    
    After registration, user receives:
    - Active membership (Cebollitas tier)
    - Unverified account status
    """
    service = AuthenticationService(db)
    
    user, error = service.register_user(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    db.commit()
    
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Login and receive JWT tokens.
    
    Returns:
    - access_token: For API requests (expires in 30 min)
    - refresh_token: For getting new access tokens (expires in 7 days)
    - user: Basic user information
    """
    service = AuthenticationService(db)
    
    # Get client info for audit
    ip_address = request.client.host if request.client else "unknown"
    
    user, error = service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
    )
    
    if error:
        # Audit failed login attempt
        from app.models.audit_logs import AuditLog
        from app.core.config import AuditActionEnum
        
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.LOGIN,
            resource_type="auth",
            resource_id=None,
            actor_user_id=None,
            metadata={"email": login_data.email, "ip_address": ip_address},
            changes_summary="Failed login attempt",
            severity="WARNING",
        )
        db.add(audit_entry)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    token_data = service.create_token_pair(user)
    
    db.commit()
    
    return Token(**token_data)


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Refresh access token using refresh token.
    
    Send the refresh token in the Authorization header:
    Authorization: Bearer <refresh_token>
    
    Returns new access_token and refresh_token pair.
    """
    service = AuthenticationService(db)
    
    refresh_token = credentials.credentials
    token_data, error = service.refresh_access_token(refresh_token)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return Token(**token_data)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update current user profile.
    
    Updatable fields:
    - first_name
    - last_name
    - phone
    """
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    # Audit log
    from app.models.audit_logs import AuditLog
    from app.core.config import AuditActionEnum
    
    audit_entry = AuditLog.log_action(
        action=AuditActionEnum.UPDATE,
        resource_type="user",
        resource_id=current_user.id,
        actor_user_id=current_user.id,
        new_values=update_data,
        severity="INFO",
    )
    db.add(audit_entry)
    db.commit()
    
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user.
    
    Note: JWT tokens cannot be invalidated server-side.
    Client should discard tokens after calling this endpoint.
    """
    from app.models.audit_logs import AuditLog
    from app.core.config import AuditActionEnum
    
    # Audit logout
    audit_entry = AuditLog.log_action(
        action=AuditActionEnum.LOGOUT,
        resource_type="user",
        resource_id=current_user.id,
        actor_user_id=current_user.id,
        severity="INFO",
    )
    db.add(audit_entry)
    db.commit()
    
    return {
        "success": True,
        "message": "Logged out successfully",
        "user_id": current_user.id,
    }


@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change current user password.
    
    Requirements:
    - Old password must be correct
    - New password minimum 8 characters
    """
    service = AuthenticationService(db)
    
    success, error = service.change_password(
        user=current_user,
        old_password=old_password,
        new_password=new_password,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Password changed successfully",
    }
