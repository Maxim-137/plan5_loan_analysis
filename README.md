# Plan 5 Student Loan Analysis

A quantitative look at the UK Plan 5 student loan: real interest-rate
history, income-contingent repayment, salary-pathway modelling, and a
loan-vs-savings decision. Work in progress.

## What's built so far

- `src/plan5/rates.py` -- real, dated Plan 5 interest rate history and lookup.
- `src/plan5/fees.py` -- historical tuition fee and maintenance loan figures.
- `src/plan5/loan.py` -- day-by-day loan balance simulation with daily
  compounding, unit-tested (caught and fixed a genuine off-by-one bug in
  the day-counting loop).
- `src/plan5/repayment.py` -- full income-contingent repayment simulation:
  monthly 9%-above-threshold deductions, the post-2027 RPI-linked
  threshold uprating, and the 40-year write-off (also caught and fixed a
  genuine off-by-one bug here, in the threshold uprating logic).
- `src/salary/pathways.py` -- three deterministic career-pathway models
  (academic/research, industry data/technical, industry quant), each with
  low/central/high scenarios built from real salary anchors.
- `scripts/01_reconstruct_current_balance.py` -- real balance to date:
  **~£45,341** as of today (3 years borrowed so far).
- `scripts/02_full_lifecycle_simulation.py` -- the full pipeline: real
  balance -> grown to the first repayment date (April 2028) -> full
  40-year repayment simulation.

### Key finding so far

Running the full course's borrowing forward through repayment gives a
genuinely striking result: the **academic/research pathway gets written
off in every single modelled scenario** -- low, central, *and* high. By
contrast, the **industry quant pathway repays in full in every scenario**,
and **industry data/technical is the genuinely mixed case**.

This matters a lot for the eventual "loan vs savings" decision: because
Plan 5 repayment amount depends only on income (not on the loan balance,
as long as the balance stays above zero), an extra pound borrowed while on
a track that's heading for write-off anyway may cost close to nothing in
extra lifetime repayments -- while the same extra pound on a track that's
going to fully repay costs real, calculable interest.

Every real-world figure used is logged with its source and a confidence
rating in `docs/assumptions_and_sources.md`.

## Roadmap

- Stochastic Monte Carlo layer (replacing the three discrete bands with
  an actual probability distribution).
- The year-4 maintenance-loan-vs-savings decision module.
- Report figures.

## License

MIT -- see LICENSE.
