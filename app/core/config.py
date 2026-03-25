"""
Club ID Invest - Configuration Settings
Business Rules & Constants for Fintech Investment Platform
"""

from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


# =============================================================================
# BUSINESS RULES CONSTANTS - CO-INVESTMENT TIERS
# =============================================================================

class InvestmentTiers:
    """
    Investment tier thresholds and Club co-investment percentages.
    Rules are CRITICAL and must be enforced at both API and service level.
    """
    # Cebollitas Tier: >55% raised + 3 months -> Club contributes 45%
    CEBOLLITAS_MIN_RAISED_PERCENT = 55.0
    CEBOLLITAS_MIN_MONTHS = 3
    CEBOLLITAS_CLUB_CONTRIBUTION = 45.0
    
    # 1ra Div Tier: >65% raised + 6 months -> Club contributes 35%
    PRIMERA_DIV_MIN_RAISED_PERCENT = 65.0
    PRIMERA_DIV_MIN_MONTHS = 6
    PRIMERA_DIV_CLUB_CONTRIBUTION = 35.0
    
    # Senior Tier: >75% raised + 9 months -> Club contributes 25%
    SENIOR_MIN_RAISED_PERCENT = 75.0
    SENIOR_MIN_MONTHS = 9
    SENIOR_CLUB_CONTRIBUTION = 25.0


# =============================================================================
# MEMBERSHIP LIFECYCLE RULES
# =============================================================================

class MembershipRules:
    """
    Membership status transitions and inactivity penalties.
    """
    # Inactivity threshold: 60 days (2 months) -> Mark as 'inactive', charge $50
    INACTIVITY_WARNING_DAYS = 60
    INACTIVITY_PENALTY_AMOUNT = 50.0
    INACTIVITY_PENALTY_CURRENCY = "USD"
    
    # Churn threshold: 180 days (6 months) -> Mark as 'churned'
    CHURN_THRESHOLD_DAYS = 180
    
    # Maximum active investments per user
    MAX_ACTIVE_INVESTMENTS_PER_USER = 5
    
    # Maximum investors per project
    MAX_INVESTORS_PER_PROJECT = 50


# =============================================================================
# INVESTMENT CATEGORY LIMITS
# =============================================================================

class InvestmentLimits:
    """
    Minimum and maximum investment amounts per category.
    """
    CEBOLLITAS_MIN = 100.0
    CEBOLLITAS_MAX = 5000.0
    
    PRIMERA_DIV_MIN = 5000.0
    PRIMERA_DIV_MAX = 25000.0
    
    SENIOR_MIN = 25000.0
    SENIOR_MAX = 100000.0


# =============================================================================
# PROJECT CATEGORIES
# =============================================================================

class ProjectCategories(str, Enum):
    """
    Project classification levels matching investor tiers.
    """
    LEVEL_1 = "level_1"      # For Cebollitas
    LEVEL_2 = "level_2"      # For 1ra Div
    LEVEL_3 = "level_3"      # For Senior


# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    # Application
    APP_NAME: str = "Club ID Invest"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/club_id_invest"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # JWT Audience & Issuer
    JWT_AUDIENCE: str = "club-id-invest"
    JWT_ISSUER: str = "club-id-invest-api"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Redis & Celery (for scheduled tasks)
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Task Scheduling (in seconds)
    AUTO_INVESTMENT_CHECK_INTERVAL: int = 86400  # Daily
    MEMBERSHIP_LIFECYCLE_CHECK_INTERVAL: int = 86400  # Daily
    
    # Contract Generation
    CONTRACT_TEMPLATE_PATH: str = "templates/contracts"
    CONTRACT_OUTPUT_PATH: str = "generated_contracts"
    
    # Audit Logging
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years for legal compliance
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance for performance.
    """
    return Settings()


# =============================================================================
# ENUM DEFINITIONS
# =============================================================================


class MembershipCategoryEnum(str, Enum):
    """Investor membership categories."""
    CEBOLLITAS = "cebollitas"
    PRIMERA_DIV = "primera_div"
    SENIOR = "senior"


class MembershipStatusEnum(str, Enum):
    """Membership lifecycle status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    SUSPENDED = "suspended"


class ProjectStatusEnum(str, Enum):
    """Project funding status."""
    DRAFT = "draft"
    FUNDING = "funding"
    FUNDED = "funded"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InvestmentStatusEnum(str, Enum):
    """Investment lifecycle status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    RETURNED = "returned"
    WRITTEN_OFF = "written_off"


class ContractStatusEnum(str, Enum):
    """Contract generation and signing status."""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    CANCELLED = "cancelled"


class AuditActionEnum(str, Enum):
    """Types of auditable actions."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    INVEST = "INVEST"
    WITHDRAW = "WITHDRAW"
    SIGN_CONTRACT = "SIGN_CONTRACT"
    STATUS_CHANGE = "STATUS_CHANGE"


class UserRoleEnum(str, Enum):
    """User role-based access control."""
    INVESTOR = "investor"
    PROJECT_MANAGER = "project_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
