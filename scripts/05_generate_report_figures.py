"""
Generates the final report figure set for this project.

Figures:
  01 - Actual loan balance reconstruction, Sept 2023 to today
  02 - Repayment trajectories by career pathway (central scenario)
  03 - Monte Carlo distribution of total lifetime repayment, by pathway
  04 - Year-4 loan-vs-savings decision: net benefit heatmap

Usage: python scripts/05_generate_report_figures.py [--n-sims 800] [--n-sims-decision 400]
"""

import _pathfix  # noqa: F401

import argparse
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

from decision.loan_vs_savings import balances_at_first_repayment, compare_pathway
from plan5.fees import maintenance_loan_minimum, tuition_fee_cap
from plan5.loan import generate_year_disbursements, simulate_balance
from plan5.repayment import simulate_repayment
from reporting.plots import PATHWAY_COLOURS, PATHWAY_LABELS, format_gbp, savefig, set_report_style
from salary.pathways import YearIncome, get_pathway
from salary.stochastic import simulate_stochastic_pathway

COURSE_START_YEAR = 2023
COURSE_LENGTH_YEARS = 4
FIRST_REPAYMENT_DATE = date(2028, 4, 6)
TODAY = date(2026, 7, 17)
PATHWAY_NAMES = ["academic", "industry_data", "industry_quant"]
RETURN_RATES = (0.0, 0.02, 0.04, 0.06, 0.08)


def academic_year_label(start_year):
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def build_full_course_disbursements():
    disbursements = []
    for i in range(COURSE_LENGTH_YEARS):
        start_year = COURSE_START_YEAR + i
        label = academic_year_label(start_year)
        tuition = tuition_fee_cap(label)
        maintenance = maintenance_loan_minimum(label)
        disbursements += generate_year_disbursements(start_year, tuition, maintenance, label=label)
    return disbursements


# ---------------------------------------------------------------------------
# Figure 1: actual balance reconstruction to date
# ---------------------------------------------------------------------------

def figure_01_balance_reconstruction():
    disbursements = build_full_course_disbursements()
    history, summary = simulate_balance(disbursements, TODAY)

    dates = [d for d, _ in history]
    balances = [b for _, b in history]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(dates, balances, color=PATHWAY_COLOURS["academic"], linewidth=2.2)
    ax.fill_between(dates, balances, alpha=0.08, color=PATHWAY_COLOURS["academic"])

    for i in range(COURSE_LENGTH_YEARS):
        year_start = date(COURSE_START_YEAR + i, 9, 25)
        if year_start <= TODAY:
            ax.axvline(year_start, color="0.6", linewidth=0.8, linestyle="--", zorder=0)

    ax.yaxis.set_major_formatter(FuncFormatter(format_gbp))
    ax.set_ylabel("Loan balance")
    ax.set_title("Actual Plan 5 loan balance, September 2023 to today")
    ax.text(
        0.02, 0.95, f"Balance today: £{summary['final_balance']:,.0f}",
        transform=ax.transAxes, va="top", fontsize=10.5, fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="0.7", pad=4)
    )
    fig.autofmt_xdate()
    savefig(fig, "fig01_actual_balance_reconstruction")


# ---------------------------------------------------------------------------
# Figure 2: repayment trajectories by pathway (central scenario)
# ---------------------------------------------------------------------------

def figure_02_repayment_trajectories():
    disbursements = build_full_course_disbursements()
    _, summary = simulate_balance(disbursements, FIRST_REPAYMENT_DATE)
    starting_balance = summary["final_balance"]

    fig, ax = plt.subplots(figsize=(8, 5))

    for pathway_name in PATHWAY_NAMES:
        salary_path = get_pathway(pathway_name, scenario="central", total_years=40)
        result = simulate_repayment(starting_balance, FIRST_REPAYMENT_DATE, salary_path, max_years=40)

        record_dates = [r[0] for r in result["monthly_records"]]
        record_balances = [r[3] for r in result["monthly_records"]]
        years_since_start = [(d - FIRST_REPAYMENT_DATE).days / 365.25 for d in record_dates]

        label = PATHWAY_LABELS[pathway_name]
        outcome = "written off" if result["written_off"] else f"repaid in {result['years_elapsed']:.0f}y"
        ax.plot(
            years_since_start, record_balances,
            color=PATHWAY_COLOURS[pathway_name], label=f"{label} ({outcome})"
        )

    ax.axvline(40, color="0.3", linestyle=":", linewidth=1.2)
    ax.text(40.3, ax.get_ylim()[1] * 0.08, "40-year\nwrite-off", fontsize=9, color="0.3")

    ax.yaxis.set_major_formatter(FuncFormatter(format_gbp))
    ax.set_xlabel("Years since first repayment (April 2028)")
    ax.set_ylabel("Remaining loan balance")
    ax.set_title("Repayment trajectories by career pathway (central scenario)")
    ax.legend(frameon=True, loc="upper left", fontsize=9)
    ax.set_xlim(0, 44)
    savefig(fig, "fig02_repayment_trajectories_central")




def main():
    set_report_style()
    figure_01_balance_reconstruction()
    figure_02_repayment_trajectories()


if __name__ == "__main__":
    main()
