from app.services.billing import parts_total, total_cost


def test_parts_total_empty_is_zero():
    assert parts_total([]) == 0


def test_parts_total_sums_price_times_quantity():
    parts = [
        {"unit_price": 50000, "quantity": 2},
        {"unit_price": 15000, "quantity": 3},
    ]
    assert parts_total(parts) == 145000


def test_total_cost_is_labor_plus_parts():
    parts = [{"unit_price": 50000, "quantity": 2}]
    assert total_cost(100000, parts) == 200000


def test_total_cost_without_parts_equals_labor():
    assert total_cost(75000, []) == 75000
