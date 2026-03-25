"""
User Model
Core user authentication and profile management.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.config import UserRoleEnum


class User(Base):
    """
    User table for authentication and profile management.
    Supports role-based access control (RBAC).
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Role-Based Access Control
    role = Column(
        SQLEnum(UserRoleEnum),
        default=UserRoleEnum.INVESTOR,
        nullable=False
    )
    
    # Profile Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    legal_entities = relationship(
        "LegalEntity",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    memberships = relationship(
        "Membership",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    investments = relationship(
        "Investment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    signed_contracts = relationship(
        "Contract",
        back_populates="signer",
        foreign_keys="Contract.signed_by_user_id",
        lazy="selectin"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="actor",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"

    @property
    def full_name(self) -> str:
        """Return full name of the user."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]
