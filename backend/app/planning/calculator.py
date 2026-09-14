from __future__ import annotations
import calendar
from dataclasses import dataclass
from datetime import date, timedelta

from app.state.models import FinancialState
from app.planning.models import Plan, DayBalance, SuggestedCut, Assumption, ActionStep

WINDOW_DAYS = 30


@dataclass
class _Event:
    day_index: int
    amount: float          # signed: positive = income, negative = spend
    kind: str              # "income" | "essential" | "optional"  (drives cut eligibility)
    ref_id: str
    label: str
    entity_kind: str = ""  # "income" | "essential_expense" | "debt_payment" | "optional_expense" (drives display)


def _next_occurrence_index(today: date, day_of_month: int, window_days: int) -> int | None:
    year, month = today.year, today.month
    days_in_month = calendar.monthrange(year, month)[1]
    day = min(day_of_month, days_in_month)
    candidate = date(year, month, day)

    if candidate < today:
        month += 1
        if month > 12:
            month = 1
            year += 1
        days_in_month = calendar.monthrange(year, month)[1]
        day = min(day_of_month, days_in_month)
        candidate = date(year, month, day)

    delta = (candidate - today).days
    return delta if 0 <= delta < window_days else None


def _build_events(state: FinancialState, window_days: int) -> list[_Event]:
    events: list[_Event] = []

    for inc in state.income:
        amount = inc.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, inc.day_of_month, window_days)
            if inc.day_of_month is not None else window_days - 1
        )
        if day_idx is None:
            continue
        events.append(_Event(day_idx, amount, "income", inc.id, inc.label, entity_kind="income"))

    for exp in state.essential_expenses:
        amount = exp.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, exp.day_of_month, window_days)
            if exp.day_of_month is not None else 0
        )
        if day_idx is None:
            continue
        events.append(_Event(day_idx, -amount, "essential", exp.id, exp.label, entity_kind="essential_expense"))

    for exp in state.optional_expenses:
        amount = exp.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, exp.day_of_month, window_days)
            if exp.day_of_month is not None else 0
        )
        if day_idx is None:
            continue
        events.append(_Event(day_idx, -amount, "optional", exp.id, exp.label, entity_kind="optional_expense"))

    for pay in state.payments:
        amount = pay.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, pay.due_day, window_days)
            if pay.due_day is not None else 0
        )
        if day_idx is None:
            continue
        kind = "essential" if pay.is_essential else "optional"
        events.append(_Event(day_idx, -amount, kind, pay.id, pay.label, entity_kind="debt_payment"))

    return events


def _simulate(events, starting_balance, window_days, today, cut_amounts) -> list[DayBalance]:
    per_day: dict[int, list[_Event]] = {i: [] for i in range(window_days)}
    for e in events:
        per_day[e.day_index].append(e)

    curve: list[DayBalance] = []
    balance = starting_balance
    for i in range(window_days):
        day_date = today + timedelta(days=i)
        day_log: list[str] = []
        for e in per_day[i]:
            amount = e.amount
            if e.kind == "optional" and e.ref_id in cut_amounts:
                amount = amount + cut_amounts[e.ref_id]
            balance += amount
            sign = "+" if amount >= 0 else ""
            day_log.append(f"{e.label}: {sign}{amount:.2f}")
        curve.append(DayBalance(date=day_date, balance=round(balance, 2), events=day_log))
    return curve


def _cuttable_items(events: list[_Event]) -> list[_Event]:
    return [e for e in events if e.kind == "optional"]


def _collect_assumptions(state: FinancialState) -> list[Assumption]:
    assumptions: list[Assumption] = []
    if state.starting_balance is None:
        assumptions.append(Assumption(description="No starting balance (money in hand today) was given — assumed ₹0."))
    for inc in state.income:
        if inc.amount is None:
            assumptions.append(Assumption(description=f"No amount given for income '{inc.label}' — assumed ₹0."))
        if inc.day_of_month is None:
            assumptions.append(Assumption(description=f"No date given for income '{inc.label}' — assumed it arrives on the last day of the 30-day window."))
    for exp in state.essential_expenses + state.optional_expenses:
        if exp.amount is None:
            assumptions.append(Assumption(description=f"No amount given for expense '{exp.label}' — assumed ₹0."))
        if exp.day_of_month is None:
            assumptions.append(Assumption(description=f"No date given for expense '{exp.label}' — assumed it is spent on day 1."))
    for pay in state.payments:
        if pay.amount is None:
            assumptions.append(Assumption(description=f"No amount given for payment '{pay.label}' — assumed ₹0."))
        if pay.due_day is None:
            assumptions.append(Assumption(description=f"No due date given for payment '{pay.label}' — assumed it is due on day 1."))
    return assumptions


def _build_action_plan(
    events: list[_Event], starting_balance: float, today: date, cut_amounts: dict[str, float],
) -> list[ActionStep]:
    """
    Walks every event in chronological order, turning the raw event
    list into a numbered sequence of plain instructions with a running
    balance — this is the actual "what to do and when" the person needs.
    """
    ordered = sorted(events, key=lambda e: e.day_index)
    balance = starting_balance
    steps: list[ActionStep] = []

    for order, e in enumerate(ordered, start=1):
        amount = e.amount
        cut = cut_amounts.get(e.ref_id, 0)
        original_amount = None
        step_kind = e.entity_kind

        if cut > 0 and e.kind == "optional":
            original_amount = abs(e.amount)
            amount = e.amount + cut  # e.amount is negative; adding a positive cut reduces its magnitude
            step_kind = "optional_cut"

        balance += amount
        display_amount = abs(amount)
        day_date = today + timedelta(days=e.day_index)

        if step_kind == "income":
            instruction = f"{e.label} arrives — +₹{display_amount:,.0f}"
        elif step_kind == "essential_expense":
            instruction = f"Pay ₹{display_amount:,.0f} for {e.label}"
        elif step_kind == "debt_payment":
            instruction = f"Pay ₹{display_amount:,.0f} toward {e.label}"
        elif step_kind == "optional_cut":
            instruction = f"Limit {e.label} to ₹{display_amount:,.0f} (down from ₹{original_amount:,.0f}) to stay on track"
        else:  # optional_expense, not cut
            instruction = f"Planned spend: ₹{display_amount:,.0f} on {e.label}"

        steps.append(ActionStep(
            day=day_date, order=order, kind=step_kind, label=e.label,
            amount=round(display_amount, 2),
            original_amount=round(original_amount, 2) if original_amount is not None else None,
            running_balance_after=round(balance, 2),
            instruction=instruction,
        ))
    return steps


def compute_plan(state: FinancialState, window_days: int = WINDOW_DAYS) -> Plan:
    events = _build_events(state, window_days)
    starting_balance = state.starting_balance or 0

    baseline_curve = _simulate(events, starting_balance, window_days, state.today, cut_amounts={})
    shortfall_days = [d.date for d in baseline_curve if d.balance < 0]

    total_income = sum((i.amount or 0) for i in state.income)
    total_essential = (
        sum((e.amount or 0) for e in state.essential_expenses)
        + sum((p.amount or 0) for p in state.payments if p.is_essential)
    )
    total_optional = (
        sum((e.amount or 0) for e in state.optional_expenses)
        + sum((p.amount or 0) for p in state.payments if not p.is_essential)
    )
    net_position = total_income - total_essential - total_optional
    monthly_headroom = total_income - total_essential
    assumptions = _collect_assumptions(state)

    if not shortfall_days:
        action_plan = _build_action_plan(events, starting_balance, state.today, cut_amounts={})
        return Plan(
            total_income=total_income, total_essential=total_essential,
            total_optional=total_optional, net_position=net_position,
            monthly_headroom=monthly_headroom,
            balance_curve=baseline_curve, shortfall_days=[], is_solvable=True,
            suggested_cuts=[], adjusted_balance_curve=None,
            action_plan=action_plan, assumptions=assumptions,
        )

    cuttable = _cuttable_items(events)
    cut_amounts: dict[str, float] = {}
    original_amount_by_id = {e.ref_id: abs(e.amount) for e in cuttable}

    for _ in range(len(cuttable) + 1):
        curve = _simulate(events, starting_balance, window_days, state.today, cut_amounts)
        neg = [(i, d) for i, d in enumerate(curve) if d.balance < 0]
        if not neg:
            break
        earliest_idx, earliest_day = neg[0]
        candidates = [
            e for e in cuttable
            if e.day_index <= earliest_idx and cut_amounts.get(e.ref_id, 0) < original_amount_by_id[e.ref_id]
        ]
        if not candidates:
            break
        candidates.sort(key=lambda e: original_amount_by_id[e.ref_id] - cut_amounts.get(e.ref_id, 0), reverse=True)
        pick = candidates[0]
        remaining_capacity = original_amount_by_id[pick.ref_id] - cut_amounts.get(pick.ref_id, 0)
        deficit = abs(earliest_day.balance)
        cut_now = min(remaining_capacity, deficit)
        cut_amounts[pick.ref_id] = cut_amounts.get(pick.ref_id, 0) + cut_now

    final_curve = _simulate(events, starting_balance, window_days, state.today, cut_amounts)
    is_solvable = all(d.balance >= 0 for d in final_curve)

    suggested_cuts = [
        SuggestedCut(
            expense_id=ref_id, label=next(e.label for e in cuttable if e.ref_id == ref_id),
            original_amount=original_amount_by_id[ref_id], cut_amount=round(amount, 2),
        )
        for ref_id, amount in cut_amounts.items() if amount > 0
    ]

    action_plan = _build_action_plan(events, starting_balance, state.today, cut_amounts)

    return Plan(
        total_income=total_income, total_essential=total_essential,
        total_optional=total_optional, net_position=net_position,
        monthly_headroom=monthly_headroom,
        balance_curve=baseline_curve, shortfall_days=shortfall_days,
        is_solvable=is_solvable, suggested_cuts=suggested_cuts,
        adjusted_balance_curve=final_curve, action_plan=action_plan,
        assumptions=assumptions,
    )