from datetime import date
from app.state.models import FinancialState, IncomeItem, ExpenseItem, PaymentItem
from app.planning.calculator import compute_plan


def _base_state(**overrides) -> FinancialState:
    defaults = dict(session_id="test", today=date(2026, 9, 1))
    defaults.update(overrides)
    return FinancialState(**defaults)


def test_pure_surplus_has_no_shortfall():
    state = _base_state(
        starting_balance=5000,
        income=[IncomeItem(label="salary", amount=50000, day_of_month=1, confidence="confirmed")],
        essential_expenses=[ExpenseItem(label="rent", amount=15000, category="essential", day_of_month=5, confidence="confirmed")],
        optional_expenses=[ExpenseItem(label="dining out", amount=3000, category="optional", confidence="confirmed")],
    )
    plan = compute_plan(state)
    assert plan.shortfall_days == []
    assert plan.is_solvable is True
    assert plan.suggested_cuts == []
    assert plan.net_position == 50000 - 15000 - 3000


def test_shortfall_resolved_by_cutting_optional_expense():
    # Rent due day 2, salary arrives day 20 — a gap early in the month
    state = _base_state(
        starting_balance=1000,
        income=[IncomeItem(label="salary", amount=20000, day_of_month=20, confidence="confirmed")],
        essential_expenses=[ExpenseItem(label="rent", amount=15000, category="essential", day_of_month=2, confidence="confirmed")],
        optional_expenses=[ExpenseItem(label="shopping", amount=10000, category="optional", day_of_month=1, confidence="confirmed")],
    )
    plan = compute_plan(state)
    assert len(plan.shortfall_days) > 0          # baseline has a gap
    assert plan.is_solvable is True               # but cutting shopping fixes it
    assert len(plan.suggested_cuts) == 1
    assert plan.suggested_cuts[0].label == "shopping"
    assert all(d.balance >= 0 for d in plan.adjusted_balance_curve)


def test_unsolvable_when_no_optional_expenses_to_cut():
    state = _base_state(
        starting_balance=0,
        income=[IncomeItem(label="salary", amount=5000, day_of_month=25, confidence="confirmed")],
        essential_expenses=[ExpenseItem(label="rent", amount=15000, category="essential", day_of_month=2, confidence="confirmed")],
        optional_expenses=[],
    )
    plan = compute_plan(state)
    assert len(plan.shortfall_days) > 0
    assert plan.is_solvable is False
    assert plan.suggested_cuts == []


def test_undated_income_placed_on_last_day_of_window():
    state = _base_state(
        starting_balance=0,
        income=[IncomeItem(label="freelance", amount=10000, day_of_month=None, confidence="uncertain")],
    )
    plan = compute_plan(state)
    last_day_balance = plan.balance_curve[-1]
    assert last_day_balance.balance == 10000
    # every earlier day should NOT yet reflect the income
    assert plan.balance_curve[0].balance == 0


def test_undated_expense_is_front_loaded_to_day_zero():
    state = _base_state(
        starting_balance=5000,
        essential_expenses=[ExpenseItem(label="groceries", amount=2000, category="essential", day_of_month=None, confidence="estimated")],
    )
    plan = compute_plan(state)
    assert plan.balance_curve[0].balance == 3000
    assert plan.balance_curve[-1].balance == 3000  # unchanged rest of month


def test_missing_amounts_generate_assumptions_not_silent_zeros():
    state = _base_state(
        starting_balance=None,
        income=[IncomeItem(label="salary", amount=None, day_of_month=1, confidence="uncertain")],
    )
    plan = compute_plan(state)
    descriptions = [a.description for a in plan.assumptions]
    assert any("starting balance" in d.lower() for d in descriptions)
    assert any("salary" in d for d in descriptions)


def test_debt_payment_is_never_a_cut_candidate():
    state = _base_state(
        starting_balance=0,
        income=[IncomeItem(label="salary", amount=1000, day_of_month=20, confidence="confirmed")],
        payments=[PaymentItem(label="car loan", type="loan_emi", amount=15000, due_day=2, confidence="confirmed")],
        # is_essential defaults True — should never appear in suggested_cuts
    )
    plan = compute_plan(state)
    assert plan.is_solvable is False   # nothing optional exists to cut
    assert all(c.label != "car loan" for c in plan.suggested_cuts)