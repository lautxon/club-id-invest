"""
Scheduled Celery Tasks
Periodic jobs for Club ID Invest platform.
"""

from celery import current_app
import logging
from datetime import datetime
from typing import Dict

from app.core.database import SessionLocal
from app.services.investment_service import InvestmentService
from app.services.membership_service import MembershipService
from app.services.contract_service import ContractService
from app.models.projects import Project
from app.models.investments import Investment, InvestmentStatusEnum

logger = logging.getLogger(__name__)


@current_app.task(bind=True, max_retries=3)
def run_auto_investment_check(self) -> Dict:
    """
    Daily task to check and trigger automatic Club co-investments.
    
    Business Rules:
    - Cebollitas: >55% raised + 3 months -> Club contributes 45%
    - 1ra Div: >65% raised + 6 months -> Club contributes 35%
    - Senior: >75% raised + 9 months -> Club contributes 25%
    
    Returns:
        Dict with results summary
    """
    db = SessionLocal()
    try:
        logger.info("Starting auto-investment check...")
        
        service = InvestmentService(db)
        triggered = service.check_auto_investment_trigger()
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "triggered_count": len(triggered),
            "triggered_investments": triggered,
        }
        
        logger.info(f"Auto-investment check complete: {len(triggered)} triggered")
        return result
        
    except Exception as e:
        logger.error(f"Auto-investment check failed: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry in 5 minutes
    finally:
        db.close()


@current_app.task(bind=True, max_retries=3)
def run_membership_lifecycle_check(self) -> Dict:
    """
    Daily task to manage membership lifecycle and inactivity penalties.
    
    Business Rules:
    - 60 days inactive -> Mark 'inactive', charge $50 penalty
    - 180 days inactive -> Mark 'churned'
    
    Returns:
        Dict with status change counts
    """
    db = SessionLocal()
    try:
        logger.info("Starting membership lifecycle check...")
        
        service = MembershipService(db)
        changes = service.manage_membership_lifecycle()
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "changes": changes,
        }
        
        logger.info(
            f"Membership lifecycle check complete: "
            f"{changes['marked_inactive']} inactive, "
            f"{changes['marked_churned']} churned"
        )
        return result
        
    except Exception as e:
        logger.error(f"Membership lifecycle check failed: {e}")
        raise self.retry(exc=e, countdown=300)
    finally:
        db.close()


@current_app.task(bind=True, max_retries=2)
def send_contract_reminders(self) -> Dict:
    """
    Send reminders for pending contracts.
    Runs every 6 hours.
    
    Returns:
        Dict with reminder count
    """
    db = SessionLocal()
    try:
        logger.info("Sending contract reminders...")
        
        service = ContractService(db)
        pending_contracts = service.get_pending_contracts()
        
        reminders_sent = 0
        for contract in pending_contracts:
            # TODO: Implement actual email/notification sending
            # For now, just log
            logger.info(
                f"Would send reminder for contract {contract.contract_number} "
                f"(pending since {contract.sent_at})"
            )
            reminders_sent += 1
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "reminders_sent": reminders_sent,
            "pending_count": len(pending_contracts),
        }
        
        logger.info(f"Contract reminders complete: {reminders_sent} sent")
        return result
        
    except Exception as e:
        logger.error(f"Contract reminders failed: {e}")
        raise self.retry(exc=e, countdown=600)
    finally:
        db.close()


@current_app.task(bind=True, max_retries=3)
def update_funding_progress(self) -> Dict:
    """
    Update funding progress for all active projects.
    Runs hourly.
    
    Returns:
        Dict with update summary
    """
    db = SessionLocal()
    try:
        logger.info("Updating funding progress...")
        
        # Get all funding projects
        projects = db.query(Project).filter(
            Project.status.in_(["funding", "funded"])
        ).all()
        
        updated_count = 0
        for project in projects:
            # Calculate totals from investments
            investments = db.query(Investment).filter(
                Investment.project_id == project.id,
                Investment.status.in_([
                    InvestmentStatusEnum.CONFIRMED,
                    InvestmentStatusEnum.ACTIVE,
                ])
            ).all()
            
            total_raised = sum(inv.investment_amount for inv in investments)
            investor_count = len(set(inv.user_id for inv in investments))
            
            # Update project
            old_raised = project.raised_amount
            project.raised_amount = total_raised
            project.raised_percent = (total_raised / project.target_amount * 100) if project.target_amount > 0 else 0
            project.investor_count = investor_count
            
            if old_raised != total_raised:
                updated_count += 1
            
            # Auto-mark as funded if 100%
            if project.raised_percent >= 100 and project.status == "funding":
                project.status = "funded"
                logger.info(f"Project {project.id} fully funded!")
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "projects_checked": len(projects),
            "projects_updated": updated_count,
        }
        
        logger.info(f"Funding progress update complete: {updated_count} updated")
        return result
        
    except Exception as e:
        logger.error(f"Funding progress update failed: {e}")
        raise self.retry(exc=e, countdown=180)
    finally:
        db.close()


@current_app.task(bind=True, max_retries=2)
def generate_monthly_reports(self) -> Dict:
    """
    Generate monthly investment reports.
    Runs on the 1st of each month.
    
    Returns:
        Dict with report generation summary
    """
    db = SessionLocal()
    try:
        logger.info("Generating monthly reports...")
        
        # TODO: Implement monthly report generation
        # - Total investments by category
        # - Club co-investment summary
        # - Active projects status
        # - Membership statistics
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "not_implemented",
        }
        
        logger.info("Monthly reports generation complete")
        return result
        
    except Exception as e:
        logger.error(f"Monthly reports generation failed: {e}")
        raise self.retry(exc=e, countdown=600)
    finally:
        db.close()


# =============================================================================
# MANUAL TRIGGER TASKS (Can be called via API)
# =============================================================================

@current_app.task
def process_investment_payment(investment_id: int) -> Dict:
    """
    Process payment for a pending investment.
    Can be triggered manually or via webhook.
    
    Args:
        investment_id: ID of the investment to process
    
    Returns:
        Dict with processing result
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing payment for investment {investment_id}...")
        
        investment = db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment:
            return {"success": False, "error": "Investment not found"}
        
        if investment.status != InvestmentStatusEnum.PENDING:
            return {"success": False, "error": f"Investment is {investment.status.value}"}
        
        # TODO: Implement actual payment processing
        # - Verify payment with payment gateway
        # - Update transaction status
        
        # For now, just confirm the investment
        investment.status = InvestmentStatusEnum.CONFIRMED
        investment.payment_confirmed_at = datetime.utcnow()
        investment.confirmed_at = datetime.utcnow()
        
        # Update membership statistics
        from app.models.memberships import Membership
        membership = db.query(Membership).filter(Membership.user_id == investment.user_id).first()
        if membership:
            membership.total_investments_count += 1
            membership.total_invested_amount += investment.investment_amount
            membership.active_investments_count += 1
            membership.last_activity_date = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Investment {investment_id} payment confirmed")
        return {
            "success": True,
            "investment_id": investment_id,
            "status": "confirmed",
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Payment processing failed for investment {investment_id}: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()
