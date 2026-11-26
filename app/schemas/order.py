from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.entities import OrderStatus


class OrderCreate(BaseModel):
    code: str = Field(pattern=r"^\d{3,}$", examples=["2001"])
    customer_email: EmailStr
    total: float = Field(gt=0, examples=[150000])


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    store_id: str
    code: str
    customer_email: str
    total: float
    status: OrderStatus
    created_at: datetime
