from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StoreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["Mi Tienda"])
    domain: str = Field(min_length=3, max_length=200, examples=["mitienda.com"])


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    domain: str
    created_at: datetime
