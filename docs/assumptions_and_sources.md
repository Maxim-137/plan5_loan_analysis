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

## Salary pathway anchors (researched for the career-path modelling)

| Fact | Value | Confidence | Source |
|---|---|---|---|
| UKRI minimum PhD stipend, 2024/25 | £19,237/year (tax-free) | confirmed | Nature careers news, UKRI |
| UKRI minimum PhD stipend, 2025/26 | £20,780/year (+8%) | confirmed | UKRI announcement, 30 Jan 2025 |
| UKRI minimum PhD stipend, 2026/27 | £21,805/year (+4.9%), from 1 Oct 2026 | confirmed | UKRI announcement, 5 Feb 2026 |
| PhD stipends are not subject to Income Tax, NI, or Plan 5 repayment deductions | assumed true (stipends are bursaries, not PAYE/self-employment earnings) | assumption (high confidence, not independently verified via a dedicated search) | standard treatment of UKRI studentships; worth a direct confirmatory check before treating as settled |
| Postdoc / Research Associate (Grade 7-equivalent) starting salary | ~£38,000-£41,000, rising to ~£46,000-£48,000 within grade | confirmed (range across multiple current job listings) | jobs.ac.uk live listings, July 2026 |
| Postdoc average (all levels) | £40,280/year | confirmed | Indeed UK aggregate, Feb 2026 |
| Senior Lecturer / Associate Professor | ~£52,000-£67,000 (median ~£57,000) | confirmed | Payscale UK aggregate |
| Full Professor | not confirmed here; treated as a ~£70,000-£85,000 ceiling for modelling the far tail of the academic path | assumption | not independently sourced -- flagged as the weakest anchor in the academic pathway |
| Science-subject graduates, median salary 15 months after graduation | £29,498 (2022/23) -> £30,000 (2023/24) | confirmed | HESA Graduate Outcomes SB275 |
| Graduate data scientist, average starting salary | ~£35,873/year | confirmed | Glassdoor UK, Apr 2026 |
| Data scientist, 2-5 years experience | £50,000-£65,000/year | estimated (industry aggregator, not an official survey) | upGrad UK salary guide, May 2026 |
| Graduate quant (bank, entry) | roughly £55,000-£80,000 base in London depending on firm tier; top prop-trading firms start near the top of this range | estimated (industry guide, illustrative, self-reported aggregator data mixed with editorial commentary) | Quantt UK quant salary guide, 2026 |
| Quant total compensation, experienced | can range very widely (£90,000 to £500,000+ at senior/prop-trading level) | estimated, high dispersion is a genuine feature of this career track, not just noise | Quantt, Glassdoor UK aggregates |

**Action items:** the full-professor ceiling and the quant-track figures are
the least rigorously sourced inputs in this project (aggregator/self-report
sites rather than an official survey like HESA/ONS). They're good enough to
show realistic *shape* and *relative* differences between career tracks, but
shouldn't be read as precise.

## Stochastic model calibration

| Fact | Value used | Confidence | Source |
|---|---|---|---|
| UK individual earnings year-on-year volatility (SD of arc % change, UKHLS-based) | ~0.40-0.42 | confirmed (population-wide estimate) | Avram et al. (2022) via Brewer, "What Do We Know About Income and Earnings Volatility?", Review of Income and Wealth (2025) |
| Annual log-normal sigma used in this project's stochastic model | 0.12 | assumption -- deliberately set below the population-wide figure above, because that figure pools in structural transitions (job loss, sector switches, part-time transitions) that this project models as a *separate*, explicit discrete event (see below) rather than folding into smooth continuous noise. 0.12 represents realistic bonus/raise/cost-of-living variation *conditional on staying on the same career track*. | modelling choice, stated explicitly so it can be revisited |
| Proportion of UK/international postdocs who ever reach a permanent academic (tenured/tenure-equivalent) position | roughly 10%-15% across the general postdoc population; some UK-specific surveys report 20-30% (definitions and cohorts vary a lot between studies) | confirmed range, but with real cross-study disagreement -- flagged explicitly | CEDARS (2021), Hardy/Carter/Bowden (2016), and others, via Prosper Portal (Liverpool); UK-specific alumni tracking studies cited in an Effective Altruism Forum literature review |
| Central "eventual permanent position" probability used in this project | 20% | assumption, chosen as a round central estimate within the sourced range above | modelling choice |
| Note on selection bias | a Times Higher Education report on British Academy postdoctoral *fellows* specifically (a highly competitive, elite sub-population) found ~91% went on to permanent roles -- this is NOT used as the general-population estimate here, since it reflects an already-selected group, but is worth knowing as context for what a strong fellowship can do to these odds | confirmed (for that specific fellowship's alumni only) | Times Higher Education, 22 May 2025 |
