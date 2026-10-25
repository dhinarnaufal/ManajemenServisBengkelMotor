from typing import Any, Dict, Iterable

from app.core.errors import MechanicAtCapacityError
from app.services.workflow import is_active


def count_active(mechanic_id: int, orders: Iterable[Dict[str, Any]]) -> int:
    return sum(
        1
        for order in orders
        if order["mechanic_id"] == mechanic_id and is_active(order["status"])
    )


def ensure_capacity(
    mechanic_id: int, orders: Iterable[Dict[str, Any]], limit: int
) -> None:
    active = count_active(mechanic_id, orders)
    if active >= limit:
        raise MechanicAtCapacityError(
            "Mekanik sudah memegang {} servis aktif (batas {}).".format(active, limit)
        )
