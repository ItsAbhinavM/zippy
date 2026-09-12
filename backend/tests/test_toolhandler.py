import asyncio
from app.state.store import StateStore
from app.agent.tool_handlers import register_all_tools

class FakeParams:
    def __init__(self, arguments: dict):
        self.arguments = arguments
        self.result = None

    async def result_callback(self, result: dict):
        self.result = result


class FakeLLM:
    """Captures registered handlers so tests can call them directly."""
    def __init__(self):
        self.handlers = {}

    def register_function(self, name, handler):
        self.handlers[name] = handler


def _setup():
    store = StateStore(session_id="s1")
    llm = FakeLLM()
    register_all_tools(llm, store)
    return store, llm


def test_add_income_via_tool_handler():
    store, llm = _setup()
    params = FakeParams({"label": "salary", "amount": 50000, "day_of_month": 1, "confidence": "confirmed"})
    asyncio.run(llm.handlers["add_income"](params))

    assert params.result["status"] == "recorded"
    assert store.state.income[0].label == "salary"


def test_update_amount_conflict_surfaces_in_callback():
    store, llm = _setup()
    asyncio.run(llm.handlers["add_payment"](FakeParams({
        "label": "HDFC card", "type": "credit_card_min", "amount": 8000, "confidence": "confirmed",
    })))

    params = FakeParams({
        "entity_type": "payment", "label": "HDFC card", "amount": 12000, "confidence": "confirmed",
    })
    asyncio.run(llm.handlers["update_amount"](params))

    assert params.result["status"] == "conflict"
    assert len(store.state.conflicts) == 1


def test_resolve_conflict_via_label():
    store, llm = _setup()
    asyncio.run(llm.handlers["add_income"](FakeParams({
        "label": "freelance", "amount": 10000, "confidence": "confirmed",
    })))
    asyncio.run(llm.handlers["update_amount"](FakeParams({
        "entity_type": "income", "label": "freelance", "amount": 15000, "confidence": "confirmed",
    })))
    assert len(store.state.conflicts) == 1

    params = FakeParams({"entity_type": "income", "label": "freelance", "correct_amount": 15000})
    asyncio.run(llm.handlers["resolve_conflict"](params))

    assert params.result["status"] == "resolved"
    assert store.state.conflicts[0].resolved is True
    assert store.state.income[0].confidence == "confirmed"


def test_mark_ready_for_planning_computes_plan():
    store, llm = _setup()
    asyncio.run(llm.handlers["set_starting_balance"](FakeParams({"amount": 1000})))
    asyncio.run(llm.handlers["add_income"](FakeParams({
        "label": "salary", "amount": 20000, "day_of_month": 1, "confidence": "confirmed",
    })))

    params = FakeParams({})
    asyncio.run(llm.handlers["mark_ready_for_planning"](params))

    assert params.result["status"] == "planned"
    assert store.plan is not None
    assert store.state.phase == "planning"


def test_flag_missing_is_recorded():
    store, llm = _setup()
    params = FakeParams({"description": "car loan amount", "why_it_matters": "affects shortfall calc"})
    asyncio.run(llm.handlers["flag_missing"](params))

    assert params.result["status"] == "flagged"
    assert len(store.state.missing_fields) == 1