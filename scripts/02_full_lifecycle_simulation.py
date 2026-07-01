"""
Full Plan 5 lifecycle simulation: real disbursement history (years 1-4)
-> interest-only accrual through to the first repayment date -> income-
contingent repayment simulated against each career pathway/scenario.

This answers the actual central question: under realistic career
outcomes, does this loan get repaid in full, or written off after 40
years -- and what does that mean for its real cost?

Baseline assumption for year 4 (2026/27): the maintenance loan IS taken
(same as previous years). This is the "if you borrow as usual" baseline;
the specific loan-vs-savings comparison for year 4 is a separate module
(src/decision/loan_vs_savings.py, once savings figures are available).
"""

import _pathfix  # noqa: F401

from datetime import date

from plan5.fees import maintenance_loan_minimum, tuition_fee_cap
from plan5.loan import generate_year_disbursements, simulate_balance
from plan5.repayment import simulate_repayment
from salary.pathways import get_pathway

COURSE_START_YEAR = 2023
COURSE_LENGTH_YEARS = 4
FIRST_REPAYMENT_DATE = date(2028, 4, 6)  # "the April after leaving the course" (graduates summer 2027)

PATHWAY_NAMES = ["academic", "industry_data", "industry_quant"]
SCENARIOS = ["low", "central", "high"]


def academic_year_label(start_year):
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def build_full_course_disbursements():
    """All 4 years of tuition + maintenance loan disbursements (baseline: maintenance taken every year)."""
    disbursements = []
    for i in range(COURSE_LENGTH_YEARS):
        start_year = COURSE_START_YEAR + i
        label = academic_year_label(start_year)
        tuition = tuition_fee_cap(label)
        maintenance = maintenance_loan_minimum(label)
        disbursements += generate_year_disbursements(start_year, tuition, maintenance, label=label)
    return disbursements


def balance_at_first_repayment():
    """Grows the full disbursement history forward (interest only, no repayments) to FIRST_REPAYMENT_DATE."""
    disbursements = build_full_course_disbursements()
    _, summary = simulate_balance(disbursements, FIRST_REPAYMENT_DATE)
    return summary


def run_all_scenarios(starting_balance):
    results = {}
    for pathway_name in PATHWAY_NAMES:
        for scenario in SCENARIOS:
            salary_path = get_pathway(pathway_name, scenario=scenario, total_years=40)
            result = simulate_repayment(starting_balance, FIRST_REPAYMENT_DATE, salary_path, max_years=40)
            results[(pathway_name, scenario)] = result
    return results


def main():
    pre_repayment_summary = balance_at_first_repayment()
    starting_balance = pre_repayment_summary["final_balance"]

    print("=" * 78)
    print("BALANCE AT FIRST REPAYMENT DATE (assuming year 4 maintenance loan taken)")
    print("=" * 78)
    print(f"First repayment date:            {FIRST_REPAYMENT_DATE}")
    print(f"Total borrowed over 4 years:      £{pre_repayment_summary['total_borrowed']:,.2f}")
    print(f"Interest accrued before repayment starts: £{pre_repayment_summary['total_interest_accrued']:,.2f}")
    print(f"Balance when repayment begins:    £{starting_balance:,.2f}")

    results = run_all_scenarios(starting_balance)

    print("\n" + "=" * 78)
    print("REPAYMENT OUTCOMES BY CAREER PATHWAY AND SCENARIO")
    print("=" * 78)
    header = f"{'Pathway':16s} {'Scenario':9s} {'Total repaid':>14s} {'Years':>7s} {'Outcome':>14s}"
    print(header)
    print("-" * len(header))

    for pathway_name in PATHWAY_NAMES:
        for scenario in SCENARIOS:
            r = results[(pathway_name, scenario)]
            outcome = "WRITTEN OFF" if r["written_off"] else "repaid in full"
            print(
                f"{pathway_name:16s} {scenario:9s} "
                f"£{r['total_repaid']:>12,.0f} {r['years_elapsed']:>6.1f}y {outcome:>14s}"
            )

    print("\nNote: 'Total repaid' is the actual cash paid via repayments -- this is")
    print("the real, comparable measure of what the loan cost, regardless of the")
    print("headline amount borrowed or the balance at write-off (which is never")
    print("actually paid if written off).")

    return starting_balance, results


if __name__ == "__main__":
    main()
