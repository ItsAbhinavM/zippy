from __future__ import annotations
from typing import Callable
from pydantic import BaseModel
from app.state.models import (
    FinancialState, IncomeItem, PaymentItem, ExpenseItem,
    Conflict, MissingField, Confidence,
)
from app.state.diff import compute_diff

CONFLICT_THRESHOLD = 0.10

Listener = Callable[[dict], None]

def _make_json_safe(value):
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_make_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k, v in value.items()}
    return value


class StateStore:
    def __init__(self, session_id: str):
        self.state = FinancialState(session_id=session_id)
        self.plan = None
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def _emit(self, envelope: dict) -> None:
        for listener in self._listeners:
            listener(envelope)

    def _notify(self, old_state: FinancialState) -> None:
        diff = compute_diff(old_state, self.state)
        if not diff:
            return
        self._emit({"type": "diff", "data": _make_json_safe(diff)})

    def _snapshot(self) -> FinancialState:
        return self.state.model_copy(deep=True)

    # ---- income ----
    def add_income(self, label, amount, day_of_month, confidence: Confidence = "estimated") -> IncomeItem:
        before = self._snapshot()
        item = IncomeItem(label=label, amount=amount, day_of_month=day_of_month, confidence=confidence)
        self.state.income.append(item)
        self._notify(before)
        return item

    def update_income_amount(self, item_id, amount, confidence: Confidence) -> None:
        before = self._snapshot()
        item = self._find(self.state.income, item_id)
        self._apply_amount_update(item, amount, confidence, entity_type="income")
        self._notify(before)

    # ---- payments ----
    def add_payment(self, label, type, amount, due_day, confidence: Confidence = "estimated", is_essential: bool = True) -> PaymentItem:
        before = self._snapshot()
        item = PaymentItem(label=label, type=type, amount=amount, due_day=due_day, confidence=confidence, is_essential=is_essential)
        self.state.payments.append(item)
        self._notify(before)
        return item

    def update_payment_amount(self, item_id, amount, confidence: Confidence) -> None:
        before = self._snapshot()
        item = self._find(self.state.payments, item_id)
        self._apply_amount_update(item, amount, confidence, entity_type="payment")
        self._notify(before)

    # ---- expenses ----
    def add_expense(self, label, amount, category, day_of_month=None, confidence: Confidence = "estimated") -> ExpenseItem:
        before = self._snapshot()
        item = ExpenseItem(label=label, amount=amount, category=category, day_of_month=day_of_month, confidence=confidence)
        target = self.state.essential_expenses if category == "essential" else self.state.optional_expenses
        target.append(item)
        self._notify(before)
        return item

    def update_expense_amount(self, item_id, amount, confidence: Confidence) -> None:
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
        self.state.missing_fields = [m for m in self.state.missing_fields if m.id != missing_id]
        self._notify(before)

    # ---- conflicts ----
    def resolve_conflict(self, conflict_id: str, correct_value: float) -> None:
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

    # ---- plan ----
    def compute_and_store_plan(self):
        from app.planning.calculator import compute_plan
        plan = compute_plan(self.state)
        self.plan = plan
        self._emit({"type": "diff", "data": {"plan": plan.model_dump(mode="json")}})
        return plan

    # ---- live conversation captions (NEW) ----
    def push_transcript(self, role: str, text: str) -> None:
        """
        Ephemeral — not stored in FinancialState, just broadcast for the
        frontend's live caption. role is "user" or "assistant".
        """
        if not text:
            return
        self._emit({"type": "transcript", "data": {"role": role, "text": text}})

    # ---- internals ----
    def _apply_amount_update(self, item, amount, confidence, entity_type) -> None:
        if item.amount is not None and item.confidence == "confirmed":
            relative_diff = abs(amount - item.amount) / max(abs(item.amount), 1e-9)
            if relative_diff > CONFLICT_THRESHOLD:
                self.state.conflicts.append(Conflict(
                    field_ref=item.id, entity_type=entity_type,
                    values_seen=[item.amount, amount],
                ))
                item.amount = amount
                item.confidence = "uncertain"
                if self.state.phase in ("planning", "reviewing"):
                    self.compute_and_store_plan()
                return
        item.amount = amount
        item.confidence = confidence
        if self.state.phase in ("planning", "reviewing"):
            self.compute_and_store_plan()

    @staticmethod
    def _find(items: list, item_id: str, required: bool = True):
        for i in items:
            if i.id == item_id:
                return i
        if required:
            raise KeyError(f"item {item_id} not found")
        return None