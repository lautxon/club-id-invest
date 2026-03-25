"""
Authentication Service
Handles user authentication, registration, and token management.
"""

from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, Tuple
import logging

from app.core.config import get_settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.models.users import User
from app.models.audit_logs import AuditLog
from app.core.config import AuditActionEnum, UserRoleEnum

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Service for managing user authentication.
    
    Features:
    - User registration
    - Login with JWT tokens
    - Password verification
    - Token refresh
    """

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user by email and password.
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            Tuple of (User, None) if successful, (None, error_message) if failed
        """
        user = self.db.query(User).filter(User.email == email.lower()).first()
        
        if not user:
            return None, "Invalid email or password"
        
        if not user.is_active:
            return None, "Account is inactive. Please contact support."
        
        if not verify_password(password, user.password_hash):
            return None, "Invalid email or password"
        
        # Update last login
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        
        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.LOGIN,
            resource_type="user",
            resource_id=user.id,
            actor_user_id=user.id,
            severity="INFO",
        )
        self.db.add(audit_entry)
        
        return user, None

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        role: UserRoleEnum = UserRoleEnum.INVESTOR,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            first_name: User first name
            last_name: User last name
            phone: Optional phone number
            role: User role (default: INVESTOR)
        
        Returns:
            Tuple of (User, None) if successful, (None, error_message) if failed
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            return None, "Email already registered"
        
        # Validate password strength
        if len(password) < 8:
            return None, "Password must be at least 8 characters long"
        
        # Create user
        user = User(
            email=email.lower(),
            password_hash=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            is_active=True,
            is_verified=False,
        )
        
        self.db.add(user)
        self.db.flush()
        
        # Create initial membership
        from app.models.memberships import Membership, MembershipCategoryEnum, MembershipStatusEnum
        from datetime import datetime
        
        membership = Membership(
            user_id=user.id,
            category=MembershipCategoryEnum.CEBOLLITAS,
            status=MembershipStatusEnum.ACTIVE,
            join_date=datetime.utcnow(),
            last_activity_date=datetime.utcnow(),
        )
        self.db.add(membership)
        
        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.CREATE,
            resource_type="user",
            resource_id=user.id,
            actor_user_id=user.id,
            new_values={"email": email, "role": role.value},
            severity="INFO",
        )
        self.db.add(audit_entry)
        
        logger.info(f"Registered new user: {email} (ID: {user.id})")
        return user, None

    def create_token_pair(self, user: User) -> dict:
        """
        Create access and refresh token pair for a user.
        
        Args:
            user: User object
        
        Returns:
            Dict with tokens and metadata
        """
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }
        )
        
        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
                "email": user.email,
            }
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
            },
        }

    def refresh_access_token(self, refresh_token: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Tuple of (token_dict, None) if successful, (None, error_message) if failed
        """
        from app.core.security import decode_token
        
        try:
            payload = decode_token(refresh_token)
        except Exception as e:
            return None, f"Invalid refresh token: {str(e)}"
        
        # Check token type
        if payload.get("type") != "refresh":
            return None, "Invalid token type"
        
        # Get user
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            return None, "User not found"
        
        if not user.is_active:
            return None, "Account is inactive"
        
        # Create new token pair
        return self.create_token_pair(user), None

    def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password.
        
        Args:
            user: User object
            old_password: Current password
            new_password: New password
        
        Returns:
            Tuple of (True, None) if successful, (False, error_message) if failed
        """
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters long"
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        
        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.UPDATE,
            resource_type="user",
            resource_id=user.id,
            actor_user_id=user.id,
            changes_summary="Password changed",
            severity="WARNING",
        )
        self.db.add(audit_entry)
        
        logger.info(f"Password changed for user {user.id}")
        return True, None

    def deactivate_user(self, user: User, admin_user: User) -> Tuple[bool, Optional[str]]:
        """
        Deactivate a user account (admin only).
        
        Args:
            user: User to deactivate
            admin_user: Admin performing the action
        
        Returns:
            Tuple of (True, None) if successful, (False, error_message) if failed
        """
        if user.id == admin_user.id:
            return False, "Cannot deactivate your own account"
        
        user.is_active = False
        
        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.STATUS_CHANGE,
            resource_type="user",
            resource_id=user.id,
            actor_user_id=admin_user.id,
            changes_summary=f"Account deactivated by admin {admin_user.email}",
            severity="WARNING",
        )
        self.db.add(audit_entry)
        
        logger.info(f"User {user.id} deactivated by admin {admin_user.id}")
        return True, None
