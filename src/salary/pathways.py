"""
Deterministic salary-pathway models.

Each career track is built from a sequence of CareerPhase segments (a
starting salary and a compounding annual growth rate for N years), which
keeps every anchor figure and growth assumption explicit and inspectable,
rather than burying them in a single opaque formula. See
docs/assumptions_and_sources.md for where every anchor salary came from.

Year 0 = the first year after leaving the MPhys (assumed 2027).

Note on PhD stipends: they are modelled as NOT "sl_assessable" -- i.e.
they don't count as income for Plan 5 repayment purposes (stipends are
tax-free bursaries, not PAYE/self-employment earnings), even though they
are real spending-power income for the person living on them. This is
flagged as an assumption in docs/assumptions_and_sources.md.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CareerPhase:
    duration_years: int
    start_salary: float
    annual_growth_rate: float
    sl_assessable: bool = True
    label: str = ""


@dataclass(frozen=True)
class YearIncome:
    year_index: int
    gross_income: float
    sl_assessable_income: float
    label: str = ""


def build_year_by_year(phases, total_years=40):
    """Expands a list of CareerPhase into one YearIncome per year, up to total_years."""
    incomes = []
    year = 0

    for phase in phases:
        salary = phase.start_salary
        for _ in range(phase.duration_years):
            if year >= total_years:
                return incomes
            assessable = salary if phase.sl_assessable else 0.0
            incomes.append(YearIncome(year, salary, assessable, phase.label))
            salary *= (1 + phase.annual_growth_rate)
            year += 1

    # Plateau at the final phase's last salary (with a very small drift so
    # it isn't perfectly flat forever, matching typical late-career small
    # increments) for any remaining years out to total_years.
    last_salary = incomes[-1].gross_income if incomes else 0.0
    while year < total_years:
        incomes.append(YearIncome(year, last_salary, last_salary, "plateau"))
        last_salary *= 1.015
        year += 1

    return incomes


# ---------------------------------------------------------------------------
# Academic / research route: PhD -> Postdoc -> Senior Research/Lectureship
# ---------------------------------------------------------------------------

def academic_pathway(scenario="central", total_years=40):
    """
    PhD stipend (tax-free, not SL-assessable) -> postdoc -> senior
    research/lectureship. The "low" scenario reflects the well-documented
    real risk in this track: an extended sequence of fixed-term postdoc
    contracts without ever landing a permanent role, not just "slower
    growth" -- academia's downside case is genuinely more severe than
    industry's.
    """
    if scenario == "low":
        phases = [
            CareerPhase(4, 21_805, 0.03, sl_assessable=False, label="PhD stipend"),
            CareerPhase(6, 38_000, 0.02, label="Postdoc (extended fixed-term)"),
            CareerPhase(30, 46_000, 0.008, label="Senior postdoc / no permanent post"),
        ]
    elif scenario == "high":
        phases = [
            CareerPhase(4, 21_805, 0.04, sl_assessable=False, label="PhD stipend"),
            CareerPhase(3, 41_000, 0.04, label="Postdoc"),
            CareerPhase(4, 50_000, 0.03, label="Lectureship"),
            CareerPhase(29, 68_000, 0.018, label="Senior Lecturer -> Professor"),
        ]
    else:  # central
        phases = [
            CareerPhase(4, 21_805, 0.035, sl_assessable=False, label="PhD stipend"),
            CareerPhase(4, 40_000, 0.03, label="Postdoc"),
            CareerPhase(6, 48_000, 0.025, label="Senior Research Fellow / Lecturer"),
            CareerPhase(26, 58_000, 0.012, label="Senior Lecturer / Associate Professor"),
        ]

    return build_year_by_year(phases, total_years)


# ---------------------------------------------------------------------------
# Industry: general technical / data track
# ---------------------------------------------------------------------------

def industry_data_pathway(scenario="central", total_years=40):
    """Graduate data/technical role -> senior individual contributor / team lead."""
    if scenario == "low":
        phases = [
            CareerPhase(5, 32_000, 0.025, label="Graduate/junior data role"),
            CareerPhase(35, 46_000, 0.010, label="Data analyst/scientist, slow progression"),
        ]
    elif scenario == "high":
        phases = [
            CareerPhase(3, 37_000, 0.09, label="Graduate data scientist"),
            CareerPhase(4, 58_000, 0.06, label="Data scientist -> senior"),
            CareerPhase(33, 92_000, 0.018, label="Staff/lead, then plateau"),
        ]
    else:  # central
        phases = [
            CareerPhase(3, 34_000, 0.055, label="Graduate data scientist"),
            CareerPhase(4, 46_000, 0.045, label="Data scientist"),
            CareerPhase(6, 62_000, 0.025, label="Senior data scientist"),
            CareerPhase(27, 75_000, 0.013, label="Staff/lead, plateau"),
        ]

    return build_year_by_year(phases, total_years)


# ---------------------------------------------------------------------------
# Industry: quantitative finance track
# ---------------------------------------------------------------------------

def industry_quant_pathway(scenario="central", total_years=40):
    """
    Graduate quant role -> senior quant/trader. Much higher entry point
    than the other tracks, and genuinely much wider dispersion between
    scenarios -- this is a real, well-documented feature of the quant
    career track, not a modelling artefact.
    """
    if scenario == "low":
        phases = [
            CareerPhase(5, 55_000, 0.035, label="Graduate quant, mid-tier bank"),
            CareerPhase(35, 85_000, 0.012, label="Quant analyst, steady track"),
        ]
    elif scenario == "high":
        phases = [
            CareerPhase(3, 70_000, 0.14, label="Graduate quant, top-tier firm"),
            CareerPhase(4, 140_000, 0.10, label="Quant researcher/trader, fast track"),
            CareerPhase(33, 260_000, 0.020, label="Senior quant/PM, plateau"),
        ]
    else:  # central
        phases = [
            CareerPhase(3, 60_000, 0.09, label="Graduate quant"),
            CareerPhase(4, 90_000, 0.07, label="Quant analyst/researcher"),
            CareerPhase(6, 140_000, 0.03, label="Senior quant"),
            CareerPhase(27, 170_000, 0.015, label="Senior quant/PM, plateau"),
        ]

    return build_year_by_year(phases, total_years)


PATHWAYS = {
    "academic": academic_pathway,
    "industry_data": industry_data_pathway,
    "industry_quant": industry_quant_pathway,
}


def get_pathway(name, scenario="central", total_years=40):
    if name not in PATHWAYS:
        raise KeyError(f"Unknown pathway '{name}'. Choose from: {list(PATHWAYS)}")
    return PATHWAYS[name](scenario=scenario, total_years=total_years)
