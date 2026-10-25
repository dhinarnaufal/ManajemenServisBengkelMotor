from typing import Any, Dict

from app.core.errors import InsufficientStockError


def take_stock(sparepart: Dict[str, Any], quantity: int) -> None:
    """Kurangi stok. Jika stok kurang, stok tidak berubah dan error dilempar."""
    if quantity < 1:
        raise ValueError("Jumlah harus minimal 1.")
    if sparepart["stock"] < quantity:
        raise InsufficientStockError(
            "Stok '{}' tidak cukup: tersedia {}, diminta {}.".format(
                sparepart["name"], sparepart["stock"], quantity
            )
        )
    sparepart["stock"] -= quantity


def add_stock(sparepart: Dict[str, Any], quantity: int) -> None:
    if quantity < 1:
        raise ValueError("Jumlah harus minimal 1.")
    sparepart["stock"] += quantity
