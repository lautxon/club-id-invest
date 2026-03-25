"""
Membership Model
Manages investor membership tiers, status, and lifecycle.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.config import MembershipCategoryEnum, MembershipStatusEnum


class Membership(Base):
    """
    Membership table tracks investor category and lifecycle status.
    
    Business Rules:
    - Cebollitas: >55% raised + 3 months -> Club contributes 45%
    - 1ra Div: >65% raised + 6 months -> Club contributes 35%
    - Senior: >75% raised + 9 months -> Club contributes 25%
    
    Lifecycle:
    - 60 days inactive -> Mark 'inactive', charge $50 penalty
    - 180 days inactive -> Mark 'churned'
    """
    __tablename__ = "memberships"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Membership Category (Investor Tier)
    category = Column(
        SQLEnum(MembershipCategoryEnum),
        default=MembershipCategoryEnum.CEBOLLITAS,
        nullable=False
    )
    
    # Lifecycle Status
    status = Column(
        SQLEnum(MembershipStatusEnum),
        default=MembershipStatusEnum.ACTIVE,
        nullable=False,
        index=True
    )
    
    # Important Dates for Business Rules
    join_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Category Upgrade/Downgrade Tracking
    category_changed_at = Column(DateTime(timezone=True), nullable=True)
    previous_category = Column(String(50), nullable=True)
    
    # Inactivity Penalty Tracking
    penalty_amount = Column(Float, default=0.0, nullable=False)
    penalty_currency = Column(String(10), default="USD", nullable=False)
    last_penalty_applied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Investment Statistics (denormalized for performance)
    total_investments_count = Column(Integer, default=0, nullable=False)
    total_invested_amount = Column(Float, default=0.0, nullable=False)
    active_investments_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<Membership(id={self.id}, user_id={self.user_id}, category={self.category.value}, status={self.status.value})>"

    @property
    def is_inactive(self) -> bool:
        """Check if membership is inactive."""
        return self.status == MembershipStatusEnum.INACTIVE

    @property
    def is_churned(self) -> bool:
        """Check if membership has churned."""
        return self.status == MembershipStatusEnum.CHURNED

    def get_club_contribution_percent(self) -> float:
        """
        Get Club co-investment percentage based on category.
        
        Returns:
            float: Club contribution percentage (45%, 35%, or 25%)
        """
        contribution_map = {
            MembershipCategoryEnum.CEBOLLITAS: 45.0,
            MembershipCategoryEnum.PRIMERA_DIV: 35.0,
            MembershipCategoryEnum.SENIOR: 25.0,
        }
        return contribution_map.get(self.category, 0.0)

    def get_minimum_investment_months(self) -> int:
        """
        Get minimum months required for auto-investment trigger.
        
        Returns:
            int: Minimum months (3, 6, or 9)
        """
        months_map = {
            MembershipCategoryEnum.CEBOLLITAS: 3,
            MembershipCategoryEnum.PRIMERA_DIV: 6,
            MembershipCategoryEnum.SENIOR: 9,
        }
        return months_map.get(self.category, 0)

    def get_minimum_raised_percent(self) -> float:
        """
        Get minimum raised percentage for auto-investment trigger.
        
        Returns:
            float: Minimum raised percentage (55%, 65%, or 75%)
        """
        percent_map = {
            MembershipCategoryEnum.CEBOLLITAS: 55.0,
            MembershipCategoryEnum.PRIMERA_DIV: 65.0,
            MembershipCategoryEnum.SENIOR: 75.0,
        }
        return percent_map.get(self.category, 0.0)
