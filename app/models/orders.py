from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.order_items import OrderItem, OrderItemCreate, OrderItemPublicV1

class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    ready_for_delivery = "ready_for_delivery"
    delivered = "delivered"
    canceled = "canceled"

class OrderCreate(SQLModel):
    branch_id: int
    items: list["OrderItemCreate"]
    dropoff_lon: Decimal = Field(max_digits=9, decimal_places=6)
    dropoff_lat: Decimal = Field(max_digits=9, decimal_places=6)

class OrderPublic(SQLModel):
    id: int
    customer_id: int
    branch_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime | None

class OrderPublicForCustomer(SQLModel):
    # remove customer_id
    id: int
    branch_id: int
    branch_name: str # enrich
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime | None

    order_items: list["OrderItemPublicV1"]

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: int = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="users.id")
    branch_id: int = Field(foreign_key="branches.id")
    status: OrderStatus = OrderStatus.pending
    total_amount: Decimal = Field(default=0, max_digits=12, decimal_places=3, ge=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None

    order_items: list["OrderItem"] = Relationship(back_populates="order")