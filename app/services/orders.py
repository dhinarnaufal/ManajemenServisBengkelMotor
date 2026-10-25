"""Orkestrasi alur servis: menggabungkan repository dengan aturan bisnis."""
from typing import Any, Dict, List, Optional

from app.core.config import get_max_active_services
from app.core.enums import ServiceStatus
from app.core.errors import ConflictError, NotFoundError
from app.repositories import memory
from app.services import billing, inventory, mechanic_load, workflow


def get_or_404(table: Dict[int, Dict[str, Any]], item_id: int, label: str) -> Dict[str, Any]:
    item = table.get(item_id)
    if item is None:
        raise NotFoundError("{} tidak ditemukan.".format(label))
    return item


def to_read(order: Dict[str, Any]) -> Dict[str, Any]:
    parts = [
        {**part, "subtotal": part["unit_price"] * part["quantity"]}
        for part in order["parts"]
    ]
    return {
        **order,
        "parts": parts,
        "parts_total": billing.parts_total(order["parts"]),
        "total_cost": billing.total_cost(order["labor_cost"], order["parts"]),
    }


def mechanic_view(mechanic: Dict[str, Any]) -> Dict[str, Any]:
    limit = get_max_active_services()
    active = mechanic_load.count_active(mechanic["id"], memory.orders.values())
    return {
        **mechanic,
        "active_services": active,
        "max_active_services": limit,
        "available": active < limit,
    }


def create_order(data: Dict[str, Any]) -> Dict[str, Any]:
    get_or_404(memory.vehicles, data["vehicle_id"], "Kendaraan")
    get_or_404(memory.mechanics, data["mechanic_id"], "Mekanik")
    mechanic_load.ensure_capacity(
        data["mechanic_id"], memory.orders.values(), get_max_active_services()
    )

    order = {
        "id": memory.next_id("order"),
        **data,
        "status": ServiceStatus.ANTRI,
        "parts": [],
    }
    memory.orders[order["id"]] = order
    return to_read(order)


def list_orders(
    status: Optional[ServiceStatus] = None, mechanic_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    items = list(memory.orders.values())
    if status is not None:
        items = [o for o in items if o["status"] == status]
    if mechanic_id is not None:
        items = [o for o in items if o["mechanic_id"] == mechanic_id]
    return [to_read(o) for o in items]


def add_part(order_id: int, sparepart_id: int, quantity: int) -> Dict[str, Any]:
    order = get_or_404(memory.orders, order_id, "Servis")
    if not workflow.can_modify_parts(order["status"]):
        raise ConflictError(
            "Sparepart hanya bisa ditambahkan saat servis berstatus antri atau dikerjakan."
        )
    sparepart = get_or_404(memory.spareparts, sparepart_id, "Sparepart")

    inventory.take_stock(sparepart, quantity)  # stok berkurang otomatis

    for line in order["parts"]:
        if line["sparepart_id"] == sparepart_id:
            line["quantity"] += quantity
            break
    else:
        order["parts"].append(
            {
                "sparepart_id": sparepart_id,
                "name": sparepart["name"],
                "quantity": quantity,
                "unit_price": sparepart["price"],  # harga dikunci saat ditambahkan
            }
        )
    return to_read(order)


def change_status(order_id: int, target: ServiceStatus) -> Dict[str, Any]:
    order = get_or_404(memory.orders, order_id, "Servis")
    workflow.ensure_valid_transition(order["status"], target)
    order["status"] = target
    return to_read(order)
