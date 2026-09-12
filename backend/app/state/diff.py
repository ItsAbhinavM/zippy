from __future__ import annotations
from app.state.models import FinancialState


SECTION_FIELDS = [
    "income",
    "essential_expenses",
    "optional_expenses",
    "payments",
    "conflicts",
    "missing_fields",
    "starting_balance",
    "phase",
]


def compute_diff(old: FinancialState, new: FinancialState) -> dict:
    """
    Returns a dict of {section_name: new_value} for every section that
    changed between old and new. Empty dict means nothing changed.
    """
    changed: dict = {}
    for field in SECTION_FIELDS:
        old_val = getattr(old, field)
        new_val = getattr(new, field)
        if old_val != new_val:
            changed[field] = new_val
    return changed