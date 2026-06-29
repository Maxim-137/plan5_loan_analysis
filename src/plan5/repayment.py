"""
Plan 5 income-contingent repayment simulation.

Combines a starting loan balance with a salary pathway (see
src/salary/pathways.py) to simulate the loan from the first repayment
date onward: daily-compounded interest, monthly repayments of 9% of
income above the (RPI-uprated-from-2027) threshold, deducted via a
simplified "one deduction per calendar month" schedule. Stops either when
the balance reaches zero (repaid in full) or after `max_years` (written off).
"""

from datetime import date, timedelta

from .rates import load_rate_history, rate_on


def _days_in_year(year):
    return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365


def annual_income_for_date(query_date, repayment_start_date, salary_path):
    """Looks up the SL-assessable annual income applicable at query_date, given the salary path starts at repayment_start_date."""
    years_elapsed = (query_date - repayment_start_date).days / 365.25
    year_index = int(years_elapsed)
    year_index = max(0, min(year_index, len(salary_path) - 1))
    return salary_path[year_index].sl_assessable_income


def threshold_on(query_date, periods=None, forward_rate_override=None,
                  base_threshold=25_000.0, freeze_until=date(2027, 4, 6)):
    """
    Plan 5 repayment threshold: frozen at £25,000 until April 2027, then
    uprated each subsequent 6 April in line with RPI. We use the Plan 5
    loan's own interest rate as the RPI proxy for this uprating, since
    (outside the 2023-2025 Prevailing-Market-Rate-capped years, which
    predate the freeze end date anyway) that rate IS RPI directly.
    """
    if query_date < freeze_until:
        return base_threshold

    periods = periods if periods is not None else load_rate_history()
    threshold = base_threshold
    year = freeze_until.year

    while True:
        next_april = date(year + 1, 4, 6)
        if next_april > query_date:
            break
        rpi_proxy = rate_on(date(year, 9, 1), periods=periods, forward_rate_override=forward_rate_override)
        threshold *= (1 + rpi_proxy)
        year += 1

    return threshold


def simulate_repayment(
    starting_balance,
    start_date,
    salary_path,
    max_years=40,
    periods=None,
    forward_rate_override=None,
    repayment_day_of_month=6,
):
    """
    Simulates Plan 5 repayment from `starting_balance` at `start_date`.

    Returns a summary dict: final_balance, total_repaid,
    total_interest_in_repayment, written_off (bool), years_elapsed, and
    monthly_records (a list of (date, annual_income, repayment, balance)).
    """
    periods = periods if periods is not None else load_rate_history()

    balance = starting_balance
    current_date = start_date
    end_date = start_date + timedelta(days=int(max_years * 365.25))

    total_repaid = 0.0
    total_interest = 0.0
    monthly_records = []

    while current_date < end_date and balance > 0:
        annual_rate = rate_on(current_date, periods=periods, forward_rate_override=forward_rate_override)
        daily_rate = annual_rate / _days_in_year(current_date.year)
        interest_today = balance * daily_rate
        balance += interest_today
        total_interest += interest_today

        if current_date.day == repayment_day_of_month:
            annual_income = annual_income_for_date(current_date, start_date, salary_path)
            threshold = threshold_on(current_date, periods=periods, forward_rate_override=forward_rate_override)

            monthly_income = annual_income / 12.0
            monthly_threshold = threshold / 12.0
            repayment = 0.09 * max(0.0, monthly_income - monthly_threshold)
            repayment = min(repayment, balance)

            balance -= repayment
            total_repaid += repayment
            monthly_records.append((current_date, annual_income, repayment, balance))

        current_date += timedelta(days=1)

    written_off = balance > 0.005  # small tolerance for floating point
    years_elapsed = (current_date - start_date).days / 365.25

    return {
        "final_balance": max(balance, 0.0),
        "total_repaid": total_repaid,
        "total_interest_in_repayment": total_interest,
        "written_off": written_off,
        "years_elapsed": years_elapsed,
        "monthly_records": monthly_records,
    }
