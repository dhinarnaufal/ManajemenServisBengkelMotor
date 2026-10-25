from typing import List

from fastapi import APIRouter, Depends, status

from app.core.errors import ConflictError
from app.dependencies.auth import verify_api_key
from app.repositories import memory
from app.schemas.sparepart import SparepartCreate, SparepartRead, StockAdd
from app.services import inventory
from app.services.orders import get_or_404

router = APIRouter(
    prefix="/spareparts",
    tags=["Sparepart"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=SparepartRead, status_code=status.HTTP_201_CREATED)
def create_sparepart(payload: SparepartCreate):
    name_key = payload.name.casefold()
    if any(s["name"].casefold() == name_key for s in memory.spareparts.values()):
        raise ConflictError("Sparepart dengan nama yang sama sudah terdaftar.")

    sparepart = {"id": memory.next_id("sparepart"), **payload.model_dump()}
    memory.spareparts[sparepart["id"]] = sparepart
    return sparepart


@router.get("", response_model=List[SparepartRead])
def list_spareparts():
    return list(memory.spareparts.values())


@router.get("/{sparepart_id}", response_model=SparepartRead)
def get_sparepart(sparepart_id: int):
    return get_or_404(memory.spareparts, sparepart_id, "Sparepart")


@router.post("/{sparepart_id}/restock", response_model=SparepartRead)
def restock_sparepart(sparepart_id: int, payload: StockAdd):
    sparepart = get_or_404(memory.spareparts, sparepart_id, "Sparepart")
    inventory.add_stock(sparepart, payload.quantity)
    return sparepart
