"""
Pydantic Schemas for API Validation
Type-safe request/response models for FastAPI endpoints.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUM SCHEMAS
# =============================================================================

class MembershipCategory(str, Enum):
    CEBOLLITAS = "cebollitas"
    PRIMERA_DIV = "primera_div"
    SENIOR = "senior"


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    SUSPENDED = "suspended"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    FUNDING = "funding"
    FUNDED = "funded"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InvestmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    RETURNED = "returned"
    WRITTEN_OFF = "written_off"


class UserRole(str, Enum):
    INVESTOR = "investor"
    PROJECT_MANAGER = "project_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.INVESTOR


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


# =============================================================================
# MEMBERSHIP SCHEMAS
# =============================================================================

class MembershipBase(BaseModel):
    """Base schema for membership data."""
    category: MembershipCategory = MembershipCategory.CEBOLLITAS


class MembershipCreate(MembershipBase):
    """Schema for creating a membership."""
    user_id: int


class MembershipResponse(BaseModel):
    """Schema for membership response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    category: MembershipCategory
    status: MembershipStatus
    join_date: datetime
    last_activity_date: Optional[datetime] = None
    penalty_amount: float
    total_investments_count: int
    total_invested_amount: float
    active_investments_count: int
    created_at: datetime


# =============================================================================
# PROJECT SCHEMAS
# =============================================================================

class ProjectBase(BaseModel):
    """Base schema for project data."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    target_amount: float = Field(..., gt=0)
    minimum_investment: float = Field(..., gt=0)
    maximum_investment: Optional[float] = Field(None, gt=0)
    expected_return_percent: Optional[float] = Field(None, ge=0, le=100)
    expected_duration_months: Optional[int] = Field(None, gt=0)
    risk_rating: Optional[int] = Field(None, ge=1, le=5)


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    category: str = "level_1"
    funding_deadline: datetime


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    category: str
    raised_amount: float
    raised_percent: float
    investor_count: int
    club_contribution_percent: Optional[float] = None
    club_contribution_amount: Optional[float] = None
    club_contribution_triggered: bool
    status: ProjectStatus
    funding_deadline: Optional[datetime] = None
    created_at: datetime
    published_at: Optional[datetime] = None


# =============================================================================
# INVESTMENT SCHEMAS
# =============================================================================

class InvestmentBase(BaseModel):
    """Base schema for investment data."""
    investment_amount: float = Field(..., gt=0)
    currency: str = "USD"
    notes: Optional[str] = None


class InvestmentCreate(InvestmentBase):
    """Schema for creating an investment."""
    project_id: int
    legal_entity_id: Optional[int] = None


class InvestmentValidate(BaseModel):
    """Schema for validating investment limits before creation."""
    project_id: int
    investment_amount: float
    user_id: int


class InvestmentValidationResult(BaseModel):
    """Result of investment validation."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    max_allowed: Optional[float] = None
    remaining_capacity: Optional[float] = None


class InvestmentResponse(BaseModel):
    """Schema for investment response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    project_id: int
    legal_entity_id: Optional[int] = None
    investment_amount: float
    currency: str
    status: InvestmentStatus
    payment_method: Optional[str] = None
    payment_confirmed_at: Optional[datetime] = None
    is_club_contribution: bool
    expected_return_percent: Optional[float] = None
    created_at: datetime
    confirmed_at: Optional[datetime] = None


# =============================================================================
# CONTRACT SCHEMAS
# =============================================================================

class ContractBase(BaseModel):
    """Base schema for contract data."""
    contract_type: str
    title: str
    principal_amount: float
    interest_rate: Optional[float] = None
    term_months: Optional[int] = None


class ContractCreate(ContractBase):
    """Schema for creating a contract."""
    project_id: int
    investment_id: Optional[int] = None
    legal_entity_id: Optional[int] = None


class ContractSignRequest(BaseModel):
    """Schema for contract signature request."""
    contract_id: int
    ip_address: str
    user_agent: str


class ContractResponse(BaseModel):
    """Schema for contract response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contract_number: str
    contract_type: str
    title: str
    principal_amount: float
    currency: str
    status: str
    is_club_contribution_contract: bool
    created_at: datetime
    signed_at: Optional[datetime] = None


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================

class InvestmentAlert(BaseModel):
    """Investment alert for dashboard."""
    investment_id: int
    project_title: str
    alert_type: str  # funding_deadline, payment_pending, return_expected
    message: str
    days_remaining: Optional[int] = None
    severity: str  # info, warning, critical


class ProjectProgress(BaseModel):
    """Project progress for dashboard."""
    project_id: int
    title: str
    raised_percent: float
    target_amount: float
    raised_amount: float
    days_remaining: Optional[int] = None
    club_contribution_triggered: bool


class DashboardResponse(BaseModel):
    """Complete dashboard response."""
    total_invested: float
    active_investments_count: int
    total_returns: float
    pending_alerts: List[InvestmentAlert]
    active_projects: List[ProjectProgress]
    membership_status: Optional[str] = None


# =============================================================================
# AUTH SCHEMAS
# =============================================================================

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


# =============================================================================
# AUDIT LOG SCHEMAS
# =============================================================================

class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    actor_user_id: Optional[int] = None
    changes_summary: Optional[str] = None
    severity: str
    created_at: datetime
    ip_address: Optional[str] = None
