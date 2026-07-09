# Plan 5 Student Loan Analysis

A quantitative look at the UK Plan 5 student loan: real interest-rate
history, income-contingent repayment, salary-pathway modelling, and a
loan-vs-savings decision. Work in progress.

## What's built so far

- `src/plan5/rates.py` -- real, dated Plan 5 interest rate history and lookup.
- `src/plan5/fees.py` -- historical tuition fee and maintenance loan figures.
- `src/plan5/loan.py` -- day-by-day loan balance simulation with daily
  compounding, unit-tested (caught and fixed a genuine off-by-one bug).
- `src/plan5/repayment.py` -- full income-contingent repayment simulation
  (also caught and fixed a genuine off-by-one bug, in the threshold
  uprating logic).
- `src/salary/pathways.py` -- three deterministic career-pathway models
  (academic/research, industry data/technical, industry quant).
- `src/salary/stochastic.py` -- Monte Carlo layer: a persistent per-career
  "quality" factor plus year-to-year log-normal noise, and (for the
  academic pathway) a stochastic postdoc-to-permanent-position hazard
  rate calibrated to real literature estimates (~20% ever convert).
- `scripts/01_reconstruct_current_balance.py` -- real balance to date:
  **~£45,341** as of today.
- `scripts/02_full_lifecycle_simulation.py` -- deterministic pathway comparison.
- `scripts/03_monte_carlo_repayment.py` -- the same pipeline with an
  actual Monte Carlo probability distribution over outcomes.

### Key finding so far

| Pathway | P(written off) | Median total repaid |
|---|---|---|
| Academic/research | **~99-100%** | ~£10,400 |
| Industry (data/technical) | ~63-68% | ~£88,000 |
| Industry (quant) | **~0%** | ~£78,500 |

The academic pathway is written off in nearly every plausible simulated
career. Industry quant repays in full in essentially every simulation.
Industry data/technical is the genuinely uncertain case.

**Methodological note:** an early version of the Monte Carlo layer used
only year-to-year noise around a single central trajectory, which
collapsed every pathway to a near-100%-or-near-0% write-off probability
with no realistic middle ground. Adding a persistent, career-long
"quality" factor (fixed per simulated career, representing durable
differences in promotion speed that compound rather than wash out) fixed
this. See `tests/test_stochastic.py` for the regression test this created.

Every real-world figure used is logged with its source and a confidence
rating in `docs/assumptions_and_sources.md`.

## Roadmap

- The year-4 maintenance-loan-vs-savings decision module.
- Report figures.

## License

MIT -- see LICENSE.
