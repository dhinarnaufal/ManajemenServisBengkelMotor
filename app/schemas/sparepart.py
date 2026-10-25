from pydantic import BaseModel, ConfigDict, Field


class SparepartCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=80, examples=["Oli Mesin 1L"])
    price: int = Field(gt=0, description="Harga satuan (Rupiah).", examples=[55000])
    stock: int = Field(ge=0, le=100000, examples=[20])


class StockAdd(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1, le=100000)


class SparepartRead(BaseModel):
    id: int
    name: str
    price: int
    stock: int
