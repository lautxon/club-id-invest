"""
Legal Entity Model
For managing corporate structures and legal representatives.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class LegalEntity(Base):
    """
    Legal Entity table for corporate investors and legal representatives.
    A user can represent multiple legal entities (companies, trusts, etc.).
    """
    __tablename__ = "legal_entities"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to User (legal representative)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Entity Information
    legal_name = Column(String(255), nullable=False, index=True)
    trade_name = Column(String(255), nullable=True)
    tax_id = Column(String(50), unique=True, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # SA, SRL, Trust, etc.
    
    # Registration Details
    registration_number = Column(String(100), nullable=True)
    jurisdiction = Column(String(100), nullable=True)  # Country/State of incorporation
    incorporation_date = Column(DateTime, nullable=True)
    
    # Contact Information
    registered_address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Argentina", nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Banking Information (encrypted at application level)
    bank_name = Column(String(100), nullable=True)
    bank_account_number = Column(String(100), nullable=True)
    bank_routing_code = Column(String(50), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="legal_entities")
    investments = relationship(
        "Investment",
        back_populates="legal_entity",
        lazy="selectin"
    )
    contracts = relationship(
        "Contract",
        back_populates="legal_entity",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<LegalEntity(id={self.id}, legal_name={self.legal_name}, tax_id={self.tax_id})>"

    @property
    def full_legal_info(self) -> str:
        """Return formatted legal entity information."""
        return f"{self.legal_name} ({self.entity_type}) - Tax ID: {self.tax_id}"
