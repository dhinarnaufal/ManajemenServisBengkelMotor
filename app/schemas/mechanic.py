from pydantic import BaseModel, ConfigDict, Field


class MechanicCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=80, examples=["Budi"])
    specialty: str = Field(min_length=3, max_length=40, examples=["Mesin"])


class MechanicRead(BaseModel):
    id: int
    name: str
    specialty: str
    active_services: int
    max_active_services: int
    available: bool
