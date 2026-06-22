"""
Reconstructs the actual Plan 5 loan balance to date, using the real
tuition fee cap and (estimated pre-2026/27) maintenance loan minimum for
each academic year, and the real Plan 5 interest rate history.

Personal assumptions (see docs/assumptions_and_sources.md for the
underlying loan/fee/rate figures):
  - Course: 4-year MPhys, started September 2023 (first Plan 5 cohort)
  - Full tuition fee loan taken every year
  - Minimum (household-income-capped) maintenance loan taken in years 1-3
  - Year 4 (2026/27): this script assumes the maintenance loan IS taken,
    as a baseline "if you borrow as usual" figure. The loan-vs-savings
    comparison for year 4 is a separate module (see
    src/decision/loan_vs_savings.py, once savings figures are supplied).
"""

import _pathfix  # noqa: F401

from plan5.fees import maintenance_loan_minimum, tuition_fee_cap
from plan5.loan import generate_year_disbursements, simulate_balance
from datetime import date

COURSE_START_YEAR = 2023  # September 2023 intake
COURSE_LENGTH_YEARS = 4   # 4-year MPhys
AS_OF_DATE = date(2026, 7, 17)  # "today"


def academic_year_label(start_year):
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def build_disbursements(as_of_date=AS_OF_DATE):
    """Builds the real disbursement history for all years that have started by as_of_date."""
    disbursements = []
    for i in range(COURSE_LENGTH_YEARS):
        start_year = COURSE_START_YEAR + i
        label = academic_year_label(start_year)

        # Only include years that have actually started by as_of_date
        if date(start_year, 9, 25) > as_of_date:
            break

        tuition = tuition_fee_cap(label)
        maintenance = maintenance_loan_minimum(label)
        disbursements += generate_year_disbursements(start_year, tuition, maintenance, label=label)

    return disbursements


def main():
    disbursements = build_disbursements()

    print("=" * 72)
    print("DISBURSEMENT HISTORY USED")
    print("=" * 72)
    running_total = 0.0
    for d in disbursements:
        running_total += d.amount
        print(f"{d.disbursement_date}  £{d.amount:9,.2f}   {d.description}")
    print(f"\nTotal disbursed to date (principal only, no interest): £{running_total:,.2f}")

    history, summary = simulate_balance(disbursements, AS_OF_DATE)

    print("\n" + "=" * 72)
    print(f"BALANCE RECONSTRUCTION AS OF {AS_OF_DATE}")
    print("=" * 72)
    print(f"Total borrowed (principal):     £{summary['total_borrowed']:,.2f}")
    print(f"Total interest accrued to date: £{summary['total_interest_accrued']:,.2f}")
    print(f"Estimated current balance:      £{summary['final_balance']:,.2f}")

    # A handful of milestone balances along the way, for a sanity-check trajectory
    print("\nBalance at end of each academic year so far:")
    milestone_dates = [date(COURSE_START_YEAR + i + 1, 8, 31) for i in range(COURSE_LENGTH_YEARS)]
    history_dict = dict(history)
    for md in milestone_dates:
        if md in history_dict:
            print(f"  {md}: £{history_dict[md]:,.2f}")

    return history, summary


if __name__ == "__main__":
    main()
