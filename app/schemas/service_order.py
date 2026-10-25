from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ServiceStatus


class ServiceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    vehicle_id: int = Field(ge=1)
    mechanic_id: int = Field(ge=1)
    complaint: str = Field(min_length=5, max_length=300, examples=["Mesin brebet saat digas"])
    labor_cost: int = Field(ge=0, description="Biaya jasa (Rupiah).", examples=[75000])


class ServicePartAdd(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sparepart_id: int = Field(ge=1)
    quantity: int = Field(ge=1, le=100)


class ServiceStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ServiceStatus


class ServicePartRead(BaseModel):
    sparepart_id: int
    name: str
    quantity: int
    unit_price: int
    subtotal: int


class ServiceRead(BaseModel):
    id: int
    vehicle_id: int
    mechanic_id: int
    complaint: str
    status: ServiceStatus
    labor_cost: int
    parts: List[ServicePartRead]
    parts_total: int
    total_cost: int
