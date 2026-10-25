from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=80, examples=["Andi Saputra"])
    phone: str = Field(pattern=r"^\+?[0-9]{8,15}$", examples=["081234567890"])


class CustomerRead(BaseModel):
    id: int
    name: str
    phone: str
