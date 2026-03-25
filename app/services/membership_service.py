"""
Membership Service
Handles membership lifecycle, status transitions, and inactivity penalties.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from app.core.config import (
    MembershipRules,
    MembershipCategoryEnum,
    MembershipStatusEnum,
    AuditActionEnum,
)
from app.models.memberships import Membership
from app.models.audit_logs import AuditLog
from app.models.investments import Investment, InvestmentStatusEnum

logger = logging.getLogger(__name__)


class MembershipService:
    """
    Service for managing membership lifecycle.
    
    Business Rules:
    - 60 days inactive -> Mark 'inactive', charge $50 penalty
    - 180 days inactive -> Mark 'churned'
    """

    def __init__(self, db: Session):
        self.db = db

    def get_membership(self, user_id: int) -> Optional[Membership]:
        """Get active membership for a user."""
        return (
            self.db.query(Membership)
            .filter(Membership.user_id == user_id)
            .order_by(Membership.created_at.desc())
            .first()
        )

    def create_membership(
        self,
        user_id: int,
        category: MembershipCategoryEnum = MembershipCategoryEnum.CEBOLLITAS,
    ) -> Membership:
        """Create a new membership for a user."""
        membership = Membership(
            user_id=user_id,
            category=category,
            status=MembershipStatusEnum.ACTIVE,
            join_date=datetime.utcnow(),
            last_activity_date=datetime.utcnow(),
        )
        self.db.add(membership)
        
        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.CREATE,
            resource_type="membership",
            resource_id=membership.id,
            actor_user_id=user_id,
            new_values={"category": category.value},
            severity="INFO",
        )
        self.db.add(audit_entry)
        
        logger.info(f"Created membership {membership.id} for user {user_id}")
        return membership

    def update_activity(self, user_id: int) -> None:
        """Update last activity date for a membership."""
        membership = self.get_membership(user_id)
        if membership:
            membership.last_activity_date = datetime.utcnow()
            self.db.flush()

    def manage_membership_lifecycle(self) -> Dict[str, int]:
        """
        Check and update membership statuses based on inactivity.
        
        Business Rules:
        - 60 days inactive -> Mark 'inactive', charge $50 penalty
        - 180 days inactive -> Mark 'churned'
        
        Returns:
            Dict with counts of status changes
        """
        today = datetime.utcnow()
        changes = {
            "marked_inactive": 0,
            "marked_churned": 0,
            "penalties_applied": 0,
            "errors": 0,
        }

        # Get all active memberships
        active_memberships = (
            self.db.query(Membership)
            .filter(Membership.status == MembershipStatusEnum.ACTIVE)
            .all()
        )

        for membership in active_memberships:
            try:
                self._process_membership_lifecycle(membership, today, changes)
            except Exception as e:
                logger.error(f"Error processing membership {membership.id}: {e}")
                changes["errors"] += 1

        # Also check already inactive memberships for churn
        inactive_memberships = (
            self.db.query(Membership)
            .filter(Membership.status == MembershipStatusEnum.INACTIVE)
            .all()
        )

        for membership in inactive_memberships:
            try:
                self._check_churn_status(membership, today, changes)
            except Exception as e:
                logger.error(f"Error checking churn for membership {membership.id}: {e}")
                changes["errors"] += 1

        logger.info(
            f"Lifecycle check complete: {changes['marked_inactive']} inactive, "
            f"{changes['marked_churned']} churned, {changes['penalties_applied']} penalties"
        )
        return changes

    def _process_membership_lifecycle(
        self,
        membership: Membership,
        today: datetime,
        changes: Dict[str, int],
    ) -> None:
        """Process a single membership lifecycle."""
        if not membership.last_activity_date:
            return

        days_inactive = (today - membership.last_activity_date).days

        # Check for churn (180 days)
        if days_inactive >= MembershipRules.CHURN_THRESHOLD_DAYS:
            membership.status = MembershipStatusEnum.CHURNED
            changes["marked_churned"] += 1
            
            audit_entry = AuditLog.log_action(
                action=AuditActionEnum.STATUS_CHANGE,
                resource_type="membership",
                resource_id=membership.id,
                actor_user_id=None,  # System
                changes_summary=f"Auto-churned after {days_inactive} days of inactivity",
                severity="WARNING",
            )
            self.db.add(audit_entry)
            logger.info(f"Membership {membership.id} churned after {days_inactive} days")

        # Check for inactive (60 days)
        elif days_inactive >= MembershipRules.INACTIVITY_WARNING_DAYS:
            if membership.status != MembershipStatusEnum.INACTIVE:
                membership.status = MembershipStatusEnum.INACTIVE
                changes["marked_inactive"] += 1
                
                # Apply penalty
                self._apply_penalty(membership, changes)
                
                audit_entry = AuditLog.log_action(
                    action=AuditActionEnum.STATUS_CHANGE,
                    resource_type="membership",
                    resource_id=membership.id,
                    actor_user_id=None,  # System
                    changes_summary=f"Marked inactive after {days_inactive} days, penalty ${MembershipRules.INACTIVITY_PENALTY_AMOUNT} applied",
                    severity="WARNING",
                )
                self.db.add(audit_entry)
                logger.info(f"Membership {membership.id} marked inactive after {days_inactive} days")

    def _check_churn_status(
        self,
        membership: Membership,
        today: datetime,
        changes: Dict[str, int],
    ) -> None:
        """Check if inactive membership should be churned."""
        if not membership.last_activity_date:
            return

        days_inactive = (today - membership.last_activity_date).days

        if days_inactive >= MembershipRules.CHURN_THRESHOLD_DAYS:
            membership.status = MembershipStatusEnum.CHURNED
            changes["marked_churned"] += 1
            
            audit_entry = AuditLog.log_action(
                action=AuditActionEnum.STATUS_CHANGE,
                resource_type="membership",
                resource_id=membership.id,
                actor_user_id=None,
                changes_summary=f"Churned after {days_inactive} days of total inactivity",
                severity="WARNING",
            )
            self.db.add(audit_entry)
            logger.info(f"Inactive membership {membership.id} churned after {days_inactive} days")

    def _apply_penalty(
        self,
        membership: Membership,
        changes: Dict[str, int],
    ) -> None:
        """Apply inactivity penalty to membership."""
        penalty_amount = MembershipRules.INACTIVITY_PENALTY_AMOUNT
        
        membership.penalty_amount += penalty_amount
        membership.last_penalty_applied_at = datetime.utcnow()
        changes["penalties_applied"] += 1

        # Create penalty transaction
        from app.models.investments import InvestmentTransaction
        penalty_transaction = InvestmentTransaction(
            investment_id=None,  # No specific investment
            transaction_type="PENALTY",
            amount=penalty_amount,
            currency=MembershipRules.INACTIVITY_PENALTY_CURRENCY,
            status="pending",
            description=f"Inactivity penalty after {MembershipRules.INACTIVITY_WARNING_DAYS} days",
        )
        self.db.add(penalty_transaction)

        logger.info(f"Applied ${penalty_amount} penalty to membership {membership.id}")

    def reactivate_membership(
        self,
        user_id: int,
        pay_penalty: bool = False,
    ) -> Dict[str, any]:
        """
        Reactivate an inactive or churned membership.
        
        Returns:
            Dict with reactivation status and any required payment
        """
        membership = self.get_membership(user_id)
        
        if not membership:
            return {"success": False, "error": "No membership found"}

        if membership.status == MembershipStatusEnum.ACTIVE:
            return {"success": True, "message": "Membership already active"}

        # Check if penalty needs to be paid
        if membership.penalty_amount > 0 and not pay_penalty:
            return {
                "success": False,
                "requires_payment": True,
                "penalty_amount": membership.penalty_amount,
                "currency": MembershipRules.INACTIVITY_PENALTY_CURRENCY,
            }

        # Reactivate
        old_status = membership.status
        membership.status = MembershipStatusEnum.ACTIVE
        membership.last_activity_date = datetime.utcnow()
        
        if pay_penalty and membership.penalty_amount > 0:
            membership.penalty_amount = 0

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.STATUS_CHANGE,
            resource_type="membership",
            resource_id=membership.id,
            actor_user_id=user_id,
            old_values={"status": old_status.value},
            new_values={"status": MembershipStatusEnum.ACTIVE.value},
            changes_summary=f"Reactivated from {old_status.value}",
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Reactivated membership {membership.id} for user {user_id}")
        return {"success": True, "membership_id": membership.id}

    def upgrade_membership(
        self,
        user_id: int,
        new_category: MembershipCategoryEnum,
    ) -> Dict[str, any]:
        """Upgrade membership to a higher category."""
        membership = self.get_membership(user_id)
        
        if not membership:
            return {"success": False, "error": "No membership found"}

        old_category = membership.category
        membership.category = new_category
        membership.category_changed_at = datetime.utcnow()
        membership.previous_category = old_category.value

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.UPDATE,
            resource_type="membership",
            resource_id=membership.id,
            actor_user_id=user_id,
            old_values={"category": old_category.value},
            new_values={"category": new_category.value},
            changes_summary=f"Upgraded from {old_category.value} to {new_category.value}",
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Upgraded membership {membership.id} from {old_category.value} to {new_category.value}")
        return {"success": True, "membership_id": membership.id}

    def get_membership_statistics(self, user_id: int) -> Dict[str, any]:
        """Get membership statistics for a user."""
        membership = self.get_membership(user_id)
        
        if not membership:
            return None

        # Calculate days since last activity
        days_inactive = 0
        if membership.last_activity_date:
            days_inactive = (datetime.utcnow() - membership.last_activity_date).days

        # Get investment summary
        investment_stats = (
            self.db.query(
                func.count(Investment.id).label("total_count"),
                func.sum(Investment.investment_amount).label("total_amount"),
            )
            .filter(
                Investment.user_id == user_id,
                Investment.status == InvestmentStatusEnum.ACTIVE,
            )
            .first()
        )

        return {
            "membership_id": membership.id,
            "category": membership.category.value,
            "status": membership.status.value,
            "join_date": membership.join_date.isoformat(),
            "days_inactive": days_inactive,
            "penalty_amount": membership.penalty_amount,
            "active_investments": membership.active_investments_count,
            "total_invested": membership.total_invested_amount,
            "investment_stats": {
                "count": investment_stats.total_count or 0,
                "total_amount": float(investment_stats.total_amount or 0),
            } if investment_stats else {"count": 0, "total_amount": 0},
        }
