"""
Year 4: take the maintenance loan, or use savings instead?

Compares the marginal extra lifetime repayment caused by borrowing this
year's maintenance loan (rather than funding the same amount from
savings) against the foregone growth of that same amount if it had been
left invested/saved, across a range of assumed return rates and all
three career pathways.

Usage: python scripts/04_loan_vs_savings_decision.py [--n-sims 300]
"""

import _pathfix  # noqa: F401

import argparse

from decision.loan_vs_savings import balances_at_first_repayment, compare_pathway

PATHWAY_NAMES = ["academic", "industry_data", "industry_quant"]
RETURN_RATES = (0.0, 0.02, 0.04, 0.06, 0.08)
RETURN_RATE_LABELS = {
    0.0: "0% (cash, no growth)",
    0.02: "2% (below-inflation savings)",
    0.04: "4% (typical easy-access savings)",
    0.06: "6% (moderate investment)",
    0.08: "8% (long-run diversified equities, historical)",
}


def main(n_sims=300):
    balance_with, balance_without, deferred_amount = balances_at_first_repayment()

    print("=" * 90)
    print("YEAR 4 MAINTENANCE LOAN VS SAVINGS: MARGINAL DECISION ANALYSIS")
    print("=" * 90)
    print(f"Amount in question (2026/27 maintenance loan, estimated): £{deferred_amount:,.2f}")
    print(f"Balance at first repayment WITH this year's maintenance loan:    £{balance_with:,.2f}")
    print(f"Balance at first repayment WITHOUT it:                          £{balance_without:,.2f}")
    print(f"(difference already reflects ~1.5-2 years of Plan 5 interest before repayment starts)\n")

    print("If you take the loan: you keep this amount in savings/investments instead of spending")
    print("it on living costs, and it can grow. The question is whether that growth outweighs the")
    print("EXTRA amount you'll actually repay over your lifetime as a result of the bigger balance")
    print("-- which, as shown in script 03, is NOT the same as the loan's interest rate, because")
    print("repayment depends on income, not balance, once you factor in write-off.\n")

    results = {}
    for pathway in PATHWAY_NAMES:
        print(f"Running Monte Carlo comparison for {pathway}...")
        results[pathway] = compare_pathway(pathway, return_rates=RETURN_RATES, n_sims=n_sims)

    print("\n" + "=" * 90)
    print("MARGINAL EXTRA LIFETIME REPAYMENT FROM TAKING THE LOAN (vs using savings)")
    print("=" * 90)
    header = f"{'Pathway':16s} {'Mean':>10s} {'Median':>10s} {'P10':>10s} {'P90':>10s}"
    print(header)
    print("-" * len(header))
    for pathway in PATHWAY_NAMES:
        r = results[pathway]
        print(
            f"{pathway:16s} £{r['extra_repaid_mean']:>8,.0f} £{r['extra_repaid_median']:>8,.0f} "
            f"£{r['extra_repaid_p10']:>8,.0f} £{r['extra_repaid_p90']:>8,.0f}"
        )

    print("\n" + "=" * 90)
    print(f"FOREGONE GROWTH IF £{deferred_amount:,.0f} STAYS INVESTED (~41 years, to the write-off date)")
    print("=" * 90)
    for rate in RETURN_RATES:
        growth = results[PATHWAY_NAMES[0]]["growth_by_rate"][rate]  # same for all pathways (doesn't depend on career)
        print(f"  {RETURN_RATE_LABELS[rate]:45s} £{growth:>10,.0f}")

    print("\n" + "=" * 90)
    print("BOTTOM LINE: net benefit of TAKING THE LOAN (foregone growth MINUS extra repaid)")
    print("Positive = taking the loan and keeping savings invested comes out ahead")
    print("Negative = using savings instead comes out ahead")
    print("=" * 90)
    header2 = f"{'Pathway':16s}" + "".join(f"{f'@{int(r*100)}%':>10s}" for r in RETURN_RATES)

    print("\nUsing MEDIAN extra repaid (\"most likely\" outcome):")
    print(header2)
    print("-" * len(header2))
    for pathway in PATHWAY_NAMES:
        r = results[pathway]
        row = f"{pathway:16s}"
        for rate in RETURN_RATES:
            net = r["growth_by_rate"][rate] - r["extra_repaid_median"]
            row += f"£{net:>8,.0f}"
        print(row)

    print("\nUsing MEAN extra repaid (risk-weighted expected value -- matters more when the")
    print("outcome is genuinely uncertain, e.g. industry_data's ~65%/35% split):")
    print(header2)
    print("-" * len(header2))
    for pathway in PATHWAY_NAMES:
        r = results[pathway]
        row = f"{pathway:16s}"
        for rate in RETURN_RATES:
            net = r["growth_by_rate"][rate] - r["extra_repaid_mean"]
            row += f"£{net:>8,.0f}"
        print(row)

    print("\nFor a pathway with a wide split between likely outcomes (like industry_data),")
    print("the MEAN is the more theoretically appropriate figure for a single expected-value")
    print("decision, since it properly weights the less-likely-but-costly scenarios; the")
    print("MEDIAN just describes the single most probable outcome on its own.")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sims", type=int, default=300)
    args = parser.parse_args()
    main(n_sims=args.n_sims)
