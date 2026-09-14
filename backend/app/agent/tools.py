# ONly tool definitions here
# TOOL_DEFINITION: list[dict]=[]
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

_CONFIDENCE_ENUM = {"type": "string", "enum": ["confirmed", "estimated", "uncertain"]}

add_income_schema = FunctionSchema(
    name="add_income",
    description="Record a new source of income the user has mentioned. Call this once per distinct income source.",
    properties={
        "label": {"type": "string", "description": "short name, e.g. 'salary', 'freelance client A'"},
        "amount": {"type": "number", "description": "amount per occurrence, in the user's currency"},
        "day_of_month": {"type": "integer", "description": "day of month it arrives (1-31). Omit entirely if the user hasn't said or doesn't know."},
        "confidence": _CONFIDENCE_ENUM,
    },
    required=["label", "amount", "confidence"],
)

add_payment_schema = FunctionSchema(
    name="add_payment",
    description="Record a loan EMI or credit-card payment the user owes.",
    properties={
        "label": {"type": "string", "description": "e.g. 'HDFC credit card', 'car loan'"},
        "type": {"type": "string", "enum": ["loan_emi", "credit_card_min", "credit_card_full"]},
        "amount": {"type": "number"},
        "due_day": {"type": "integer", "description": "day of month it's due (1-31). Omit if unknown."},
        "confidence": _CONFIDENCE_ENUM,
    },
    required=["label", "type", "amount", "confidence"],
)

add_expense_schema = FunctionSchema(
    name="add_expense",
    description="Record a household or discretionary expense. Use category 'essential' for things like rent, groceries, utilities, and 'optional' for discretionary spending like dining out or subscriptions.",
    properties={
        "label": {"type": "string"},
        "amount": {"type": "number"},
        "category": {"type": "string", "enum": ["essential", "optional"]},
        "day_of_month": {"type": "integer", "description": "Omit if it's a recurring/spread cost with no fixed date."},
        "confidence": _CONFIDENCE_ENUM,
    },
    required=["label", "amount", "category", "confidence"],
)

update_amount_schema = FunctionSchema(
    name="update_amount",
    description="Update the amount for an income, payment, or expense that was already recorded, when the user gives a new or corrected figure. Identify the item by the same label used before.",
    properties={
        "entity_type": {"type": "string", "enum": ["income", "payment", "expense"]},
        "label": {"type": "string", "description": "must match (or closely match) the label used when it was first added"},
        "amount": {"type": "number"},
        "confidence": _CONFIDENCE_ENUM,
    },
    required=["entity_type", "label", "amount", "confidence"],
)

set_starting_balance_schema = FunctionSchema(
    name="set_starting_balance",
    description="Record how much money the user currently has available right now, before any of the 30 days begin. Ask for this explicitly if not yet known — it materially affects the plan.",
    properties={"amount": {"type": "number"}},
    required=["amount"],
)

flag_missing_schema = FunctionSchema(
    name="flag_missing",
    description="Register that a piece of information is missing and still needed, without inventing a value for it.",
    properties={
        "description": {"type": "string", "description": "what's missing, e.g. 'amount for HDFC credit card'"},
        "why_it_matters": {"type": "string"},
    },
    required=["description", "why_it_matters"],
)

resolve_conflict_schema = FunctionSchema(
    name="resolve_conflict",
    description="Resolve a previously flagged conflicting value once the user clarifies which figure is correct.",
    properties={
        "entity_type": {"type": "string", "enum": ["income", "payment", "expense"]},
        "label": {"type": "string"},
        "correct_amount": {"type": "number"},
    },
    required=["entity_type", "label", "correct_amount"],
)

mark_ready_for_planning_schema = FunctionSchema(
    name="mark_ready_for_planning",
    description="Call this once income, essential expenses, and debt payments are known well enough (estimated or confirmed) to compute a 30-day plan. Minor missing details are fine — flag them with flag_missing rather than blocking on them.",
    properties={},
    required=[],
)

confirm_understood_schema = FunctionSchema(
    name="confirm_understood",
    description="Call this once the user has explicitly confirmed they understand the final plan.",
    properties={},
    required=[],
)

set_current_question_schema = FunctionSchema(
    name="set_current_question",
    description=(
        "Call this immediately, before you start speaking, whenever you are "
        "about to ask the person something new. Give a short, direct, few-word "
        "version of it — not the full sentence you'll say out loud. Call it "
        "again each time you move to a new question."
    ),
    properties={
        "question": {"type": "string", "description": "Short one-liner, e.g. 'How much do you have right now?'"},
    },
    required=["question"],
)

TOOLS_SCHEMA = ToolsSchema(standard_tools=[
    add_income_schema,
    add_payment_schema,
    add_expense_schema,
    update_amount_schema,
    set_starting_balance_schema,
    flag_missing_schema,
    resolve_conflict_schema,
    mark_ready_for_planning_schema,
    confirm_understood_schema,
    set_current_question_schema
])