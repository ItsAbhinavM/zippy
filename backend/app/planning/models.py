from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class DayBalance(BaseModel):
    date: date
    balance: float
    events: list[str] = []   # human-readable log of what happened that day


class SuggestedCut(BaseModel):
    expense_id: str
    label: str
    original_amount: float
    cut_amount: float        # may be a partial cut, not always the full amount


class Assumption(BaseModel):
    description: str


class Plan(BaseModel):
    total_income: float
    total_essential: float
    total_optional: float
    net_position: float

    balance_curve: list[DayBalance]       # before any suggested cuts
    shortfall_days: list[date]

    is_solvable: bool                     # true if cuts (or no cuts needed) clear all shortfalls
    suggested_cuts: list[SuggestedCut]
    adjusted_balance_curve: list[DayBalance] | None = None  # present only if cuts were computed

    assumptions: list[Assumption] = []