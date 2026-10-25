from typing import Any, Dict, Iterable


def parts_total(parts: Iterable[Dict[str, Any]]) -> int:
    """Total harga semua sparepart pada satu servis."""
    return sum(part["unit_price"] * part["quantity"] for part in parts)


def total_cost(labor_cost: int, parts: Iterable[Dict[str, Any]]) -> int:
    """Total biaya = jasa + sparepart."""
    return labor_cost + parts_total(parts)
