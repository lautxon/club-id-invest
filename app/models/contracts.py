"""
Contract Model
Legal contracts for investments (fideicomisos).
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.config import ContractStatusEnum


class Contract(Base):
    """
    Contract table for legal agreements (fideicomisos).
    Generates PDF contracts with dynamic data for each investment.
    """
    __tablename__ = "contracts"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    investment_id = Column(Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=True)
    legal_entity_id = Column(Integer, ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=True)
    signed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Contract Information
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    contract_type = Column(String(50), nullable=False)
    # Types: FIDEICOMISO, INVESTMENT_AGREEMENT, CLUB_CONTRIBUTION, AMENDMENT
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Financial Terms
    principal_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=True)
    term_months = Column(Integer, nullable=True)
    currency = Column(String(10), default="USD", nullable=False)
    
    # Status
    status = Column(
        SQLEnum(ContractStatusEnum),
        default=ContractStatusEnum.DRAFT,
        nullable=False,
        index=True
    )
    
    # Document Storage
    template_path = Column(String(500), nullable=True)
    generated_pdf_path = Column(String(500), nullable=True)
    signed_pdf_path = Column(String(500), nullable=True)
    
    # Electronic Signature (simulated)
    signature_hash = Column(String(255), nullable=True)
    signature_timestamp = Column(DateTime(timezone=True), nullable=True)
    signature_ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    signature_user_agent = Column(String(500), nullable=True)
    
    # Club Contribution Flag
    is_club_contribution_contract = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="contracts")
    investment = relationship("Investment", backref="contract")
    legal_entity = relationship("LegalEntity", back_populates="contracts")
    signer = relationship("User", foreign_keys=[signed_by_user_id])

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, contract_number={self.contract_number}, status={self.status.value})>"

    @property
    def is_signed(self) -> bool:
        """Check if contract is fully signed."""
        return self.status == ContractStatusEnum.SIGNED

    @property
    def is_pending_signature(self) -> bool:
        """Check if contract is awaiting signature."""
        return self.status == ContractStatusEnum.PENDING_SIGNATURE

    def generate_signature_hash(self, user_id: int, ip_address: str, user_agent: str) -> str:
        """
        Generate a simulated electronic signature hash.
        In production, use a proper cryptographic signature service.
        """
        import hashlib
        import json
        
        data = {
            "contract_id": self.id,
            "contract_number": self.contract_number,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        data_string = json.dumps(data, sort_keys=True)
        signature_hash = hashlib.sha256(data_string.encode()).hexdigest()
        
        return signature_hash
