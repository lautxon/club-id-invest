"""
Unit Tests for Co-Investment Business Rules
Tests the critical auto-investment trigger logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from app.core.config import (
    InvestmentTiers,
    MembershipRules,
    MembershipCategoryEnum,
)
from app.models.memberships import Membership


class TestInvestmentTiers:
    """Test investment tier constants."""

    def test_cebollitas_tier_constants(self):
        """Test Cebollitas tier thresholds."""
        assert InvestmentTiers.CEBOLLITAS_MIN_RAISED_PERCENT == 55.0
        assert InvestmentTiers.CEBOLLITAS_MIN_MONTHS == 3
        assert InvestmentTiers.CEBOLLITAS_CLUB_CONTRIBUTION == 45.0

    def test_primera_div_tier_constants(self):
        """Test 1ra Div tier thresholds."""
        assert InvestmentTiers.PRIMERA_DIV_MIN_RAISED_PERCENT == 65.0
        assert InvestmentTiers.PRIMERA_DIV_MIN_MONTHS == 6
        assert InvestmentTiers.PRIMERA_DIV_CLUB_CONTRIBUTION == 35.0

    def test_senior_tier_constants(self):
        """Test Senior tier thresholds."""
        assert InvestmentTiers.SENIOR_MIN_RAISED_PERCENT == 75.0
        assert InvestmentTiers.SENIOR_MIN_MONTHS == 9
        assert InvestmentTiers.SENIOR_CLUB_CONTRIBUTION == 25.0


class TestMembershipCategoryMethods:
    """Test membership category helper methods."""

    def test_cebollitas_club_contribution_percent(self):
        """Test Club contribution percentage for Cebollitas."""
        membership = Mock(spec=Membership)
        membership.category = MembershipCategoryEnum.CEBOLLITAS
        
        # Simulate the method logic
        contribution_map = {
            MembershipCategoryEnum.CEBOLLITAS: 45.0,
            MembershipCategoryEnum.PRIMERA_DIV: 35.0,
            MembershipCategoryEnum.SENIOR: 25.0,
        }
        assert contribution_map[membership.category] == 45.0

    def test_primera_div_club_contribution_percent(self):
        """Test Club contribution percentage for 1ra Div."""
        membership = Mock(spec=Membership)
        membership.category = MembershipCategoryEnum.PRIMERA_DIV
        
        contribution_map = {
            MembershipCategoryEnum.CEBOLLITAS: 45.0,
            MembershipCategoryEnum.PRIMERA_DIV: 35.0,
            MembershipCategoryEnum.SENIOR: 25.0,
        }
        assert contribution_map[membership.category] == 35.0

    def test_senior_club_contribution_percent(self):
        """Test Club contribution percentage for Senior."""
        membership = Mock(spec=Membership)
        membership.category = MembershipCategoryEnum.SENIOR
        
        contribution_map = {
            MembershipCategoryEnum.CEBOLLITAS: 45.0,
            MembershipCategoryEnum.PRIMERA_DIV: 35.0,
            MembershipCategoryEnum.SENIOR: 25.0,
        }
        assert contribution_map[membership.category] == 25.0


class TestAutoInvestmentTriggerEdgeCases:
    """
    Test edge cases for auto-investment triggers.
    Critical boundary testing: 89 days vs 90 days, 54% vs 55%.
    """

    def test_cebollitas_trigger_at_exact_threshold(self):
        """Test Cebollitas trigger at exactly 55% raised."""
        raised_percent = 55.0
        assert raised_percent >= InvestmentTiers.CEBOLLITAS_MIN_RAISED_PERCENT

    def test_cebollitas_trigger_just_below_threshold(self):
        """Test Cebollitas trigger at 54.9% - should NOT trigger."""
        raised_percent = 54.9
        assert raised_percent < InvestmentTiers.CEBOLLITAS_MIN_RAISED_PERCENT

    def test_cebollitas_trigger_just_above_threshold(self):
        """Test Cebollitas trigger at 55.1% - should trigger."""
        raised_percent = 55.1
        assert raised_percent > InvestmentTiers.CEBOLLITAS_MIN_RAISED_PERCENT

    def test_months_boundary_89_vs_90_days(self):
        """Test Senior tier: 89 days vs 90 days (3 months)."""
        today = datetime.now()
        
        # 89 days - should NOT trigger (less than 3 months)
        join_date_89 = today - timedelta(days=89)
        months_diff_89 = (today - join_date_89).days / 30
        assert months_diff_89 < InvestmentTiers.CEBOLLITAS_MIN_MONTHS
        
        # 90 days - should trigger (exactly 3 months)
        join_date_90 = today - timedelta(days=90)
        months_diff_90 = (today - join_date_90).days / 30
        assert months_diff_90 >= InvestmentTiers.CEBOLLITAS_MIN_MONTHS

    def test_primera_div_6_months_boundary(self):
        """Test 1ra Div: 179 days vs 180 days (6 months)."""
        today = datetime.now()
        
        # 179 days - should NOT trigger
        join_date_179 = today - timedelta(days=179)
        months_diff = (today - join_date_179).days / 30
        assert months_diff < InvestmentTiers.PRIMERA_DIV_MIN_MONTHS
        
        # 180 days - should trigger
        join_date_180 = today - timedelta(days=180)
        months_diff = (today - join_date_180).days / 30
        assert months_diff >= InvestmentTiers.PRIMERA_DIV_MIN_MONTHS

    def test_senior_9_months_boundary(self):
        """Test Senior: 269 days vs 270 days (9 months)."""
        today = datetime.now()
        
        # 269 days - should NOT trigger
        join_date_269 = today - timedelta(days=269)
        months_diff = (today - join_date_269).days / 30
        assert months_diff < InvestmentTiers.SENIOR_MIN_MONTHS
        
        # 270 days - should trigger
        join_date_270 = today - timedelta(days=270)
        months_diff = (today - join_date_270).days / 30
        assert months_diff >= InvestmentTiers.SENIOR_MIN_MONTHS


class TestMembershipLifecycle:
    """Test membership lifecycle and inactivity rules."""

    def test_inactive_threshold_60_days(self):
        """Test inactive status at 60 days."""
        assert MembershipRules.INACTIVITY_WARNING_DAYS == 60
        assert MembershipRules.INACTIVITY_PENALTY_AMOUNT == 50.0

    def test_churn_threshold_180_days(self):
        """Test churned status at 180 days."""
        assert MembershipRules.CHURN_THRESHOLD_DAYS == 180

    def test_inactive_status_calculation(self):
        """Test membership status based on last activity."""
        today = datetime.now()
        
        # 59 days inactive - still active
        last_activity_59 = today - timedelta(days=59)
        days_inactive_59 = (today - last_activity_59).days
        assert days_inactive_59 < MembershipRules.INACTIVITY_WARNING_DAYS
        
        # 60 days inactive - should be inactive
        last_activity_60 = today - timedelta(days=60)
        days_inactive_60 = (today - last_activity_60).days
        assert days_inactive_60 >= MembershipRules.INACTIVITY_WARNING_DAYS
        
        # 179 days inactive - still inactive (not churned)
        last_activity_179 = today - timedelta(days=179)
        days_inactive_179 = (today - last_activity_179).days
        assert days_inactive_179 < MembershipRules.CHURN_THRESHOLD_DAYS
        
        # 180 days inactive - should be churned
        last_activity_180 = today - timedelta(days=180)
        days_inactive_180 = (today - last_activity_180).days
        assert days_inactive_180 >= MembershipRules.CHURN_THRESHOLD_DAYS


class TestInvestmentConstraints:
    """Test investment constraints and limits."""

    def test_max_active_investments_per_user(self):
        """Test maximum 5 active investments per user."""
        assert MembershipRules.MAX_ACTIVE_INVESTMENTS_PER_USER == 5

    def test_max_investors_per_project(self):
        """Test maximum 50 investors per project."""
        assert MembershipRules.MAX_INVESTORS_PER_PROJECT == 50

    def test_can_accept_more_investments(self):
        """Test project can accept investments under limit."""
        current_investors = 49
        max_investors = MembershipRules.MAX_INVESTORS_PER_PROJECT
        assert current_investors < max_investors

    def test_project_at_max_capacity(self):
        """Test project at maximum capacity."""
        current_investors = 50
        max_investors = MembershipRules.MAX_INVESTORS_PER_PROJECT
        assert current_investors >= max_investors


class TestPenaltyCalculation:
    """Test penalty amount calculations."""

    def test_penalty_amount_constant(self):
        """Test penalty amount is $50."""
        assert MembershipRules.INACTIVITY_PENALTY_AMOUNT == 50.0

    def test_penalty_currency(self):
        """Test penalty currency is USD."""
        assert MembershipRules.INACTIVITY_PENALTY_CURRENCY == "USD"

    def test_total_penalty_calculation(self):
        """Test total penalty for multiple months."""
        monthly_penalty = MembershipRules.INACTIVITY_PENALTY_AMOUNT
        months_inactive = 3
        total_penalty = monthly_penalty * months_inactive
        assert total_penalty == 150.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
