from typing import List

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import verify_api_key
from app.repositories import memory
from app.schemas.customer import CustomerCreate, CustomerRead
from app.services.orders import get_or_404

router = APIRouter(
    prefix="/customers",
    tags=["Pelanggan"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate):
    customer = {"id": memory.next_id("customer"), **payload.model_dump()}
    memory.customers[customer["id"]] = customer
    return customer


@router.get("", response_model=List[CustomerRead])
def list_customers():
    return list(memory.customers.values())


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int):
    return get_or_404(memory.customers, customer_id, "Pelanggan")
