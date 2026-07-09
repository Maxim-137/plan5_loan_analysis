"""Unit tests for src/salary/stochastic.py."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from salary.pathways import get_pathway
from salary.stochastic import (
    _annual_hazard_from_eventual_probability,
    simulate_stochastic_academic,
    simulate_stochastic_generic,
    simulate_stochastic_pathway,
)


def test_generic_shocks_are_unbiased_on_average():
    """With enough simulations, the mean trajectory should converge to the deterministic central trajectory."""
    sims = simulate_stochastic_generic("industry_data", n_simulations=20_000, total_years=10,
                                        sigma_annual=0.12, seed=42)
    central = get_pathway("industry_data", scenario="central", total_years=10)
    central_arr = np.array([y.sl_assessable_income for y in central])

    mean_sim = sims.mean(axis=0)
    relative_error = np.abs(mean_sim - central_arr) / central_arr
    assert np.all(relative_error < 0.02), f"Max relative error: {relative_error.max()}"


def test_output_shape_is_correct():
    sims = simulate_stochastic_pathway("industry_quant", n_simulations=500, total_years=20, seed=1)
    assert sims.shape == (500, 20)


def test_hazard_rate_reproduces_target_eventual_probability():
    """Sanity-check the geometric hazard-rate algebra directly."""
    target = 0.20
    window = 15
    hazard = _annual_hazard_from_eventual_probability(target, window)
    never_converts_prob = (1 - hazard) ** window
    eventual_prob = 1 - never_converts_prob
    assert abs(eventual_prob - target) < 1e-9


def test_academic_conversion_rate_matches_target_probability():
    """Across many simulated academic careers, roughly 20% should ever reach the permanent track."""
    n_sims = 20_000
    sims = simulate_stochastic_academic(
        n_simulations=n_sims, total_years=40, sigma_annual=0.0, sigma_persistent=0.0,  # zero noise, so tracks are unambiguous
        permanent_position_probability=0.20, conversion_window_years=15, seed=7
    )

    # With zero noise, anyone who never converts has a value at year 39
    # EXACTLY equal to the "never converts" track's year-39 income; anyone
    # who converted (at any point, even very late) will differ from it, even
    # if only slightly (their post-conversion income may not have ramped up
    # much yet). An exact-match test is therefore precise here, unlike a
    # naive midpoint-threshold classifier, which misclassifies late
    # converters whose post-conversion salary hasn't ramped up far above the
    # "never converts" trajectory yet -- which is exactly what the first
    # version of this test got wrong (it reported ~17% instead of ~20%).
    never_track = get_pathway("academic", scenario="low", total_years=40)
    never_income_at_year_39 = never_track[39].sl_assessable_income

    converted_fraction = (np.abs(sims[:, 39] - never_income_at_year_39) > 1e-6).mean()
    assert abs(converted_fraction - 0.20) < 0.02, f"Got {converted_fraction}, expected ~0.20"


def test_academic_phd_years_are_never_sl_assessable():
    sims = simulate_stochastic_academic(n_simulations=200, total_years=40, sigma_annual=0.12, seed=3)
    assert np.all(sims[:, 0:4] == 0.0)


def test_persistent_factor_creates_genuine_long_run_dispersion():
    """
    Regression test for the bug this was built to fix: without a
    persistent per-career factor, every simulation just jitters around
    the same central trajectory and year-39 outcomes barely differ
    between simulations. With it, there should be real spread.
    """
    sims = simulate_stochastic_generic("industry_data", n_simulations=2000, total_years=40, seed=5)
    year_39_values = sims[:, 39]
    coefficient_of_variation = year_39_values.std() / year_39_values.mean()
    assert coefficient_of_variation > 0.15, f"CoV was only {coefficient_of_variation}, expected genuine dispersion"


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
