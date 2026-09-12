from __future__ import annotations
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field
import uuid

Confidence = Literal["confirmed", "estimated", "uncertain"]
Phase = Literal["gathering", "clarifying", "planning", "reviewing"]


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


class IncomeItem(BaseModel):
    id: str = Field(default_factory=_new_id)
    label: str
    amount: float | None = None
    day_of_month: int | None = None   # 1-31, None if unknown/irregular
    confidence: Confidence = "estimated"


class PaymentItem(BaseModel):
    """Loans and credit-card payments."""
    id: str = Field(default_factory=_new_id)
    label: str
    type: Literal["loan_emi", "credit_card_min", "credit_card_full"]
    amount: float | None = None
    due_day: int | None = None
    is_essential: bool = True   # debt payments default essential: penalties/credit score
    confidence: Confidence = "estimated"


class ExpenseItem(BaseModel):
    id: str = Field(default_factory=_new_id)
    label: str
    amount: float | None = None
    category: Literal["essential", "optional"]
    day_of_month: int | None = None   # None = assume spread/front-loaded across month
    confidence: Confidence = "estimated"


class Conflict(BaseModel):
    id: str = Field(default_factory=_new_id)
    field_ref: str            # id of the item this conflict is about
    entity_type: Literal["income", "payment", "expense"]
    values_seen: list[float] = []
    resolved: bool = False


class MissingField(BaseModel):
    id: str = Field(default_factory=_new_id)
    description: str          # e.g. "amount for HDFC credit card"
    why_it_matters: str


class FinancialState(BaseModel):
    session_id: str
    today: date = Field(default_factory=date.today)

    income: list[IncomeItem] = []
    essential_expenses: list[ExpenseItem] = []
    optional_expenses: list[ExpenseItem] = []
    payments: list[PaymentItem] = []

    conflicts: list[Conflict] = []
    missing_fields: list[MissingField] = []

    starting_balance: float | None = None
    phase: Phase = "gathering"