"""
Monte Carlo Plan 5 repayment simulation: runs many stochastic salary
paths per career pathway through the full repayment engine, replacing
the three discrete scenario bands in script 02 with an actual
probability distribution over outcomes.

Usage: python scripts/03_monte_carlo_repayment.py [--n-sims 500]
"""

import _pathfix  # noqa: F401

import argparse
import time
from datetime import date

import numpy as np

from plan5.fees import maintenance_loan_minimum, tuition_fee_cap
from plan5.loan import generate_year_disbursements, simulate_balance
from plan5.repayment import simulate_repayment
from salary.pathways import YearIncome
from salary.stochastic import simulate_stochastic_pathway

COURSE_START_YEAR = 2023
COURSE_LENGTH_YEARS = 4
FIRST_REPAYMENT_DATE = date(2028, 4, 6)
PATHWAY_NAMES = ["academic", "industry_data", "industry_quant"]


def academic_year_label(start_year):
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def balance_at_first_repayment():
    disbursements = []
    for i in range(COURSE_LENGTH_YEARS):
        start_year = COURSE_START_YEAR + i
        label = academic_year_label(start_year)
        tuition = tuition_fee_cap(label)
        maintenance = maintenance_loan_minimum(label)
        disbursements += generate_year_disbursements(start_year, tuition, maintenance, label=label)
    _, summary = simulate_balance(disbursements, FIRST_REPAYMENT_DATE)
    return summary["final_balance"]


def run_monte_carlo_for_pathway(pathway_name, starting_balance, n_sims, seed_base=1000):
    salary_sims = simulate_stochastic_pathway(pathway_name, n_simulations=n_sims, total_years=40, seed=seed_base)

    total_repaid = np.empty(n_sims)
    written_off = np.empty(n_sims, dtype=bool)
    years_elapsed = np.empty(n_sims)

    for i in range(n_sims):
        income_path = [YearIncome(y, salary_sims[i, y], salary_sims[i, y], "") for y in range(40)]
        result = simulate_repayment(starting_balance, FIRST_REPAYMENT_DATE, income_path, max_years=40)
        total_repaid[i] = result["total_repaid"]
        written_off[i] = result["written_off"]
        years_elapsed[i] = result["years_elapsed"]

    return {
        "total_repaid": total_repaid,
        "written_off": written_off,
        "years_elapsed": years_elapsed,
    }


def summarise(results):
    write_off_pct = 100 * results["written_off"].mean()
    repaid = results["total_repaid"]

    summary = {
        "write_off_probability_pct": write_off_pct,
        "mean_total_repaid": repaid.mean(),
        "median_total_repaid": np.median(repaid),
        "p10_total_repaid": np.percentile(repaid, 10),
        "p90_total_repaid": np.percentile(repaid, 90),
    }

    fully_repaid_mask = ~results["written_off"]
    if fully_repaid_mask.any():
        summary["median_years_if_repaid"] = np.median(results["years_elapsed"][fully_repaid_mask])
    else:
        summary["median_years_if_repaid"] = None

    return summary


def main(n_sims=500):
    starting_balance = balance_at_first_repayment()
    print(f"Starting balance at first repayment ({FIRST_REPAYMENT_DATE}): £{starting_balance:,.2f}")
    print(f"Running {n_sims} Monte Carlo simulations per pathway ({n_sims * len(PATHWAY_NAMES)} total)...\n")

    t0 = time.time()
    all_results = {}
    for pathway_name in PATHWAY_NAMES:
        results = run_monte_carlo_for_pathway(pathway_name, starting_balance, n_sims, seed_base=hash(pathway_name) % 10_000)
        all_results[pathway_name] = results

    elapsed = time.time() - t0
    print(f"Done in {elapsed:.1f}s.\n")

    print("=" * 90)
    print("MONTE CARLO REPAYMENT OUTCOMES BY CAREER PATHWAY")
    print("=" * 90)
    header = (f"{'Pathway':16s} {'P(written off)':>15s} {'Mean repaid':>13s} "
              f"{'Median repaid':>14s} {'P10':>10s} {'P90':>10s} {'Median yrs*':>12s}")
    print(header)
    print("-" * len(header))

    summaries = {}
    for pathway_name in PATHWAY_NAMES:
        s = summarise(all_results[pathway_name])
        summaries[pathway_name] = s
        years_str = f"{s['median_years_if_repaid']:.1f}" if s['median_years_if_repaid'] is not None else "n/a"
        print(
            f"{pathway_name:16s} {s['write_off_probability_pct']:>13.1f}% "
            f"£{s['mean_total_repaid']:>11,.0f} £{s['median_total_repaid']:>12,.0f} "
            f"£{s['p10_total_repaid']:>8,.0f} £{s['p90_total_repaid']:>8,.0f} {years_str:>12s}"
        )

    print("\n* Median years-to-repay-in-full, computed only among simulations that")
    print("  didn't get written off (n/a if none did).")
    print("\nThese probabilities depend heavily on the deterministic 'central'")
    print("trajectory and hazard-rate assumptions in src/salary/pathways.py and")
    print("src/salary/stochastic.py -- see docs/assumptions_and_sources.md.")

    return all_results, summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sims", type=int, default=500)
    args = parser.parse_args()
    main(n_sims=args.n_sims)
