"""
Year 4 maintenance loan vs savings: marginal decision analysis.

Key insight (see README/session notes): because Plan 5 repayment amount
depends only on income above the threshold -- not on the loan balance,
as long as the balance stays above zero -- the marginal cost of borrowing
an extra amount now is NOT simply "that amount at the Plan 5 interest
rate". It's whatever EXTRA the borrower actually ends up repaying over
their lifetime as a direct result of having borrowed it, which depends
on their career pathway (see scripts/03_monte_carlo_repayment.py).

This module computes that marginal extra-repayment distribution via a
PAIRED Monte Carlo comparison (the same simulated salary draw is used for
both the "with this year's maintenance loan" and "without it" balances,
so the difference isolates the marginal effect rather than adding fresh
simulation noise), and compares it against the foregone growth of that
same amount if it had been left invested/saved instead.
"""

from datetime import date

import numpy as np

from plan5.fees import maintenance_loan_minimum, tuition_fee_cap
from plan5.loan import generate_year_disbursements, simulate_balance
from plan5.repayment import simulate_repayment
from salary.pathways import YearIncome
from salary.stochastic import simulate_stochastic_pathway

COURSE_START_YEAR = 2023
COURSE_LENGTH_YEARS = 4
YEAR_4_LABEL = "2026/27"
FIRST_REPAYMENT_DATE = date(2028, 4, 6)
WRITE_OFF_DATE = date(2068, 4, 6)  # 40 years after first repayment


def academic_year_label(start_year):
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def _build_disbursements(include_year4_maintenance):
    disbursements = []
    for i in range(COURSE_LENGTH_YEARS):
        start_year = COURSE_START_YEAR + i
        label = academic_year_label(start_year)
        tuition = tuition_fee_cap(label)

        is_year4 = (label == YEAR_4_LABEL)
        if is_year4 and not include_year4_maintenance:
            maintenance = 0.0
        else:
            maintenance = maintenance_loan_minimum(label)

        disbursements += generate_year_disbursements(start_year, tuition, maintenance, label=label)
    return disbursements


def balances_at_first_repayment():
    """Returns (balance_with_year4_maintenance, balance_without_year4_maintenance, deferred_amount)."""
    with_disb = _build_disbursements(include_year4_maintenance=True)
    without_disb = _build_disbursements(include_year4_maintenance=False)

    _, summary_with = simulate_balance(with_disb, FIRST_REPAYMENT_DATE)
    _, summary_without = simulate_balance(without_disb, FIRST_REPAYMENT_DATE)

    deferred_amount = maintenance_loan_minimum(YEAR_4_LABEL)
    return summary_with["final_balance"], summary_without["final_balance"], deferred_amount


def marginal_repayment_cost(pathway_name, n_sims=300, seed=1):
    """
    Paired Monte Carlo: for each simulated salary draw, computes total
    repaid under both the 'with year-4 maintenance loan' and 'without it'
    starting balances, using the SAME salary draw for both so the
    difference isolates the marginal effect of the extra borrowing.

    Returns an ndarray of length n_sims: extra amount repaid (with minus
    without) for each simulated career.
    """
    balance_with, balance_without, _ = balances_at_first_repayment()
    salary_sims = simulate_stochastic_pathway(pathway_name, n_simulations=n_sims, total_years=40, seed=seed)

    extra_repaid = np.empty(n_sims)
    for i in range(n_sims):
        income_path = [YearIncome(y, salary_sims[i, y], salary_sims[i, y], "") for y in range(40)]

        result_with = simulate_repayment(balance_with, FIRST_REPAYMENT_DATE, income_path, max_years=40)
        result_without = simulate_repayment(balance_without, FIRST_REPAYMENT_DATE, income_path, max_years=40)

        extra_repaid[i] = result_with["total_repaid"] - result_without["total_repaid"]

    return extra_repaid


def foregone_growth(deferred_amount, annual_return_rate, disbursement_date=date(2027, 1, 10),
                     horizon_end=WRITE_OFF_DATE):
    """
    Compound growth (simple annual compounding) of `deferred_amount` from
    `disbursement_date` (approximated as the middle of the three year-4
    instalments) to `horizon_end`, at `annual_return_rate`. Returns the
    growth ABOVE the original amount (i.e. final value minus principal),
    for direct comparison against the marginal extra repayment.
    """
    years = (horizon_end - disbursement_date).days / 365.25
    final_value = deferred_amount * (1 + annual_return_rate) ** years
    return final_value - deferred_amount


def compare_pathway(pathway_name, return_rates=(0.0, 0.02, 0.04, 0.06, 0.08), n_sims=300, seed=1):
    """
    Full comparison for one pathway: marginal extra-repayment distribution
    (from taking the loan) vs foregone growth (from using savings instead)
    at several assumed return rates.
    """
    extra_repaid = marginal_repayment_cost(pathway_name, n_sims=n_sims, seed=seed)
    _, _, deferred_amount = balances_at_first_repayment()

    growth_by_rate = {
        rate: foregone_growth(deferred_amount, rate) for rate in return_rates
    }

    return {
        "deferred_amount": deferred_amount,
        "extra_repaid_mean": extra_repaid.mean(),
        "extra_repaid_median": np.median(extra_repaid),
        "extra_repaid_p10": np.percentile(extra_repaid, 10),
        "extra_repaid_p90": np.percentile(extra_repaid, 90),
        "growth_by_rate": growth_by_rate,
    }
