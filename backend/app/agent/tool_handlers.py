from __future__ import annotations
from app.state.store import StateStore
from app.state.models import IncomeItem, PaymentItem, ExpenseItem


def _find_income_by_label(store: StateStore, label: str) -> IncomeItem | None:
    label = label.lower()
    for item in store.state.income:
        if label in item.label.lower() or item.label.lower() in label:
            return item
    return None


def _find_payment_by_label(store: StateStore, label: str) -> PaymentItem | None:
    label = label.lower()
    for item in store.state.payments:
        if label in item.label.lower() or item.label.lower() in label:
            return item
    return None


def _find_expense_by_label(store: StateStore, label: str) -> ExpenseItem | None:
    label = label.lower()
    for item in store.state.essential_expenses + store.state.optional_expenses:
        if label in item.label.lower() or item.label.lower() in label:
            return item
    return None


def register_all_tools(llm, store: StateStore) -> None:
    """Called once per session from pipeline.py to bind every handler."""

    async def add_income(params):
        args = params.arguments
        item = store.add_income(
            label=args["label"],
            amount=args.get("amount"),
            day_of_month=args.get("day_of_month"),
            confidence=args["confidence"],
        )
        await params.result_callback({"status": "recorded", "id": item.id})

    async def add_payment(params):
        args = params.arguments
        item = store.add_payment(
            label=args["label"],
            type=args["type"],
            amount=args.get("amount"),
            due_day=args.get("due_day"),
            confidence=args["confidence"],
        )
        await params.result_callback({"status": "recorded", "id": item.id})

    async def add_expense(params):
        args = params.arguments
        item = store.add_expense(
            label=args["label"],
            amount=args.get("amount"),
            category=args["category"],
            day_of_month=args.get("day_of_month"),
            confidence=args["confidence"],
        )
        await params.result_callback({"status": "recorded", "id": item.id})

    async def update_amount(params):
        args = params.arguments
        entity_type = args["entity_type"]
        finder = {
            "income": _find_income_by_label,
            "payment": _find_payment_by_label,
            "expense": _find_expense_by_label,
        }[entity_type]
        item = finder(store, args["label"])

        if item is None:
            await params.result_callback({
                "status": "not_found",
                "message": f"No existing {entity_type} matches '{args['label']}'. Add it first with add_{entity_type}.",
            })
            return

        conflicts_before = len(store.state.conflicts)
        updater = {
            "income": store.update_income_amount,
            "payment": store.update_payment_amount,
            "expense": store.update_expense_amount,
        }[entity_type]
        updater(item.id, amount=args["amount"], confidence=args["confidence"])

        if len(store.state.conflicts) > conflicts_before:
            latest = store.state.conflicts[-1]
            await params.result_callback({
                "status": "conflict",
                "message": (
                    f"That conflicts with a previously confirmed value for "
                    f"'{item.label}' ({latest.values_seen[0]} vs {latest.values_seen[1]}). "
                    "Ask the user which figure is correct."
                ),
            })
            return
        if store.state.phase in ("planning","reviewing") :
            store.compute_and_store_plan()
        await params.result_callback({"status": "updated"})

    async def set_starting_balance(params):
        args = params.arguments
        store.set_starting_balance(args["amount"])
        await params.result_callback({"status": "recorded"})

    async def flag_missing(params):
        args = params.arguments
        item = store.flag_missing(args["description"], args["why_it_matters"])
        await params.result_callback({"status": "flagged", "id": item.id})

    async def resolve_conflict(params):
        args = params.arguments
        finder = {
            "income": _find_income_by_label,
            "payment": _find_payment_by_label,
            "expense": _find_expense_by_label,
        }[args["entity_type"]]
        item = finder(store, args["label"])
        if item is None:
            await params.result_callback({"status": "not_found"})
            return

        unresolved = [
            c for c in store.state.conflicts
            if c.field_ref == item.id and not c.resolved
        ]
        if not unresolved:
            await params.result_callback({"status": "no_open_conflict"})
            return

        store.resolve_conflict(unresolved[-1].id, args["correct_amount"])
        if store.state.phase in ("planning","reviewing"):
            store.compute_and_store_plan()
        await params.result_callback({"status": "resolved"})

    async def mark_ready_for_planning(params):
        store.set_phase("planning")
        plan = store.compute_and_store_plan()
        await params.result_callback({
            "status": "planned",
            "is_solvable": plan.is_solvable,
            "net_position": plan.net_position,
            "shortfall_day_count": len(plan.shortfall_days),
        })

    async def confirm_understood(params):
        store.set_phase("reviewing")
        await params.result_callback({"status": "confirmed"})

    llm.register_function("add_income", add_income)
    llm.register_function("add_payment", add_payment)
    llm.register_function("add_expense", add_expense)
    llm.register_function("update_amount", update_amount)
    llm.register_function("set_starting_balance", set_starting_balance)
    llm.register_function("flag_missing", flag_missing)
    llm.register_function("resolve_conflict", resolve_conflict)
    llm.register_function("mark_ready_for_planning", mark_ready_for_planning)
    llm.register_function("confirm_understood", confirm_understood)