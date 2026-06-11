# Data sources and assumptions

Every figure this project uses that comes from the real world is logged here,
with its source and a confidence rating. The rule: nothing gets hard-coded
into the analysis without an entry here explaining where it came from and how
sure we are of it. Figures marked `estimated` or `assumption` should be
treated as first-pass values to sanity-check, not final answers.

Confidence levels: `confirmed` (directly stated by an official/primary
source), `estimated` (derived/interpolated from official sources but not a
direct quote), `assumption` (a modelling choice we made, not a fact).

## Plan 5 mechanics

| Fact | Value | Confidence | Source |
|---|---|---|---|
| Applies to | English-domiciled undergrads starting course on/after 1 Aug 2023 | confirmed | gov.uk / House of Commons Library (CBP-10654) |
| Interest basis | RPI only (no added "real" rate, unlike Plan 2/3's RPI+3%) | confirmed | gov.uk, House of Commons Library |
| Repayment rate | 9% of income above threshold | confirmed | gov.uk, CIPP |
| Repayment threshold | £25,000/year, frozen since introduction | confirmed | House of Commons Library CBP-10654 |
| Threshold uprating from | April 2027, then in line with RPI | confirmed (Commons Library); one secondary source said "average earnings" instead -- Commons Library treated as authoritative | House of Commons Library CBP-10654 |
| Write-off term | 40 years after the April you're first due to repay | confirmed | Save the Student, gov.uk |
| Earliest possible first repayment date (any Plan 5 borrower) | 6 April 2026 | confirmed | CIPP, MoneySavingExpert |

## Plan 5 "while studying" interest rate history

The headline "RPI" rate and the *actual rate charged* diverge sharply in
2023/24-2024/25, because a monthly "Prevailing Market Rate" (PMR) cap kept
the rate well below RPI while RPI was running at unusually high (13.5%)
post-inflation-shock levels. This is encoded month-by-month in
`data/plan5_interest_rate_history.csv`.

| Period | Rate charged | Confidence | Source |
|---|---|---|---|
| 1 Sep 2023 - 30 Nov 2023 | 7.3% | confirmed | gov.uk announcement, 23 Aug 2023 |
| 1 Dec 2023 - ~31 Jan 2024 | 7.5% | confirmed | gov.uk announcement, 1 Dec 2023 |
| ~1 Feb 2024 - 31 Aug 2024 | 7.6% held flat | estimated | gov.uk announcement, Feb 2024 confirms 7.6%; Commons Library notes the cap "increased over the next twelve months to reach 8%" but doesn't give the intervening monthly values, so this period is modelled as flat at 7.6% pending confirmation of the exact month-by-month path |
| 1 Sep 2024 - 31 Aug 2025 | ~4.3% | estimated | Commons Library states this year's Plan 5 rate "= Plan 1 rate" (RPI or Bank Rate+1%, whichever lower); exact monthly Bank Rate path not individually verified here |
| 1 Sep 2025 - 31 Aug 2026 | 3.2% | confirmed | gov.uk announcement, 19 Aug 2025 |
| 1 Sep 2026 - 31 Aug 2027 | 4.1% | confirmed | Save the Student, citing RPI uplift, May 2026 |
| From 1 Sep 2027 onward | 3.0% (central), sensitivity range 1.5%-5.5% | assumption | modelling choice: roughly RPI's longer-run historical average; used only for forward projection, and should be treated as a scenario input, not a forecast |

**Action item before this is "final":** the Feb-Aug 2024 and Sep 2024-Aug
2025 rows are the weakest link in the historical reconstruction. Worth
cross-checking against the gov.uk historical interest rate archive page
directly if/when we want the exact accrued-to-date balance to be precise to
the pound rather than to a good approximation.

## Tuition fee loan cap (England, full-time undergraduate)

| Academic year | Cap | Confidence | Source |
|---|---|---|---|
| 2023/24 | £9,250 | confirmed | frozen since 2017/18; House of Lords Library |
| 2024/25 | £9,250 | confirmed | House of Lords Library |
| 2025/26 | £9,535 (+3.1%) | confirmed | House of Lords Library, Warwick/Newcastle fee announcements |
| 2026/27 | £9,790 (+2.71%) | confirmed | House of Lords Library, Prospects.ac.uk |
| 2027/28 (context only) | £10,050 (+2.68%) | confirmed | House of Lords Library |

## Maintenance loan (living away from home, outside London)

Full 2026/27 sliding scale by household income (confirmed, from a university
student finance briefing document):

| Household income | 2026/27 maintenance loan |
|---|---|
| £25,000 | £10,830 |
| £30,000 | £10,058 |
| £35,000 | £9,285 |
| £40,000 | £8,512 |
| £45,000 | £7,739 |
| £50,000 | £6,967 |
| £55,000 | £6,194 |
| £60,000 | £5,421 |
| £65,000 | £5,048 |

**Action item:** we only have a directly-confirmed sliding scale for
2026/27. Earlier years' exact minimum-band figures in
`data/maintenance_loan_minimum.csv` are currently backdated from the 2026/27
figures using the known year-on-year upratings (3.1% for 2025/26, and the
maintenance-loan upratings reported alongside each tuition fee change) --
these are `estimated`, not `confirmed`. If exact historical Student Finance
England entitlement letters are available, slot the real numbers in
directly and flip the confidence rating.

## Not yet sourced (needed for later stages of this project)

- ONS ASHE earnings distribution/growth-rate data, for calibrating the stochastic salary model's volatility (currently using an assumption -- see below)
