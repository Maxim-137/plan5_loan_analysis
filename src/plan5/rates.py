"""
Plan 5 interest rate history and lookup.

Loads the real, dated rate history from data/plan5_interest_rate_history.csv
(see docs/assumptions_and_sources.md for sourcing) and provides a lookup for
the applicable annual rate on any given date, plus tools to override the
forward-looking assumption for scenario analysis.
"""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class RatePeriod:
    start: date
    end: date
    annual_rate: float
    basis: str
    confidence: str
    note: str


def _parse_date(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def load_rate_history(csv_path=None):
    """
    Loads the Plan 5 interest rate history as a list of RatePeriod, sorted
    by start date. The last row's `end` is treated as an open-ended
    forward assumption unless overridden.
    """
    csv_path = csv_path or (DATA_DIR / "plan5_interest_rate_history.csv")
    periods = []

    with open(csv_path) as f:
        header = f.readline()  # noqa: F841 (header consumed, not needed)
        for line in f:
            line = line.strip()
            if not line:
                continue
            start_s, end_s, rate_s, basis, confidence, note = line.split(",", 5)
            periods.append(RatePeriod(
                start=_parse_date(start_s),
                end=_parse_date(end_s),
                annual_rate=float(rate_s),
                basis=basis,
                confidence=confidence,
                note=note,
            ))

    periods.sort(key=lambda p: p.start)
    return periods


def rate_on(query_date, periods=None, forward_rate_override=None):
    """
    Returns the annual Plan 5 interest rate applicable on `query_date`.

    If `query_date` falls after the last confirmed/estimated period and
    `forward_rate_override` is given, that value is used instead of the
    CSV's built-in long-run assumption -- this is how scenario analysis
    varies the "what if future RPI runs hotter/cooler" assumption without
    touching the historical record.
    """
    periods = periods if periods is not None else load_rate_history()

    for period in periods:
        if period.start <= query_date <= period.end:
            if forward_rate_override is not None and period.confidence == "assumption":
                return forward_rate_override
            return period.annual_rate

    raise ValueError(f"No rate period covers {query_date}; extend the rate history CSV.")


def rate_history_confidence_summary(periods=None):
    """Returns a dict counting periods by confidence level, useful as a quick data-quality check."""
    periods = periods if periods is not None else load_rate_history()
    summary = {}
    for p in periods:
        summary[p.confidence] = summary.get(p.confidence, 0) + 1
    return summary
