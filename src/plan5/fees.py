"""
Historical tuition fee loan cap and maintenance loan lookups.

Loads data/tuition_fee_caps.csv and data/maintenance_loan_minimum.csv.
See docs/assumptions_and_sources.md for sourcing and confidence levels
(the maintenance-loan figures before 2026/27 are estimated, not confirmed).
"""

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_tuition_fee_caps(csv_path=None):
    """Returns a dict {academic_year_str: (fee_cap, confidence)}."""
    csv_path = csv_path or (DATA_DIR / "tuition_fee_caps.csv")
    result = {}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            result[row["academic_year"]] = (float(row["tuition_fee_cap"]), row["confidence"])
    return result


def load_maintenance_loan_minimum(csv_path=None):
    """Returns a dict {academic_year_str: (minimum_loan_outside_london, confidence)}."""
    csv_path = csv_path or (DATA_DIR / "maintenance_loan_minimum.csv")
    result = {}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            result[row["academic_year"]] = (
                float(row["maintenance_loan_minimum_outside_london"]),
                row["confidence"],
            )
    return result


def tuition_fee_cap(academic_year, caps=None):
    """E.g. tuition_fee_cap("2024/25") -> 9250.0"""
    caps = caps if caps is not None else load_tuition_fee_caps()
    if academic_year not in caps:
        raise KeyError(f"No tuition fee cap on file for {academic_year}; add it to tuition_fee_caps.csv.")
    return caps[academic_year][0]


def maintenance_loan_minimum(academic_year, minimums=None):
    """E.g. maintenance_loan_minimum("2024/25") -> 4767.03"""
    minimums = minimums if minimums is not None else load_maintenance_loan_minimum()
    if academic_year not in minimums:
        raise KeyError(f"No maintenance loan figure on file for {academic_year}; add it to maintenance_loan_minimum.csv.")
    return minimums[academic_year][0]
