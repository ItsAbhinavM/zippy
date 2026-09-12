from app.state.store import StateStore

def test_add_income_appends_item():
    store = StateStore(session_id="s1")
    item = store.add_income("salary", 50000, day_of_month=1, confidence="confirmed")
    assert store.state.income[0].id == item.id
    assert store.state.income[0].amount == 50000


def test_confirmed_value_conflict_is_detected():
    store = StateStore(session_id="s1")
    item = store.add_payment(
        "HDFC card", type="credit_card_min", amount=8000,
        due_day=5, confidence="confirmed",
    )
    store.update_payment_amount(item.id, amount=12000, confidence="confirmed")

    assert len(store.state.conflicts) == 1
    conflict = store.state.conflicts[0]
    assert conflict.values_seen == [8000, 12000]
    # most recent value is used but marked uncertain, not silently trusted
    assert store.state.payments[0].amount == 12000
    assert store.state.payments[0].confidence == "uncertain"


def test_small_variation_does_not_trigger_conflict():
    store = StateStore(session_id="s1")
    item = store.add_income("salary", 50000, day_of_month=1, confidence="confirmed")
    store.update_income_amount(item.id, amount=51000, confidence="confirmed")  # 2% diff
    assert len(store.state.conflicts) == 0


def test_resolve_conflict_marks_confirmed():
    store = StateStore(session_id="s1")
    item = store.add_income("freelance", 10000, day_of_month=None, confidence="confirmed")
    store.update_income_amount(item.id, amount=15000, confidence="confirmed")
    conflict_id = store.state.conflicts[0].id

    store.resolve_conflict(conflict_id, correct_value=15000)

    assert store.state.conflicts[0].resolved is True
    assert store.state.income[0].amount == 15000
    assert store.state.income[0].confidence == "confirmed"


def test_diff_notifies_listener_on_change():
    store = StateStore(session_id="s1")
    received = []
    store.subscribe(lambda diff: received.append(diff))

    store.add_income("salary", 50000, day_of_month=1, confidence="confirmed")

    assert len(received) == 1
    assert "income" in received[0]


def test_no_notification_when_nothing_changes():
    store = StateStore(session_id="s1")
    received = []
    store.set_phase("gathering")  # same as default — no real change
    store.subscribe(lambda diff: received.append(diff))
    store.set_phase("gathering")
    assert received == []