import pytest

from app.core.enums import ServiceStatus as S
from app.core.errors import MechanicAtCapacityError
from app.services.mechanic_load import count_active, ensure_capacity


def order(mechanic_id, status):
    return {"mechanic_id": mechanic_id, "status": status}


def test_count_active_counts_only_antri_and_dikerjakan():
    orders = [
        order(1, S.ANTRI),
        order(1, S.DIKERJAKAN),
        order(1, S.SELESAI),
        order(1, S.DIBAYAR),
    ]
    assert count_active(1, orders) == 2


def test_count_active_ignores_other_mechanics():
    orders = [order(1, S.ANTRI), order(2, S.ANTRI), order(2, S.DIKERJAKAN)]
    assert count_active(1, orders) == 1
    assert count_active(2, orders) == 2


def test_ensure_capacity_passes_below_limit():
    ensure_capacity(1, [order(1, S.ANTRI)], limit=2)


def test_ensure_capacity_raises_at_limit():
    orders = [order(1, S.ANTRI), order(1, S.DIKERJAKAN)]
    with pytest.raises(MechanicAtCapacityError):
        ensure_capacity(1, orders, limit=2)


def test_finished_services_free_capacity():
    orders = [order(1, S.SELESAI), order(1, S.DIBAYAR)]
    ensure_capacity(1, orders, limit=1)
