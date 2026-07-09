"""
Stochastic (Monte Carlo) salary pathway simulation.

Replaces the three discrete low/central/high bands in pathways.py with an
actual probability distribution over outcomes, built from two distinct
sources of uncertainty:

1.  Smooth continuous variation: a multiplicative log-normal shock applied
    every year around the 'central' deterministic trajectory (bonuses,
    raises, cost-of-living differences -- conditional on staying on the
    same career track).
2.  For the academic pathway specifically, an explicit discrete event:
    whether/when a postdoc ever converts to a permanent academic position,
    modelled with an annual hazard rate calibrated so the *eventual*
    conversion probability matches real literature estimates (see
    docs/assumptions_and_sources.md). Most simulated academics never
    convert, matching the (sobering, well-documented) reality.

See docs/assumptions_and_sources.md for the sourcing and reasoning behind
every parameter here.
"""

import numpy as np

from .pathways import academic_pathway, get_pathway

DEFAULT_SIGMA_ANNUAL = 0.12
DEFAULT_SIGMA_PERSISTENT = 0.18
DEFAULT_PERMANENT_POSITION_PROBABILITY = 0.20  # eventual, over the modelled window
DEFAULT_CONVERSION_WINDOW_YEARS = 15  # years of postdoc-eligibility over which conversion can happen


def _lognormal_multiplicative_shocks(n_simulations, n_years, sigma, rng):
    """
    iid multiplicative log-normal shocks, mean-corrected so E[shock] = 1
    (i.e. the noise doesn't systematically bias the trajectory up or down).
    Represents year-to-year ("transitory") variation: bonuses, raises,
    small role changes.
    """
    mu = -0.5 * sigma ** 2
    return rng.lognormal(mean=mu, sigma=sigma, size=(n_simulations, n_years))


def _persistent_career_quality_multiplier(n_simulations, sigma_persistent, rng):
    """
    Draws ONE multiplicative "career quality" factor per simulation, held
    fixed across every year of that simulated career, representing durable
    differences in promotion speed, negotiating position, or reputation
    that tend to persist across a whole career rather than washing out
    year to year.

    This matters a lot: without it, every simulation just jitters around
    the *same* central trajectory forever, and nothing ever ends up on a
    genuinely faster- or slower-growing path the way the deterministic
    low/central/high bands in pathways.py do -- which was a real gap
    caught by noticing the Monte Carlo results collapsed to near-100% or
    near-0% write-off probability with no middle ground, rather than the
    spread you'd actually expect. See docs/assumptions_and_sources.md for
    why sigma_persistent is a modelling choice rather than a directly
    sourced figure.
    """
    mu = -0.5 * sigma_persistent ** 2
    return rng.lognormal(mean=mu, sigma=sigma_persistent, size=n_simulations)


def _annual_hazard_from_eventual_probability(eventual_probability, window_years):
    """
    Converts a cumulative "eventual" probability over `window_years` into a
    constant annual hazard rate, via (1 - hazard)^window_years = 1 - eventual_probability.
    """
    return 1.0 - (1.0 - eventual_probability) ** (1.0 / window_years)


def simulate_stochastic_generic(pathway_name, n_simulations=2000, total_years=40,
                                 sigma_annual=DEFAULT_SIGMA_ANNUAL,
                                 sigma_persistent=DEFAULT_SIGMA_PERSISTENT, seed=None):
    """
    Generic stochastic wrapper for pathways with no discrete structural
    event modelled (industry_data, industry_quant): a persistent
    per-career "quality" multiplier (fixed for that whole simulation) plus
    year-to-year log-normal noise, both around the 'central' deterministic
    trajectory.

    Returns an ndarray of shape (n_simulations, total_years) of
    SL-assessable annual incomes.
    """
    rng = np.random.default_rng(seed)
    central = get_pathway(pathway_name, scenario="central", total_years=total_years)
    base = np.array([y.sl_assessable_income for y in central])

    persistent = _persistent_career_quality_multiplier(n_simulations, sigma_persistent, rng)
    transitory = _lognormal_multiplicative_shocks(n_simulations, total_years, sigma_annual, rng)

    return base[None, :] * persistent[:, None] * transitory


def simulate_stochastic_academic(n_simulations=2000, total_years=40,
                                  sigma_annual=DEFAULT_SIGMA_ANNUAL,
                                  sigma_persistent=DEFAULT_SIGMA_PERSISTENT,
                                  permanent_position_probability=DEFAULT_PERMANENT_POSITION_PROBABILITY,
                                  conversion_window_years=DEFAULT_CONVERSION_WINDOW_YEARS,
                                  seed=None):
    """
    Stochastic academic pathway: PhD (fixed, not SL-assessable) -> postdoc,
    with each simulated career independently drawing whether/when it ever
    converts to a permanent position, on top of a persistent per-career
    quality factor and smooth year-to-year log-normal noise.

    Returns an ndarray of shape (n_simulations, total_years) of
    SL-assessable annual incomes.
    """
    rng = np.random.default_rng(seed)

    permanent_track = get_pathway("academic", scenario="central", total_years=total_years)
    never_permanent_track = get_pathway("academic", scenario="low", total_years=total_years)

    permanent_income = np.array([y.sl_assessable_income for y in permanent_track])
    never_permanent_income = np.array([y.sl_assessable_income for y in never_permanent_track])

    phd_years = sum(1 for y in permanent_track if not y.sl_assessable_income and y.gross_income > 0)
    # (PhD years are those with gross_income > 0 but sl_assessable_income == 0, per pathways.py's convention)

    annual_hazard = _annual_hazard_from_eventual_probability(permanent_position_probability, conversion_window_years)

    base_incomes = np.empty((n_simulations, total_years))

    for sim in range(n_simulations):
        # Test the annual hazard once per eligible year; the loop's own
        # cumulative probability of firing already equals
        # permanent_position_probability by construction (see
        # _annual_hazard_from_eventual_probability), so there is no
        # separate outer "does this person convert at all" draw needed --
        # adding one would double-apply the probability.
        conversion_year = None
        for offset in range(conversion_window_years):
            if rng.random() < annual_hazard:
                conversion_year = phd_years + offset
                break

        for year in range(total_years):
            if conversion_year is not None and year >= conversion_year:
                # Shift the permanent track's post-conversion salary curve to start at conversion_year
                shifted_index = min(year - conversion_year + phd_years + 1, total_years - 1)
                base_incomes[sim, year] = permanent_income[shifted_index]
            else:
                base_incomes[sim, year] = never_permanent_income[year]

    persistent = _persistent_career_quality_multiplier(n_simulations, sigma_persistent, rng)
    transitory = _lognormal_multiplicative_shocks(n_simulations, total_years, sigma_annual, rng)

    result = base_incomes * persistent[:, None] * transitory
    # PhD stipend years are fixed (not subject to persistent/transitory
    # noise -- the stipend is a fixed national rate, not a negotiated
    # salary) and never SL-assessable regardless of noise.
    result[:, :phd_years] = 0.0
    return result


def simulate_stochastic_pathway(pathway_name, n_simulations=2000, total_years=40,
                                 sigma_annual=DEFAULT_SIGMA_ANNUAL, seed=None, **kwargs):
    """Dispatches to the academic-specific simulator or the generic one, by pathway name."""
    if pathway_name == "academic":
        return simulate_stochastic_academic(
            n_simulations=n_simulations, total_years=total_years, sigma_annual=sigma_annual, seed=seed, **kwargs
        )
    return simulate_stochastic_generic(
        pathway_name, n_simulations=n_simulations, total_years=total_years, sigma_annual=sigma_annual, seed=seed
    )
