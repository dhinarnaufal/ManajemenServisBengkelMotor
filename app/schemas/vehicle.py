import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

PLATE_PATTERN = re.compile(r"^[A-Z]{1,2} ?[0-9]{1,4} ?[A-Z]{0,3}$")


class VehicleCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    customer_id: int = Field(ge=1)
    plate_number: str = Field(min_length=3, max_length=20, examples=["DD 1234 AB"])
    brand: str = Field(min_length=2, max_length=40, examples=["Honda"])
    model: str = Field(min_length=1, max_length=40, examples=["Beat"])
    year: int = Field(ge=1980, le=2100)

    @field_validator("plate_number")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        value = " ".join(value.upper().split())
        if not PLATE_PATTERN.match(value):
            raise ValueError("Format plat nomor tidak valid, contoh: DD 1234 AB.")
        return value


class VehicleRead(BaseModel):
    id: int
    customer_id: int
    plate_number: str
    brand: str
    model: str
    year: int
