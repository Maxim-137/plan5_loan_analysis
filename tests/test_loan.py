"""
Unit tests for src/plan5/loan.py.

Run with: python -m pytest tests/ -v   (or just `python tests/test_loan.py`)
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from plan5.loan import Disbursement, simulate_balance
from plan5.rates import RatePeriod, rate_on


def test_daily_compounding_matches_analytical_formula():
    """One year of daily compounding at a flat rate should match (1+r/n)^n exactly."""
    flat = [RatePeriod(date(2021, 1, 1), date(2030, 1, 1), 0.05, "test", "confirmed", "")]
    disb = [Disbursement(date(2021, 1, 1), 10000.0, "test")]

    _, summary = simulate_balance(disb, date(2022, 1, 1), periods=flat)
    expected = 10000 * (1 + 0.05 / 365) ** 365

    assert abs(summary["final_balance"] - expected) < 1e-6, (
        f"Expected {expected}, got {summary['final_balance']}"
    )


def test_zero_rate_leaves_principal_unchanged():
    zero = [RatePeriod(date(2021, 1, 1), date(2030, 1, 1), 0.0, "test", "confirmed", "")]
    disb = [Disbursement(date(2021, 1, 1), 10000.0, "test")]

    _, summary = simulate_balance(disb, date(2023, 6, 1), periods=zero)
    assert summary["final_balance"] == 10000.0


def test_single_day_of_interest():
    period = [RatePeriod(date(2024, 1, 1), date(2024, 12, 31), 0.05, "test", "confirmed", "")]
    disb = [Disbursement(date(2024, 3, 1), 1000.0, "test")]

    _, summary = simulate_balance(disb, date(2024, 3, 2), periods=period)
    expected = 1000 * (1 + 0.05 / 366)  # 2024 is a leap year

    assert abs(summary["final_balance"] - expected) < 1e-9


def test_rate_lookup_picks_correct_period():
    periods = [
        RatePeriod(date(2023, 9, 1), date(2023, 11, 30), 0.073, "PMR_cap", "confirmed", ""),
        RatePeriod(date(2023, 12, 1), date(2024, 1, 31), 0.075, "PMR_cap", "confirmed", ""),
    ]
    assert rate_on(date(2023, 10, 15), periods=periods) == 0.073
    assert rate_on(date(2023, 12, 15), periods=periods) == 0.075


def test_forward_rate_override_only_affects_assumption_periods():
    periods = [
        RatePeriod(date(2025, 9, 1), date(2026, 8, 31), 0.032, "RPI_only", "confirmed", ""),
        RatePeriod(date(2027, 9, 1), date(2099, 1, 1), 0.030, "assumption", "assumption", ""),
    ]
    # Confirmed period should NOT be affected by the override
    assert rate_on(date(2026, 1, 1), periods=periods, forward_rate_override=0.055) == 0.032
    # Assumption period SHOULD be affected
    assert rate_on(date(2028, 1, 1), periods=periods, forward_rate_override=0.055) == 0.055


def test_multiple_disbursements_accumulate_principal_correctly():
    disb = [
        Disbursement(date(2023, 9, 25), 1000.0, "a"),
        Disbursement(date(2023, 9, 25), 500.0, "b"),
        Disbursement(date(2024, 1, 10), 700.0, "c"),
    ]
    zero = [RatePeriod(date(2023, 1, 1), date(2030, 1, 1), 0.0, "test", "confirmed", "")]
    _, summary = simulate_balance(disb, date(2024, 6, 1), periods=zero)
    assert summary["total_borrowed"] == 2200.0
    assert summary["final_balance"] == 2200.0  # zero rate, so balance == principal


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
