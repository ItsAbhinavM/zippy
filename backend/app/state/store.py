from __future__ import annotations
from typing import Callable
from pydantic import BaseModel
from app.state.models import (
    FinancialState, IncomeItem, PaymentItem, ExpenseItem,
    Conflict, MissingField, Confidence,
)
from app.state.diff import compute_diff
from app.planning.models import Plan

# how far apart two values must be (relative) to count as a genuine conflict rather than rounding/estimation noise
CONFLICT_THRESHOLD = 0.10

Listener = Callable[[dict], None]

def _make_json_safe(value):
    if isinstance(value,BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_make_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k,v in value.items()}

class StateStore:
    def __init__(self, session_id: str):
        self.state = FinancialState(session_id=session_id)
        self._listeners: list[Listener] = []
        self.plan: Plan | None=None

    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def _notify(self, old_state: FinancialState) -> None:
        diff = compute_diff(old_state, self.state)
        if not diff:
            return
        safe_diff = _make_json_safe(diff)
        for listener in self._listeners:
            listener(diff)

    def _snapshot(self) -> FinancialState:
        return self.state.model_copy(deep=True)

    def add_income(
        self, label: str, amount: float | None, day_of_month: int | None,
        confidence: Confidence = "estimated",
    ) -> IncomeItem:
        before = self._snapshot()
        item = IncomeItem(
            label=label, amount=amount,
            day_of_month=day_of_month, confidence=confidence,
        )
        self.state.income.append(item)
        self._notify(before)
        return item

    def update_income_amount(
        self, item_id: str, amount: float, confidence: Confidence,
    ) -> None:
        before = self._snapshot()
        item = self._find(self.state.income, item_id)
        self._apply_amount_update(item, amount, confidence, entity_type="income")
        self._notify(before)

    # ---- payments (loans / credit cards) ----
    def add_payment(
        self, label: str, type: str, amount: float | None,
        due_day: int | None, confidence: Confidence = "estimated",
        is_essential: bool = True,
    ) -> PaymentItem:
        before = self._snapshot()
        item = PaymentItem(
            label=label, type=type, amount=amount,
            due_day=due_day, confidence=confidence, is_essential=is_essential,
        )
        self.state.payments.append(item)
        self._notify(before)
        return item

    def update_payment_amount(
        self, item_id: str, amount: float, confidence: Confidence,
    ) -> None:
        before = self._snapshot()
        item = self._find(self.state.payments, item_id)
        self._apply_amount_update(item, amount, confidence, entity_type="payment")
        self._notify(before)

    # ---- expenses ----
    def add_expense(
        self, label: str, amount: float | None, category: str,
        day_of_month: int | None = None, confidence: Confidence = "estimated",
    ) -> ExpenseItem:
        before = self._snapshot()
        item = ExpenseItem(
            label=label, amount=amount, category=category,
            day_of_month=day_of_month, confidence=confidence,
        )
        target = (
            self.state.essential_expenses if category == "essential"
            else self.state.optional_expenses
        )
        target.append(item)
        self._notify(before)
        return item

    def update_expense_amount(
        self, item_id: str, amount: float, confidence: Confidence,
    ) -> None:
        before = self._snapshot()
        item = (
            self._find(self.state.essential_expenses, item_id, required=False)
            or self._find(self.state.optional_expenses, item_id)
        )
        self._apply_amount_update(item, amount, confidence, entity_type="expense")
        self._notify(before)

    # ---- starting balance ----
    def set_starting_balance(self, amount: float) -> None:
        before = self._snapshot()
        self.state.starting_balance = amount
        self._notify(before)

    # ---- missing fields ----
    def flag_missing(self, description: str, why_it_matters: str) -> MissingField:
        before = self._snapshot()
        item = MissingField(description=description, why_it_matters=why_it_matters)
        self.state.missing_fields.append(item)
        self._notify(before)
        return item

    def resolve_missing(self, missing_id: str) -> None:
        before = self._snapshot()
        self.state.missing_fields = [
            m for m in self.state.missing_fields if m.id != missing_id
        ]
        self._notify(before)

    # ---- conflicts ----
    def resolve_conflict(self, conflict_id: str, correct_value: float) -> None:
        """
        Called once the user clarifies which value is correct. Applies
        the correct value to the underlying entity and marks resolved.
        """
        before = self._snapshot()
        conflict = self._find(self.state.conflicts, conflict_id)
        conflict.resolved = True

        entity_list = {
            "income": self.state.income,
            "payment": self.state.payments,
            "expense": self.state.essential_expenses + self.state.optional_expenses,
        }[conflict.entity_type]
        entity = self._find(entity_list, conflict.field_ref)
        entity.amount = correct_value
        entity.confidence = "confirmed"
        self._notify(before)

    # ---- phase ----
    def set_phase(self, phase: str) -> None:
        before = self._snapshot()
        self.state.phase = phase
        self._notify(before)

    # ---- internals ----
    def _apply_amount_update(self, item, amount, confidence, entity_type) -> None:
        if item.amount is not None and item.confidence == "confirmed":
            relative_diff = abs(amount - item.amount) / max(abs(item.amount), 1e-9)
            if relative_diff > CONFLICT_THRESHOLD:
                self.state.conflicts.append(Conflict(
                    field_ref=item.id,
                    entity_type=entity_type,
                    values_seen=[item.amount, amount],
                ))
                # keep the most recent value but mark it uncertain until
                # the conflict is explicitly resolved
                item.amount = amount
                item.confidence = "uncertain"
                return
        item.amount = amount
        item.confidence = confidence
    
    def compute_and_store_plan(self)-> "Plan":
        from app.planning.calculator import compute_plan
        plan=compute_plan(self.state)
        self.plan=plan
        for listner in self._listeners:
            listner({"plan":plan.model_dump(mode="json")})
        return plan        

    @staticmethod
    def _find(items: list, item_id: str, required: bool = True):
        for i in items:
            if i.id == item_id:
                return i
        if required:
            raise KeyError(f"item {item_id} not found")
        return None