from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class DayBalance(BaseModel):
    date: date
    balance: float
    events: list[str] = []


class SuggestedCut(BaseModel):
    expense_id: str
    label: str
    original_amount: float
    cut_amount: float


class Assumption(BaseModel):
    description: str


class ActionStep(BaseModel):
    """
    One concrete, dated instruction in the 30-day sequence — this is
    what actually answers "what do I do and when," rather than just
    reporting an end-of-month balance.
    """
    day: date
    order: int
    kind: str  # "income" | "essential_payment" | "debt_payment" | "optional_expense" | "optional_cut"
    label: str
    amount: float
    original_amount: float | None = None   # set only for optional_cut steps
    running_balance_after: float
    instruction: str                        # plain-English, ready to be spoken


class Plan(BaseModel):
    total_income: float
    total_essential: float
    total_optional: float
    net_position: float
    monthly_headroom: float   # income minus essentials/debts, before discretionary spend

    balance_curve: list[DayBalance]
    shortfall_days: list[date]

    is_solvable: bool
    suggested_cuts: list[SuggestedCut]
    adjusted_balance_curve: list[DayBalance] | None = None

    action_plan: list[ActionStep] = []   # the sequential "what to do" list

    assumptions: list[Assumption] = []