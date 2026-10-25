from typing import List

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import verify_api_key
from app.repositories import memory
from app.schemas.mechanic import MechanicCreate, MechanicRead
from app.services.orders import get_or_404, mechanic_view

router = APIRouter(
    prefix="/mechanics",
    tags=["Mekanik"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=MechanicRead, status_code=status.HTTP_201_CREATED)
def create_mechanic(payload: MechanicCreate):
    mechanic = {"id": memory.next_id("mechanic"), **payload.model_dump()}
    memory.mechanics[mechanic["id"]] = mechanic
    return mechanic_view(mechanic)


@router.get("", response_model=List[MechanicRead])
def list_mechanics():
    return [mechanic_view(m) for m in memory.mechanics.values()]


@router.get("/{mechanic_id}", response_model=MechanicRead)
def get_mechanic(mechanic_id: int):
    return mechanic_view(get_or_404(memory.mechanics, mechanic_id, "Mekanik"))
