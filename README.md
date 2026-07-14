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
- `src/salary/stochastic.py` -- Monte Carlo layer with a persistent
  per-career "quality" factor and a stochastic postdoc-to-permanent-
  position hazard rate for the academic pathway.
- `scripts/01_reconstruct_current_balance.py` -- real balance to date:
  **~£45,341** as of today.
- `scripts/02_full_lifecycle_simulation.py` / `scripts/03_monte_carlo_repayment.py`
  -- deterministic and Monte Carlo pathway comparisons.
- `src/decision/loan_vs_savings.py` and
  `scripts/04_loan_vs_savings_decision.py` -- the actual year-4 decision:
  a paired Monte Carlo comparison isolating the true marginal extra
  lifetime repayment caused by borrowing this year, vs foregone
  growth on that amount at a range of assumed return rates.

### Key finding so far

| Pathway | P(written off) | Median total repaid |
|---|---|---|
| Academic/research | ~99-100% | ~£10,400 |
| Industry (data/technical) | ~63-68% | ~£88,000 |
| Industry (quant) | ~0% | ~£78,500 |

**The actual year-4 answer:** the marginal extra lifetime repayment from
taking this year's maintenance loan is **£0 on the academic pathway**
(written off either way), a **mean of ~£4,000 on industry/data** (median
£0, genuinely skewed), and a **near-certain ~£7,400-7,500 on
industry/quant**. Compared against foregone growth on the same amount:
**taking the loan wins outright on every pathway at a 4%+ assumed
return**, and even the worst case (quant) breaks even around 2-3% --
below what most UK savings accounts have paid recently.

**Methodological note:** an early version of the Monte Carlo layer used
only year-to-year noise around a single central trajectory, which
collapsed every pathway to a near-100%-or-near-0% write-off probability.
Adding a persistent, career-long "quality" factor fixed this. See
`tests/test_stochastic.py` for the regression test this created.

Every real-world figure used is logged with its source and a confidence
rating in `docs/assumptions_and_sources.md`.

## Roadmap

- Report figures.

## License

MIT -- see LICENSE.
