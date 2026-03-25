"""
Audit Log Model
Comprehensive audit trail for compliance and security.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.config import AuditActionEnum


class AuditLog(Base):
    """
    Audit Log table for compliance and security tracking.
    
    Retention: 7 years (2555 days) for legal compliance.
    
    Tracks:
    - All CRUD operations on sensitive data
    - Authentication events (login/logout)
    - Investment transactions
    - Contract signatures
    - Status changes
    - Admin actions
    """
    __tablename__ = "audit_logs"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Actor (who performed the action)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Action Details
    action = Column(SQLEnum(AuditActionEnum), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    # Resources: user, investment, project, contract, membership, etc.
    
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Change Tracking
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes_summary = Column(Text, nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True)  # For tracing across services
    
    # Additional Metadata
    metadata = Column(JSON, nullable=True)
    
    # Severity Level (for alerting)
    severity = Column(String(20), default="INFO", nullable=False)
    # Levels: INFO, WARNING, ERROR, CRITICAL
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    actor = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action.value}, resource={self.resource_type}, user_id={self.actor_user_id})>"

    @classmethod
    def log_action(
        cls,
        action: AuditActionEnum,
        resource_type: str,
        resource_id: int,
        actor_user_id: int = None,
        old_values: dict = None,
        new_values: dict = None,
        changes_summary: str = None,
        ip_address: str = None,
        user_agent: str = None,
        request_id: str = None,
        metadata: dict = None,
        severity: str = "INFO",
    ) -> "AuditLog":
        """
        Factory method to create an audit log entry.
        
        Usage:
            audit_entry = AuditLog.log_action(
                action=AuditActionEnum.INVEST,
                resource_type="investment",
                resource_id=investment_id,
                actor_user_id=current_user.id,
                new_values={"amount": 1000, "project_id": 5},
                ip_address=request.client.host,
            )
            db.add(audit_entry)
            db.commit()
        """
        return cls(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_user_id=actor_user_id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=changes_summary,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata,
            severity=severity,
        )
