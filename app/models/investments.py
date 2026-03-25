"""
Investment Models
Tracks individual investments and transactions.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.config import InvestmentStatusEnum


class Investment(Base):
    """
    Investment table tracks individual investments in projects.
    
    Business Rules:
    - Maximum 5 active investments per user
    - Investment limits vary by membership category
    """
    __tablename__ = "investments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    legal_entity_id = Column(Integer, ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True)
    
    # Investment Details
    investment_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    # Status
    status = Column(
        SQLEnum(InvestmentStatusEnum),
        default=InvestmentStatusEnum.PENDING,
        nullable=False,
        index=True
    )
    
    # Payment Information
    payment_method = Column(String(50), nullable=True)  # bank_transfer, credit_card, etc.
    payment_reference = Column(String(255), nullable=True)
    payment_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Club Co-Investment Flag
    is_club_contribution = Column(Boolean, default=False, nullable=False)
    club_contribution_trigger_reason = Column(Text, nullable=True)
    
    # Returns Tracking
    expected_return_percent = Column(Float, nullable=True)
    expected_return_amount = Column(Float, nullable=True)
    actual_return_amount = Column(Float, nullable=True)
    return_paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="investments")
    project = relationship("Project", back_populates="investments")
    legal_entity = relationship("LegalEntity", back_populates="investments")
    transactions = relationship(
        "InvestmentTransaction",
        back_populates="investment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Investment(id={self.id}, user_id={self.user_id}, project_id={self.project_id}, amount={self.investment_amount})>"

    @property
    def is_active(self) -> bool:
        """Check if investment is currently active."""
        return self.status == InvestmentStatusEnum.ACTIVE

    @property
    def is_pending(self) -> bool:
        """Check if investment is pending confirmation."""
        return self.status == InvestmentStatusEnum.PENDING


class InvestmentTransaction(Base):
    """
    Investment Transaction table tracks all financial movements.
    Provides audit trail for payments, returns, and penalties.
    """
    __tablename__ = "investment_transactions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to Investment
    investment_id = Column(Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=False)
    
    # Transaction Details
    transaction_type = Column(String(50), nullable=False)
    # Types: PAYMENT, RETURN, PENALTY, REFUND, CLUB_CONTRIBUTION, FEE
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    # Status
    status = Column(String(50), default="pending", nullable=False)
    # Status: pending, processing, completed, failed, cancelled
    
    # Payment Details
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    external_transaction_id = Column(String(255), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    investment = relationship("Investment", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<InvestmentTransaction(id={self.id}, investment_id={self.investment_id}, type={self.transaction_type}, amount={self.amount})>"
