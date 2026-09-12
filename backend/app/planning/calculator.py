from __future__ import annotations
import calendar
from dataclasses import dataclass
from datetime import date, timedelta

from app.state.models import FinancialState
from app.planning.models import Plan, DayBalance, SuggestedCut, Assumption

WINDOW_DAYS = 30

@dataclass
class _Event:
    day_index: int          # 0..WINDOW_DAYS-1
    amount: float            # signed: positive = income, negative = spend
    kind: str                 # "income" | "essential" | "optional"
    ref_id: str
    label: str


def _next_occurrence_index(today: date, day_of_month: int, window_days: int) -> int | None:
    """
    Finds the next calendar date matching day_of_month (clamped to the
    length of whichever month it falls in) and returns its offset in
    days from `today`. Returns None if that date falls outside the
    window (rare, but possible near month boundaries).
    """
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
            if inc.day_of_month is not None
            else window_days - 1   # conservative: assume it lands last
        )
        if day_idx is None:
            continue
        events.append(_Event(day_idx, amount, "income", inc.id, inc.label))

    for exp in state.essential_expenses:
        amount = exp.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, exp.day_of_month, window_days)
            if exp.day_of_month is not None
            else 0   # conservative: assume it's spent immediately
        )
        if day_idx is None:
            continue
        events.append(_Event(day_idx, -amount, "essential", exp.id, exp.label))

    for exp in state.optional_expenses:
        amount = exp.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, exp.day_of_month, window_days)
            if exp.day_of_month is not None
            else 0
        )
        if day_idx is None:
            continue
        events.append(_Event(day_idx, -amount, "optional", exp.id, exp.label))

    for pay in state.payments:
        amount = pay.amount or 0
        day_idx = (
            _next_occurrence_index(state.today, pay.due_day, window_days)
            if pay.due_day is not None
            else 0
        )
        if day_idx is None:
            continue
        kind = "essential" if pay.is_essential else "optional"
        events.append(_Event(day_idx, -amount, kind, pay.id, pay.label))

    return events


def _simulate(
    events: list[_Event],
    starting_balance: float,
    window_days: int,
    today: date,
    cut_amounts: dict[str, float],
) -> list[DayBalance]:
    """
    Runs the running balance across the window. `cut_amounts` reduces
    the magnitude of specific optional-expense/payment events (used
    when computing the adjusted, post-suggestion curve).
    """
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
                cut = cut_amounts[e.ref_id]
                # amount is negative for spends; reduce its magnitude
                amount = amount + cut
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
        assumptions.append(Assumption(
            description="No starting balance (money in hand today) was given — assumed ₹0."
        ))

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
    assumptions = _collect_assumptions(state)

    if not shortfall_days:
        return Plan(
            total_income=total_income,
            total_essential=total_essential,
            total_optional=total_optional,
            net_position=net_position,
            balance_curve=baseline_curve,
            shortfall_days=[],
            is_solvable=True,
            suggested_cuts=[],
            adjusted_balance_curve=None,
            assumptions=assumptions,
        )

    # --- greedy cut resolution ---
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
            if e.day_index <= earliest_idx
            and cut_amounts.get(e.ref_id, 0) < original_amount_by_id[e.ref_id]
        ]
        if not candidates:
            break  # nothing left we're able to cut to fix this day

        candidates.sort(
            key=lambda e: original_amount_by_id[e.ref_id] - cut_amounts.get(e.ref_id, 0),
            reverse=True,
        )
        pick = candidates[0]
        remaining_capacity = original_amount_by_id[pick.ref_id] - cut_amounts.get(pick.ref_id, 0)
        deficit = abs(earliest_day.balance)
        cut_now = min(remaining_capacity, deficit)
        cut_amounts[pick.ref_id] = cut_amounts.get(pick.ref_id, 0) + cut_now

    final_curve = _simulate(events, starting_balance, window_days, state.today, cut_amounts)
    is_solvable = all(d.balance >= 0 for d in final_curve)

    suggested_cuts = [
        SuggestedCut(
            expense_id=ref_id,
            label=next(e.label for e in cuttable if e.ref_id == ref_id),
            original_amount=original_amount_by_id[ref_id],
            cut_amount=round(amount, 2),
        )
        for ref_id, amount in cut_amounts.items()
        if amount > 0
    ]

    return Plan(
        total_income=total_income,
        total_essential=total_essential,
        total_optional=total_optional,
        net_position=net_position,
        balance_curve=baseline_curve,
        shortfall_days=shortfall_days,
        is_solvable=is_solvable,
        suggested_cuts=suggested_cuts,
        adjusted_balance_curve=final_curve,
        assumptions=assumptions,
    )