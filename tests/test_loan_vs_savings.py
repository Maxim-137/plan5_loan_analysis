"""Unit tests for src/decision/loan_vs_savings.py."""

import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from decision.loan_vs_savings import (
    balances_at_first_repayment,
    foregone_growth,
    marginal_repayment_cost,
)


def test_balance_difference_roughly_equals_grown_maintenance_loan():
    """
    The gap between 'with' and 'without' year-4 maintenance loan balances
    should be roughly the maintenance loan amount, grown at Plan 5 rates
    from its (termly) disbursement dates to the first repayment date --
    not exactly equal (it was paid in 3 instalments, each accruing
    interest for a different length of time), but in the right ballpark.
    """
    balance_with, balance_without, deferred_amount = balances_at_first_repayment()
    difference = balance_with - balance_without

    # Should exceed the raw amount (interest accrued) but not by a huge factor
    # over ~1.5 years at Plan 5 rates (a few percent, not double)
    assert deferred_amount < difference < deferred_amount * 1.15


def test_foregone_growth_zero_rate_gives_zero_growth():
    assert foregone_growth(1000.0, 0.0) == 0.0


def test_foregone_growth_matches_compound_interest_formula():
    amount = 5000.0
    rate = 0.05
    start = date(2027, 1, 10)
    end = date(2037, 1, 10)  # exactly 10 years later

    growth = foregone_growth(amount, rate, disbursement_date=start, horizon_end=end)
    expected = amount * (1.05 ** 10) - amount
    assert abs(growth - expected) < 1.0  # small tolerance for the 365.25-day-year approximation


def test_marginal_cost_near_zero_when_always_written_off():
    """
    If a pathway is (nearly) always written off regardless, the marginal
    extra repayment from borrowing a bit more should be small relative to
    the deferred amount itself, since a bigger balance that's still going
    to be written off doesn't generally cost much extra in repayments.
    """
    extra_repaid = marginal_repayment_cost("academic", n_sims=100, seed=99)
    _, _, deferred_amount = balances_at_first_repayment()

    # Extra repaid should be small relative to what it would cost if fully
    # repaid with interest (a generous upper bound check, not a tight one)
    assert np.median(extra_repaid) < deferred_amount * 0.5


def test_marginal_cost_paired_comparison_is_never_negative():
    """Borrowing MORE should never result in repaying LESS, for any single paired draw."""
    for pathway in ["academic", "industry_data", "industry_quant"]:
        extra_repaid = marginal_repayment_cost(pathway, n_sims=50, seed=5)
        assert np.all(extra_repaid >= -0.01), f"{pathway} had a negative marginal repayment"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
