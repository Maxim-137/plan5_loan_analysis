"""
Core Plan 5 loan balance simulation.

Simulates the day-by-day balance of a Plan 5 loan: interest is compounded
daily (annual rate / days in year, applied to the current balance each
day), matching how the Student Loans Company actually accrues interest,
rather than approximating with simple annual compounding. Disbursements
(tuition fee loan and maintenance loan payments) are added to the balance
on the day they land.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from .rates import load_rate_history, rate_on


@dataclass(frozen=True)
class Disbursement:
    disbursement_date: date
    amount: float
    description: str = ""


def academic_year_instalment_dates(start_year):
    """
    Approximate Student Finance England instalment dates for an academic
    year starting in September of `start_year`: three roughly-equal
    instalments at the start of each term. SFE's real split is close to,
    but not exactly, even thirds -- this is a reasonable modelling
    approximation, flagged here rather than silently assumed.
    """
    return [
        date(start_year, 9, 25),
        date(start_year + 1, 1, 10),
        date(start_year + 1, 4, 10),
    ]


def generate_year_disbursements(start_year, tuition_amount, maintenance_amount, label=None):
    """
    Splits one academic year's tuition fee loan and maintenance loan into
    three termly instalments each, landing on the dates from
    academic_year_instalment_dates.
    """
    label = label or f"{start_year}/{str(start_year + 1)[-2:]}"
    dates = academic_year_instalment_dates(start_year)

    disbursements = []
    for d in dates:
        if tuition_amount:
            disbursements.append(Disbursement(d, tuition_amount / 3, f"{label} tuition fee loan instalment"))
        if maintenance_amount:
            disbursements.append(Disbursement(d, maintenance_amount / 3, f"{label} maintenance loan instalment"))
    return disbursements


def _days_in_year(year):
    return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365


def simulate_balance(
    disbursements,
    as_of_date,
    periods=None,
    forward_rate_override=None,
    start_balance=0.0,
    start_date=None,
):
    """
    Day-by-day simulation of the loan balance from `start_date` (or the
    first disbursement date if not given) up to and including `as_of_date`.

    Returns a list of (date, balance) tuples, one per day, plus a summary
    dict with total_borrowed and total_interest_accrued.
    """
    periods = periods if periods is not None else load_rate_history()
    disbursements = sorted(disbursements, key=lambda d: d.disbursement_date)

    if not disbursements and start_date is None:
        raise ValueError("Need at least one disbursement, or an explicit start_date.")

    current_date = start_date or disbursements[0].disbursement_date
    balance = start_balance
    total_borrowed = start_balance
    total_interest = 0.0

    disbursement_idx = 0
    history = []

    while current_date <= as_of_date:
        # Add any disbursements landing today, before today's interest accrues
        # (matches SLC convention: interest accrues on the balance including
        # the instalment paid that day).
        while (
            disbursement_idx < len(disbursements)
            and disbursements[disbursement_idx].disbursement_date == current_date
        ):
            amount = disbursements[disbursement_idx].amount
            balance += amount
            total_borrowed += amount
            disbursement_idx += 1

        annual_rate = rate_on(current_date, periods=periods, forward_rate_override=forward_rate_override)
        daily_rate = annual_rate / _days_in_year(current_date.year)
        interest_today = balance * daily_rate
        balance += interest_today
        total_interest += interest_today

        history.append((current_date, balance))
        current_date += timedelta(days=1)

    summary = {
        "final_balance": balance,
        "total_borrowed": total_borrowed,
        "total_interest_accrued": total_interest,
        "as_of_date": as_of_date,
    }
    return history, summary
