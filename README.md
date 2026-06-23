# Plan 5 Student Loan Analysis

A quantitative look at the UK Plan 5 student loan: real interest-rate
history, income-contingent repayment, salary-pathway modelling, and a
loan-vs-savings decision. Work in progress.

## What's built so far

- `src/plan5/rates.py` -- real, dated Plan 5 interest rate history and lookup.
- `src/plan5/fees.py` -- historical tuition fee and maintenance loan figures.
- `src/plan5/loan.py` -- day-by-day loan balance simulation with daily
  compounding, unit-tested against the analytical compounding formula
  (caught and fixed a genuine off-by-one bug in the day-counting loop).
- `scripts/01_reconstruct_current_balance.py` -- reconstructs the actual
  loan balance to date from real disbursement and interest-rate history.

**First real result:** current balance (3 years borrowed so far) is
approximately **£45,341**, of which about £2,857 is accrued interest.

Every real-world figure used is logged with its source and a confidence
rating in `docs/assumptions_and_sources.md`.

## Roadmap

- Salary pathway modelling (deterministic scenarios, then a stochastic layer).
- Full income-contingent repayment simulation.
- The year-4 maintenance-loan-vs-savings decision.
- Report figures.

## License

MIT -- see LICENSE.
