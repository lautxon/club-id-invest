"""
Project Models
Investment projects (fideicomisos) and related documents.
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List

from app.core.database import Base
from app.core.config import ProjectStatusEnum, ProjectCategories


class Project(Base):
    """
    Project table for investment opportunities (fideicomisos).
    
    Business Rules:
    - Maximum 50 investors per project
    - Tracks funding progress for auto-investment triggers
    """
    __tablename__ = "projects"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Project Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)
    
    # Category/Level (matches investor tiers)
    category = Column(
        SQLEnum(ProjectCategories),
        default=ProjectCategories.LEVEL_1,
        nullable=False
    )
    
    # Financial Targets
    target_amount = Column(Float, nullable=False)
    minimum_investment = Column(Float, nullable=False)
    maximum_investment = Column(Float, nullable=True)
    
    # Funding Progress (denormalized for performance)
    raised_amount = Column(Float, default=0.0, nullable=False)
    raised_percent = Column(Float, default=0.0, nullable=False)
    investor_count = Column(Integer, default=0, nullable=False)
    
    # Club Co-Investment Tracking
    club_contribution_percent = Column(Float, default=0.0, nullable=True)
    club_contribution_amount = Column(Float, default=0.0, nullable=True)
    club_contribution_triggered = Column(Boolean, default=False, nullable=False)
    club_contribution_triggered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(
        SQLEnum(ProjectStatusEnum),
        default=ProjectStatusEnum.DRAFT,
        nullable=False,
        index=True
    )
    
    # Timeline
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    funding_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Location (for real estate projects)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Argentina", nullable=True)
    
    # Expected Returns
    expected_return_percent = Column(Float, nullable=True)
    expected_duration_months = Column(Integer, nullable=True)
    
    # Risk Rating (1-5, 5 being highest risk)
    risk_rating = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    investments = relationship(
        "Investment",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    documents = relationship(
        "ProjectDocument",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    contracts = relationship(
        "Contract",
        back_populates="project",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, title={self.title}, status={self.status.value})>"

    @property
    def is_fully_funded(self) -> bool:
        """Check if project has reached 100% funding."""
        return self.raised_percent >= 100.0

    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to reach target."""
        return max(0.0, self.target_amount - self.raised_amount)

    @property
    def can_accept_investments(self) -> bool:
        """Check if project can still accept investments."""
        return (
            self.status == ProjectStatusEnum.FUNDING
            and self.investor_count < 50
            and not self.is_fully_funded
        )


class ProjectDocument(Base):
    """
    Project documents (legal, financial, technical).
    """
    __tablename__ = "project_documents"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to Project
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Document Information
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # legal, financial, technical, marketing
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Access Control
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="documents")

    def __repr__(self) -> str:
        return f"<ProjectDocument(id={self.id}, title={self.title}, type={self.document_type})>"
