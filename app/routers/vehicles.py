from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.errors import ConflictError
from app.dependencies.auth import verify_api_key
from app.repositories import memory
from app.schemas.vehicle import VehicleCreate, VehicleRead
from app.services.orders import get_or_404

router = APIRouter(
    prefix="/vehicles",
    tags=["Kendaraan"],
    dependencies=[Depends(verify_api_key)],
)


def _plate_key(plate: str) -> str:
    return plate.replace(" ", "")


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate):
    get_or_404(memory.customers, payload.customer_id, "Pelanggan")
    new_key = _plate_key(payload.plate_number)
    if any(_plate_key(v["plate_number"]) == new_key for v in memory.vehicles.values()):
        raise ConflictError("Plat nomor sudah terdaftar.")

    vehicle = {"id": memory.next_id("vehicle"), **payload.model_dump()}
    memory.vehicles[vehicle["id"]] = vehicle
    return vehicle


@router.get("", response_model=List[VehicleRead])
def list_vehicles(customer_id: Optional[int] = Query(default=None, ge=1)):
    items = list(memory.vehicles.values())
    if customer_id is not None:
        items = [v for v in items if v["customer_id"] == customer_id]
    return items


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int):
    return get_or_404(memory.vehicles, vehicle_id, "Kendaraan")
