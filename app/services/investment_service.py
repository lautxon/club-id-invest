"""
Investment Service
Handles investment validation, creation, and auto-investment triggers.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import logging

from app.core.config import (
    InvestmentTiers,
    MembershipRules,
    InvestmentLimits,
    MembershipCategoryEnum,
    InvestmentStatusEnum,
    ProjectStatusEnum,
    AuditActionEnum,
)
from app.models.investments import Investment, InvestmentTransaction
from app.models.projects import Project
from app.models.memberships import Membership
from app.models.audit_logs import AuditLog

logger = logging.getLogger(__name__)


class InvestmentService:
    """
    Service for managing investments and co-investment logic.
    
    Business Rules:
    - Cebollitas: >55% raised + 3 months -> Club contributes 45%
    - 1ra Div: >65% raised + 6 months -> Club contributes 35%
    - Senior: >75% raised + 9 months -> Club contributes 25%
    """

    def __init__(self, db: Session):
        self.db = db

    def validate_investment(
        self,
        user_id: int,
        project_id: int,
        amount: float,
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate investment against business rules.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check project exists and accepts investments
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            errors.append(f"Project {project_id} not found")
            return False, errors, warnings

        if not project.can_accept_investments:
            errors.append(f"Project '{project.title}' is not accepting investments")
            return False, errors, warnings

        # Check user membership and limits
        membership = (
            self.db.query(Membership)
            .filter(Membership.user_id == user_id, Membership.status == MembershipStatusEnum.ACTIVE)
            .first()
        )
        if not membership:
            errors.append("No active membership found for user")
            return False, errors, warnings

        # Check max active investments per user
        if membership.active_investments_count >= MembershipRules.MAX_ACTIVE_INVESTMENTS_PER_USER:
            errors.append(
                f"Maximum {MembershipRules.MAX_ACTIVE_INVESTMENTS_PER_USER} active investments reached"
            )
            return False, errors, warnings

        # Check project capacity
        if project.investor_count >= MembershipRules.MAX_INVESTORS_PER_PROJECT:
            errors.append(f"Project has reached maximum {MembershipRules.MAX_INVESTORS_PER_PROJECT} investors")
            return False, errors, warnings

        # Check investment limits by category
        min_amount, max_amount = self._get_investment_limits(membership.category)
        if amount < min_amount:
            errors.append(f"Minimum investment for {membership.category.value} is ${min_amount}")
        if max_amount and amount > max_amount:
            errors.append(f"Maximum investment for {membership.category.value} is ${max_amount}")

        # Check if user already invested in this project
        existing_investment = (
            self.db.query(Investment)
            .filter(
                Investment.user_id == user_id,
                Investment.project_id == project_id,
                Investment.status.in_([InvestmentStatusEnum.PENDING, InvestmentStatusEnum.ACTIVE])
            )
            .first()
        )
        if existing_investment:
            warnings.append("You already have an active investment in this project")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def _get_investment_limits(self, category: MembershipCategoryEnum) -> Tuple[float, Optional[float]]:
        """Get min/max investment limits for membership category."""
        limits = {
            MembershipCategoryEnum.CEBOLLITAS: (InvestmentLimits.CEBOLLITAS_MIN, InvestmentLimits.CEBOLLITAS_MAX),
            MembershipCategoryEnum.PRIMERA_DIV: (InvestmentLimits.PRIMERA_DIV_MIN, InvestmentLimits.PRIMERA_DIV_MAX),
            MembershipCategoryEnum.SENIOR: (InvestmentLimits.SENIOR_MIN, InvestmentLimits.SENIOR_MAX),
        }
        return limits.get(category, (0, None))

    def create_investment(
        self,
        user_id: int,
        project_id: int,
        amount: float,
        payment_method: str = "bank_transfer",
        legal_entity_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Investment:
        """
        Create a new investment after validation.
        
        Raises:
            ValueError: If investment validation fails
        """
        # Validate first
        is_valid, errors, warnings = self.validate_investment(user_id, project_id, amount)
        if not is_valid:
            raise ValueError("; ".join(errors))

        # Log warnings
        for warning in warnings:
            logger.warning(f"Investment warning: {warning}")

        # Create investment
        investment = Investment(
            user_id=user_id,
            project_id=project_id,
            legal_entity_id=legal_entity_id,
            investment_amount=amount,
            payment_method=payment_method,
            notes=notes,
            status=InvestmentStatusEnum.PENDING,
        )
        self.db.add(investment)
        self.db.flush()  # Get ID

        # Create transaction record
        transaction = InvestmentTransaction(
            investment_id=investment.id,
            transaction_type="PAYMENT",
            amount=amount,
            status="pending",
            payment_method=payment_method,
            description=f"Investment payment for project {project_id}",
        )
        self.db.add(transaction)

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.INVEST,
            resource_type="investment",
            resource_id=investment.id,
            actor_user_id=user_id,
            new_values={"amount": amount, "project_id": project_id},
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Created investment {investment.id} for user {user_id}, project {project_id}, amount ${amount}")
        return investment

    def check_auto_investment_trigger(self) -> List[dict]:
        """
        Check and trigger automatic Club co-investments.
        
        Business Rules:
        - Cebollitas: >55% raised + 3 months -> Club contributes 45%
        - 1ra Div: >65% raised + 6 months -> Club contributes 35%
        - Senior: >75% raised + 9 months -> Club contributes 25%
        
        Returns:
            List of triggered co-investments
        """
        triggered_investments = []
        today = datetime.utcnow()

        # Get all active funding projects
        projects = (
            self.db.query(Project)
            .filter(
                Project.status == ProjectStatusEnum.FUNDING,
                Project.club_contribution_triggered == False,
            )
            .all()
        )

        for project in projects:
            # Check if project meets trigger conditions
            should_trigger, category, reason = self._evaluate_project_trigger(project, today)
            
            if should_trigger:
                try:
                    club_investment = self._trigger_club_contribution(project, category, reason)
                    triggered_investments.append({
                        "project_id": project.id,
                        "project_title": project.title,
                        "investment_id": club_investment.id,
                        "amount": club_investment.investment_amount,
                        "category": category.value,
                        "reason": reason,
                    })
                    logger.info(
                        f"Triggered Club co-investment for project {project.id}: "
                        f"${club_investment.investment_amount} ({category.value})"
                    )
                except Exception as e:
                    logger.error(f"Failed to trigger co-investment for project {project.id}: {e}")

        return triggered_investments

    def _evaluate_project_trigger(
        self,
        project: Project,
        today: datetime
    ) -> Tuple[bool, Optional[MembershipCategoryEnum], str]:
        """
        Evaluate if a project meets auto-investment trigger conditions.
        
        Returns:
            Tuple of (should_trigger, category, reason)
        """
        # Check funding percentage and determine category
        category = None
        min_percent = 0

        if project.raised_percent > InvestmentTiers.SENIOR_MIN_RAISED_PERCENT:
            category = MembershipCategoryEnum.SENIOR
            min_percent = InvestmentTiers.SENIOR_MIN_RAISED_PERCENT
        elif project.raised_percent > InvestmentTiers.PRIMERA_DIV_MIN_RAISED_PERCENT:
            category = MembershipCategoryEnum.PRIMERA_DIV
            min_percent = InvestmentTiers.PRIMERA_DIV_MIN_RAISED_PERCENT
        elif project.raised_percent > InvestmentTiers.CEBOLLITAS_MIN_RAISED_PERCENT:
            category = MembershipCategoryEnum.CEBOLLITAS
            min_percent = InvestmentTiers.CEBOLLITAS_MIN_RAISED_PERCENT

        if not category:
            return False, None, "Funding percentage below minimum threshold"

        # Check time requirement
        if not project.created_at:
            return False, None, "Project has no creation date"

        months_active = (today - project.created_at).days / 30
        min_months = self._get_minimum_months(category)

        if months_active < min_months:
            return False, None, f"Project active for {months_active:.1f} months, need {min_months}"

        # All conditions met
        reason = (
            f"Project reached {project.raised_percent:.1f}% raised "
            f"(>{min_percent}%) and active for {months_active:.1f} months (>{min_months})"
        )
        return True, category, reason

    def _get_minimum_months(self, category: MembershipCategoryEnum) -> int:
        """Get minimum months for category trigger."""
        months_map = {
            MembershipCategoryEnum.CEBOLLITAS: InvestmentTiers.CEBOLLITAS_MIN_MONTHS,
            MembershipCategoryEnum.PRIMERA_DIV: InvestmentTiers.PRIMERA_DIV_MIN_MONTHS,
            MembershipCategoryEnum.SENIOR: InvestmentTiers.SENIOR_MIN_MONTHS,
        }
        return months_map.get(category, 0)

    def _trigger_club_contribution(
        self,
        project: Project,
        category: MembershipCategoryEnum,
        reason: str,
    ) -> Investment:
        """
        Create Club co-investment for a project.
        """
        # Calculate contribution amount
        contribution_percent = self._get_club_contribution_percent(category)
        remaining_amount = project.target_amount - project.raised_amount
        club_amount = remaining_amount * (contribution_percent / 100)

        # Create investment record
        club_investment = Investment(
            user_id=1,  # Club user ID (system account)
            project_id=project.id,
            investment_amount=club_amount,
            currency="USD",
            status=InvestmentStatusEnum.CONFIRMED,
            is_club_contribution=True,
            club_contribution_trigger_reason=reason,
            payment_confirmed_at=datetime.utcnow(),
        )
        self.db.add(club_investment)
        self.db.flush()

        # Update project
        project.club_contribution_triggered = True
        project.club_contribution_triggered_at = datetime.utcnow()
        project.club_contribution_percent = contribution_percent
        project.club_contribution_amount = club_amount

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.INVEST,
            resource_type="investment",
            resource_id=club_investment.id,
            actor_user_id=1,  # System
            new_values={
                "amount": club_amount,
                "project_id": project.id,
                "is_club_contribution": True,
            },
            severity="INFO",
        )
        self.db.add(audit_entry)

        return club_investment

    def _get_club_contribution_percent(self, category: MembershipCategoryEnum) -> float:
        """Get Club contribution percentage for category."""
        percent_map = {
            MembershipCategoryEnum.CEBOLLITAS: InvestmentTiers.CEBOLLITAS_CLUB_CONTRIBUTION,
            MembershipCategoryEnum.PRIMERA_DIV: InvestmentTiers.PRIMERA_DIV_CLUB_CONTRIBUTION,
            MembershipCategoryEnum.SENIOR: InvestmentTiers.SENIOR_CLUB_CONTRIBUTION,
        }
        return percent_map.get(category, 0.0)
