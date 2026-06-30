"""Unit tests for src/plan5/repayment.py."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from plan5.repayment import simulate_repayment, threshold_on
from plan5.rates import RatePeriod
from salary.pathways import YearIncome


FLAT_2PCT = [RatePeriod(date(2020, 1, 1), date(2099, 1, 1), 0.02, "test", "confirmed", "")]


def test_zero_income_forever_means_full_writeoff_no_repayment():
    """Someone who never earns anything should repay nothing, and get written off at exactly max_years."""
    zero_income_path = [YearIncome(y, 0.0, 0.0, "unemployed") for y in range(41)]
    result = simulate_repayment(10_000.0, date(2028, 4, 6), zero_income_path,
                                 max_years=40, periods=FLAT_2PCT)

    assert result["total_repaid"] == 0.0
    assert result["written_off"] is True
    # Balance should be close to 10000 * (1.02)^40 (allowing for daily-compounding vs annual approx)
    expected_approx = 10_000 * (1.02 ** 40)
    assert abs(result["final_balance"] - expected_approx) / expected_approx < 0.01


def test_very_high_income_repays_well_before_writeoff():
    """Someone earning far above the threshold should clear a modest balance quickly."""
    high_income_path = [YearIncome(y, 500_000.0, 500_000.0, "high earner") for y in range(41)]
    result = simulate_repayment(5_000.0, date(2028, 4, 6), high_income_path,
                                 max_years=40, periods=FLAT_2PCT)

    assert result["written_off"] is False
    assert result["final_balance"] == 0.0
    assert result["years_elapsed"] < 2.0  # should clear a small balance within ~a year or two
    assert result["total_repaid"] >= 5_000.0  # repaid at least the starting balance (plus some interest)


def test_income_exactly_at_threshold_triggers_no_repayment():
    """Income exactly at (not above) the threshold should trigger zero repayment."""
    at_threshold_path = [YearIncome(y, 25_000.0, 25_000.0, "at threshold") for y in range(41)]
    result = simulate_repayment(1_000.0, date(2026, 6, 1), at_threshold_path,
                                 max_years=1, periods=FLAT_2PCT)
    assert result["total_repaid"] == 0.0


def test_income_above_threshold_matches_hand_calculation():
    """A simple one-month hand-calculation check on the 9% repayment formula."""
    # £37,000/year is £12,000/year above the frozen £25,000 threshold (pre-2027)
    # -> annual repayment amount would be 9% of £12,000 = £1,080/year = £90/month
    path = [YearIncome(y, 37_000.0, 37_000.0, "test") for y in range(41)]
    result = simulate_repayment(100_000.0, date(2026, 6, 6), path, max_years=1)

    first_repayment = result["monthly_records"][0][2]
    expected_monthly_repayment = 0.09 * (37_000 - 25_000) / 12
    assert abs(first_repayment - expected_monthly_repayment) < 0.01


def test_threshold_frozen_before_2027_then_uprates():
    periods = [
        RatePeriod(date(2025, 9, 1), date(2026, 8, 31), 0.032, "RPI_only", "confirmed", ""),
        RatePeriod(date(2026, 9, 1), date(2099, 1, 1), 0.03, "assumption", "assumption", ""),
    ]
    assert threshold_on(date(2026, 1, 1), periods=periods) == 25_000.0
    assert threshold_on(date(2027, 1, 1), periods=periods) == 25_000.0  # still frozen (before 6 Apr 2027)
    after = threshold_on(date(2027, 6, 1), periods=periods)
    assert after > 25_000.0  # should have uprated once by now


def test_repayment_never_exceeds_remaining_balance():
    """A huge income against a tiny balance shouldn't cause negative balances."""
    path = [YearIncome(y, 1_000_000.0, 1_000_000.0, "huge") for y in range(41)]
    result = simulate_repayment(10.0, date(2026, 6, 6), path, max_years=1)
    assert result["final_balance"] == 0.0
    assert result["total_repaid"] < 1000  # shouldn't repay wildly more than the tiny starting balance + interest


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
