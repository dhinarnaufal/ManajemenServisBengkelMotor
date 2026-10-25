from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.enums import ServiceStatus
from app.dependencies.auth import verify_api_key
from app.repositories import memory
from app.schemas.service_order import (
    ServiceCreate,
    ServicePartAdd,
    ServiceRead,
    ServiceStatusUpdate,
)
from app.services import orders as order_service

router = APIRouter(
    prefix="/services",
    tags=["Servis"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate):
    return order_service.create_order(payload.model_dump())


@router.get("", response_model=List[ServiceRead])
def list_services(
    status: Optional[ServiceStatus] = Query(default=None),
    mechanic_id: Optional[int] = Query(default=None, ge=1),
):
    return order_service.list_orders(status=status, mechanic_id=mechanic_id)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int):
    order = order_service.get_or_404(memory.orders, service_id, "Servis")
    return order_service.to_read(order)


@router.post("/{service_id}/parts", response_model=ServiceRead)
def add_service_part(service_id: int, payload: ServicePartAdd):
    return order_service.add_part(service_id, payload.sparepart_id, payload.quantity)


@router.patch("/{service_id}/status", response_model=ServiceRead)
def update_service_status(service_id: int, payload: ServiceStatusUpdate):
    return order_service.change_status(service_id, payload.status)
